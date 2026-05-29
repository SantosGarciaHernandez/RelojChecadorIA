import json
import re
import shutil
from pathlib import Path

import cv2
import numpy as np
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.ml.image_preprocessing import decode_base64_image
from app.models.user_model import Usuario
from app.schemas.training_schema import TrainingRegisterRequest
from app.services.training_progress_store import training_progress_store
from app.services.user_service import UserService


IMAGE_EXTENSIONS = ("*.jpg", "*.jpeg", "*.png")


class ModelTrainingService:
    def __init__(self) -> None:
        self.settings = get_settings()

    def _progress(self, job_id: str, percent: int, step: str, message: str, extra: dict | None = None) -> None:
        training_progress_store.update(
            job_id=job_id,
            percent=percent,
            step=step,
            message=message,
            extra=extra,
        )

    @staticmethod
    def _validate_model_label(model_label: str) -> str:
        label = model_label.strip()
        if not label:
            raise ValueError("La etiqueta del modelo es obligatoria")

        # Evita path traversal y caracteres inválidos para carpetas Windows/Linux.
        if ".." in label or "/" in label or "\\" in label:
            raise ValueError("La etiqueta del modelo no puede contener rutas ni separadores")

        if re.search(r'[<>:"|?*]', label):
            raise ValueError("La etiqueta del modelo contiene caracteres inválidos para carpeta")

        return label

    @staticmethod
    def _count_images(directory: Path) -> int:
        if not directory.exists():
            return 0
        total = 0
        for pattern in IMAGE_EXTENSIONS:
            total += len(list(directory.glob(pattern)))
        return total

    def _load_existing_labels(self) -> dict[str, str]:
        path = self.settings.absolute_labels_path
        if not path.exists():
            return {}
        with path.open("r", encoding="utf-8") as file:
            labels = json.load(file)
        if not isinstance(labels, dict):
            raise ValueError("labels.json debe ser un objeto JSON")
        normalized: dict[str, str] = {}
        for index, raw_label in labels.items():
            if isinstance(raw_label, str):
                normalized[str(index)] = raw_label
            elif isinstance(raw_label, dict):
                normalized[str(index)] = (
                    raw_label.get("model_label")
                    or raw_label.get("nombre_etiqueta_modelo")
                    or raw_label.get("name")
                    or raw_label.get("nombre")
                    or f"Clase_{index}"
                )
            else:
                normalized[str(index)] = f"Clase_{index}"
        return normalized

    def _validate_existing_dataset(self, new_label: str) -> None:
        train_dir = self.settings.absolute_training_train_dir
        validation_dir = self.settings.absolute_training_validation_dir
        existing_labels = set(self._load_existing_labels().values())

        if not existing_labels:
            raise ValueError("No existe labels.json previo. No se puede reentrenar sin las clases existentes.")

        missing: list[str] = []
        for label in sorted(existing_labels):
            if label == new_label:
                continue

            train_count = self._count_images(train_dir / label)
            validation_count = self._count_images(validation_dir / label)
            if train_count == 0 or validation_count == 0:
                missing.append(f"{label} (Train={train_count}, Validation={validation_count})")

        if missing:
            raise ValueError(
                "Para reentrenar sin perder clases, el backend necesita el dataset anterior. "
                "Faltan imágenes en DataSet/Train y/o DataSet/Validation para: " + "; ".join(missing)
            )

    def _save_captured_images(self, payload: TrainingRegisterRequest, model_label: str) -> tuple[Path, Path]:
        captured_total = len(payload.images_base64)
        expected_total = self.settings.training_capture_total_images
        train_count = self.settings.training_train_image_count
        validation_count = self.settings.training_validation_image_count

        if captured_total != expected_total:
            raise ValueError(f"Se esperaban {expected_total} imágenes y se recibieron {captured_total}")

        if train_count + validation_count != expected_total:
            raise ValueError("TRAIN + VALIDATION no coincide con el total configurado")

        train_target = self.settings.absolute_training_train_dir / model_label
        validation_target = self.settings.absolute_training_validation_dir / model_label

        if train_target.exists() or validation_target.exists():
            raise ValueError(
                f"Ya existe una carpeta de entrenamiento para la etiqueta {model_label}. "
                "Usa otra etiqueta o elimina el dataset anterior manualmente."
            )

        train_target.mkdir(parents=True, exist_ok=False)
        validation_target.mkdir(parents=True, exist_ok=False)

        try:
            for index, image_base64 in enumerate(payload.images_base64):
                image_bgr = decode_base64_image(image_base64)
                image_bgr = cv2.resize(
                    image_bgr,
                    (self.settings.model_input_width, self.settings.model_input_height),
                    interpolation=cv2.INTER_AREA,
                )

                if index < train_count:
                    folder = train_target
                    prefix = "train"
                else:
                    folder = validation_target
                    prefix = "val"

                output_path = folder / f"{prefix}_{index + 1:04d}.jpg"
                ok = cv2.imwrite(str(output_path), image_bgr)
                if not ok:
                    raise ValueError(f"No se pudo guardar la imagen {index + 1}")
        except Exception:
            shutil.rmtree(train_target, ignore_errors=True)
            shutil.rmtree(validation_target, ignore_errors=True)
            raise

        return train_target, validation_target

    def _build_model(self, num_classes: int):
        # TensorFlow se importa solo cuando se va a entrenar, para no hacer lento el arranque de la API.
        import tensorflow as tf
        from tensorflow.keras import layers, models

        img_size = self.settings.model_input_width

        data_augmentation = tf.keras.Sequential(
            [
                layers.RandomFlip("horizontal"),
                layers.RandomRotation(0.05),
                layers.RandomZoom(0.10),
                layers.RandomContrast(0.15),
                layers.RandomBrightness(0.10),
            ],
            name="data_augmentation",
        )

        model = models.Sequential(
            [
                layers.Input(shape=(img_size, img_size, 3)),
                data_augmentation,
                layers.Rescaling(1.0 / 255),
                layers.Conv2D(32, (3, 3), activation="relu", padding="same"),
                layers.MaxPooling2D(),
                layers.Dropout(0.2),
                layers.Conv2D(64, (3, 3), activation="relu", padding="same"),
                layers.MaxPooling2D(),
                layers.Dropout(0.25),
                layers.Conv2D(128, (3, 3), activation="relu", padding="same"),
                layers.MaxPooling2D(),
                layers.Dropout(0.3),
                layers.Conv2D(256, (3, 3), activation="relu", padding="same"),
                layers.MaxPooling2D(),
                layers.Dropout(0.3),
                layers.GlobalAveragePooling2D(),
                layers.Dense(128, activation="relu"),
                layers.Dropout(0.5),
                layers.Dense(num_classes, activation="softmax"),
            ]
        )

        model.compile(
            optimizer="adam",
            loss="sparse_categorical_crossentropy",
            metrics=["accuracy"],
        )
        return model

    def _train_model(self, job_id: str) -> dict[str, str]:
        import tensorflow as tf
        from tensorflow.keras.callbacks import Callback, EarlyStopping, ModelCheckpoint, ReduceLROnPlateau

        train_dir = self.settings.absolute_training_train_dir
        validation_dir = self.settings.absolute_training_validation_dir
        img_size = self.settings.model_input_width
        batch_size = self.settings.training_batch_size
        epochs = self.settings.training_epochs
        seed = self.settings.training_seed

        self._progress(job_id, 24, "dataset", "Cargando dataset de entrenamiento y validación...")

        train_ds = tf.keras.utils.image_dataset_from_directory(
            train_dir,
            image_size=(img_size, img_size),
            batch_size=batch_size,
            seed=seed,
            label_mode="int",
        )

        validation_ds = tf.keras.utils.image_dataset_from_directory(
            validation_dir,
            image_size=(img_size, img_size),
            batch_size=batch_size,
            seed=seed,
            label_mode="int",
        )

        class_names = list(train_ds.class_names)
        if class_names != list(validation_ds.class_names):
            raise ValueError("Las clases de Train y Validation no coinciden")

        num_classes = len(class_names)
        if num_classes < 2:
            raise ValueError("Se necesitan al menos 2 clases para entrenar el modelo")

        autotune = tf.data.AUTOTUNE
        train_ds = train_ds.cache().shuffle(1000).prefetch(buffer_size=autotune)
        validation_ds = validation_ds.cache().prefetch(buffer_size=autotune)

        self._progress(job_id, 30, "model", f"Construyendo modelo con {num_classes} clases...")
        model = self._build_model(num_classes)

        checkpoint_path = self.settings.absolute_training_output_dir / "best_model.weights.h5"
        checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

        class ProgressCallback(Callback):
            def on_epoch_end(callback_self, epoch, logs=None):  # noqa: ANN001
                logs = logs or {}
                percent = 30 + int(((epoch + 1) / max(epochs, 1)) * 58)
                self._progress(
                    job_id,
                    percent,
                    "training",
                    f"Entrenando modelo: época {epoch + 1}/{epochs}",
                    extra={
                        "epoch": epoch + 1,
                        "epochs": epochs,
                        "loss": float(logs.get("loss", 0.0)),
                        "accuracy": float(logs.get("accuracy", 0.0)),
                        "val_loss": float(logs.get("val_loss", 0.0)),
                        "val_accuracy": float(logs.get("val_accuracy", 0.0)),
                    },
                )

        callbacks = [
            EarlyStopping(
                monitor="val_loss",
                patience=self.settings.training_early_stopping_patience,
                restore_best_weights=True,
                verbose=0,
            ),
            ReduceLROnPlateau(
                monitor="val_loss",
                factor=0.3,
                patience=3,
                min_lr=1e-7,
                verbose=0,
            ),
            ModelCheckpoint(
                filepath=str(checkpoint_path),
                monitor="val_loss",
                mode="min",
                save_best_only=True,
                save_weights_only=True,
                verbose=0,
            ),
            ProgressCallback(),
        ]

        self._progress(job_id, 34, "training", "Iniciando entrenamiento del modelo...")
        model.fit(
            train_ds,
            validation_data=validation_ds,
            epochs=epochs,
            callbacks=callbacks,
            verbose=0,
        )

        self._progress(job_id, 91, "saving", "Guardando trained_model.keras y labels.json...")

        self.settings.absolute_model_path.parent.mkdir(parents=True, exist_ok=True)
        model.save(str(self.settings.absolute_model_path))

        labels = {str(index): class_name for index, class_name in enumerate(class_names)}
        self.settings.absolute_labels_path.parent.mkdir(parents=True, exist_ok=True)
        with self.settings.absolute_labels_path.open("w", encoding="utf-8") as file:
            json.dump(labels, file, indent=4, ensure_ascii=False)

        return labels

    def register_user_after_successful_training(self, db: Session, payload: TrainingRegisterRequest) -> tuple[Usuario, dict[str, str]]:
        job_id = payload.job_id
        model_label = self._validate_model_label(payload.nombre_etiqueta_modelo)
        training_progress_store.start(job_id, "Validando información del usuario...")

        if model_label.strip().lower() == self.settings.intruder_label_name.strip().lower():
            raise ValueError("La etiqueta Intruso es reservada y no puede usarse para usuarios")

        if UserService.get_by_employee_or_email(db, payload.numero_empleado):
            raise ValueError("Ya existe un usuario con ese número de empleado o correo")

        if UserService.get_by_model_label(db, model_label):
            raise ValueError("Ya existe un usuario relacionado con esa etiqueta del modelo")

        existing_labels = set(self._load_existing_labels().values())
        if model_label in existing_labels:
            raise ValueError(
                f"La etiqueta {model_label} ya existe en labels.json. "
                "Para registrar un usuario nuevo, usa una etiqueta nueva."
            )

        self._progress(job_id, 6, "validation", "Validando dataset existente del modelo...")
        self._validate_existing_dataset(model_label)

        train_target: Path | None = None
        validation_target: Path | None = None

        try:
            self._progress(job_id, 12, "images", "Guardando 220 imágenes para Train y 100 para Validation...")
            train_target, validation_target = self._save_captured_images(payload, model_label)

            labels = self._train_model(job_id)

            self._progress(job_id, 96, "database", "Entrenamiento exitoso. Guardando usuario en SQL Server...")
            user = Usuario(
                numero_empleado=payload.numero_empleado,
                nombre=payload.nombre,
                nombre_etiqueta_modelo=model_label,
                correo=str(payload.correo) if payload.correo else None,
                rol=payload.rol,
                activo=payload.activo,
                password_hash=get_password_hash(payload.password) if payload.password else None,
            )
            db.add(user)
            db.commit()
            db.refresh(user)

            # Obliga a que la siguiente predicción cargue el modelo y labels nuevos.
            try:
                from app.services.detection_service import detection_service

                detection_service.reload_face_recognizer()
            except Exception:
                pass

            training_progress_store.complete(
                job_id,
                "Entrenamiento terminado y usuario guardado correctamente.",
                extra={
                    "user_id": user.id_usuario,
                    "nombre": user.nombre,
                    "nombre_etiqueta_modelo": user.nombre_etiqueta_modelo,
                    "classes": labels,
                },
            )
            return user, labels

        except Exception as exc:
            db.rollback()
            if train_target:
                shutil.rmtree(train_target, ignore_errors=True)
            if validation_target:
                shutil.rmtree(validation_target, ignore_errors=True)
            training_progress_store.fail(job_id, str(exc))
            raise
