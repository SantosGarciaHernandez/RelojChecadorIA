from pathlib import Path
import argparse
import json
import cv2
import numpy as np
import tensorflow as tf


# =========================
# CONFIGURACIÓN DEFAULT
# =========================

DEFAULT_MODEL_PATH = r"D:\\Aplicaciones multiplataforma\\002 - RelojChecador IA\\Training\\Notebooks\\Model\\trained_model.keras"
DEFAULT_LABELS_PATH = r"D:\\Aplicaciones multiplataforma\\002 - RelojChecador IA\\Training\\Notebooks\\Model\\labels.json"

IMG_SIZE = 128
THRESHOLD = 0.70
FACE_MARGIN = 0.25


# =========================
# CARGA DE MODELO Y LABELS
# =========================

def load_model_and_labels(model_path, labels_path):
    model_path = Path(model_path)
    labels_path = Path(labels_path)

    if not model_path.exists():
        raise FileNotFoundError(f"No existe el modelo: {model_path}")

    if not labels_path.exists():
        raise FileNotFoundError(f"No existe el archivo labels.json: {labels_path}")

    model = tf.keras.models.load_model(model_path, compile=False)

    with open(labels_path, "r", encoding="utf-8") as f:
        labels = json.load(f)

    return model, labels


# =========================
# DETECTOR DE ROSTRO
# =========================

def load_face_detector():
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    face_detector = cv2.CascadeClassifier(cascade_path)

    if face_detector.empty():
        raise RuntimeError("No se pudo cargar el detector Haar Cascade de OpenCV.")

    return face_detector


# =========================
# RECORTE DE ROSTRO
# =========================

def crop_largest_face(image_path, face_detector, img_size=128, margin=0.25):
    image_path = Path(image_path)

    if not image_path.exists():
        raise FileNotFoundError(f"No existe la imagen: {image_path}")

    image_bgr = cv2.imread(str(image_path))

    if image_bgr is None:
        raise ValueError(f"No se pudo leer la imagen: {image_path}")

    gray = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2GRAY)

    faces = face_detector.detectMultiScale(
        gray,
        scaleFactor=1.1,
        minNeighbors=5,
        minSize=(60, 60)
    )

    if len(faces) == 0:
        return None, image_bgr, "sin_rostro"

    # Seleccionar el rostro más grande
    x, y, w, h = max(faces, key=lambda face: face[2] * face[3])

    margin_x = int(w * margin)
    margin_y = int(h * margin)

    x1 = max(0, x - margin_x)
    y1 = max(0, y - margin_y)
    x2 = min(image_bgr.shape[1], x + w + margin_x)
    y2 = min(image_bgr.shape[0], y + h + margin_y)

    face_crop_bgr = image_bgr[y1:y2, x1:x2]

    if face_crop_bgr.size == 0:
        return None, image_bgr, "recorte_vacio"

    face_resized_bgr = cv2.resize(face_crop_bgr, (img_size, img_size))

    return face_resized_bgr, image_bgr, "ok"


# =========================
# PREDICCIÓN
# =========================

def predict_image(image_path, model, labels, face_detector):
    face_bgr, original_bgr, status = crop_largest_face(
        image_path=image_path,
        face_detector=face_detector,
        img_size=IMG_SIZE,
        margin=FACE_MARGIN
    )

    if status != "ok":
        print("No se pudo procesar la imagen.")
        print("Estado:", status)
        return {
            "success": False,
            "status": status
        }

    # OpenCV lee en BGR, TensorFlow normalmente espera RGB
    face_rgb = cv2.cvtColor(face_bgr, cv2.COLOR_BGR2RGB)

    # Batch: (1, 128, 128, 3)
    input_img = np.expand_dims(face_rgb, axis=0)

    # OJO:
    # Si tu modelo ya tiene layers.Rescaling(1./255), NO normalices aquí.
    # Si tu modelo NO tiene Rescaling, entonces usa:
    # input_img = input_img / 255.0

    predictions = model.predict(input_img, verbose=0)[0]

    predicted_index = int(np.argmax(predictions))
    confidence = float(predictions[predicted_index])

    predicted_label = labels.get(str(predicted_index), f"Clase_{predicted_index}")

    label_lower = predicted_label.lower()

    if label_lower != "intruso" and confidence >= THRESHOLD:
        final_result = "Usuario reconocido"
        is_intruder = False
    else:
        final_result = "Intruso / desconocido"
        is_intruder = True

    print("\n========== RESULTADO ==========")
    print("Imagen:", image_path)
    print("Predicción completa:", predictions)
    print("Índice predicho:", predicted_index)
    print("Clase predicha:", predicted_label)
    print("Confianza:", round(confidence * 100, 2), "%")
    print("Resultado final:", final_result)
    print("¿Es intruso?:", is_intruder)
    print("================================\n")

    return {
        "success": True,
        "predicted_index": predicted_index,
        "predicted_label": predicted_label,
        "confidence": confidence,
        "is_intruder": is_intruder,
        "result": final_result
    }


# =========================
# MAIN
# =========================

def main():
    parser = argparse.ArgumentParser(
        description="Probar modelo CNN de RelojChecador IA con una imagen."
    )

    parser.add_argument(
        "--image",
        required=True,
        help="Ruta de la imagen que quieres probar."
    )

    parser.add_argument(
        "--model",
        default=DEFAULT_MODEL_PATH,
        help="Ruta del modelo .h5."
    )

    parser.add_argument(
        "--labels",
        default=DEFAULT_LABELS_PATH,
        help="Ruta del archivo labels.json."
    )

    args = parser.parse_args()

    print("Cargando modelo...")
    model, labels = load_model_and_labels(args.model, args.labels)

    print("Labels cargados:", labels)

    print("Cargando detector facial...")
    face_detector = load_face_detector()

    print("Procesando imagen...")
    predict_image(
        image_path=args.image,
        model=model,
        labels=labels,
        face_detector=face_detector
    )


if __name__ == "__main__":
    main()