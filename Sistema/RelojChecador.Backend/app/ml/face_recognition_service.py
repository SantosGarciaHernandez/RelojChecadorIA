import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np

from app.core.config import get_settings
from app.ml.image_preprocessing import preprocess_face
from app.ml.model_loader import ModelLoader


@dataclass
class FacePrediction:
    recognized: bool
    is_intruder_label: bool
    class_index: int | None
    confidence: float
    user_id: int | None
    employee_number: str | None
    name: str | None
    model_label: str | None
    raw_label: Any | None
    probabilities: dict[str, float]


class FaceRecognitionService:
    def __init__(self, model_path: Path | None = None, labels_path: Path | None = None) -> None:
        settings = get_settings()
        self.settings = settings
        self.model_loader = ModelLoader(model_path or settings.absolute_model_path)
        self.labels_path = labels_path or settings.absolute_labels_path
        self.labels = self._load_labels(self.labels_path)

    @staticmethod
    def _load_labels(path: Path) -> dict[str, Any]:
        if not path.exists():
            raise FileNotFoundError(f"No existe labels.json: {path}")
        with path.open("r", encoding="utf-8") as file:
            labels = json.load(file)
        if not isinstance(labels, dict):
            raise ValueError("labels.json debe ser un objeto JSON con índices de clase como llave")
        return labels

    @staticmethod
    def _normalize_label(raw_label: Any) -> tuple[int | None, str | None, str | None, str | None]:
        """
        Soporta dos formatos:
        "0": "SantosSet"
        "0": {"user_id": 1, "employee_number": "E001", "name": "Santos", "model_label": "SantosSet"}
        """
        if isinstance(raw_label, dict):
            user_id = raw_label.get("user_id") or raw_label.get("id_usuario")
            employee_number = raw_label.get("employee_number") or raw_label.get("numero_empleado")
            name = raw_label.get("name") or raw_label.get("nombre")
            model_label = raw_label.get("model_label") or raw_label.get("nombre_etiqueta_modelo") or name
            return int(user_id) if user_id is not None else None, employee_number, name, model_label

        if isinstance(raw_label, str):
            return None, None, raw_label, raw_label

        return None, None, None, None

    def _probabilities_by_label(self, prediction: np.ndarray) -> dict[str, float]:
        probabilities: dict[str, float] = {}
        for index, probability in enumerate(prediction):
            raw_label = self.labels.get(str(index), f"Clase_{index}")
            _, _, _, model_label = self._normalize_label(raw_label)
            probabilities[model_label or f"Clase_{index}"] = float(probability)
        return probabilities

    def predict(self, face_bgr: np.ndarray, threshold: float | None = None) -> FacePrediction:
        model = self.model_loader.get_model()
        threshold = threshold if threshold is not None else self.settings.default_intruder_threshold

        input_tensor = preprocess_face(
            face_bgr,
            target_size=(self.settings.model_input_width, self.settings.model_input_height),
            channels=self.settings.model_input_channels,
            normalize=self.settings.model_normalize_input,
        )
        prediction = model.predict(input_tensor, verbose=0)[0]
        class_index = int(np.argmax(prediction))
        confidence = float(prediction[class_index])
        raw_label = self.labels.get(str(class_index))
        user_id, employee_number, name, model_label = self._normalize_label(raw_label)

        is_intruder_label = (model_label or "").strip().lower() == self.settings.intruder_label_name.strip().lower()
        recognized = confidence >= threshold and raw_label is not None and not is_intruder_label

        return FacePrediction(
            recognized=recognized,
            is_intruder_label=is_intruder_label,
            class_index=class_index,
            confidence=confidence,
            user_id=user_id,
            employee_number=employee_number,
            name=name,
            model_label=model_label,
            raw_label=raw_label,
            probabilities=self._probabilities_by_label(prediction),
        )
