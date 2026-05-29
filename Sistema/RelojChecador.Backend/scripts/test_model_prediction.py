"""Prueba rápida del modelo sin levantar FastAPI.

Uso:
python scripts/test_model_prediction.py --image "C:\ruta\cara_recortada.jpg"
"""

import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from keras.saving import load_model


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--image", required=True, help="Ruta de una cara recortada")
    parser.add_argument("--model", default="app/ml/trained_model.keras")
    parser.add_argument("--labels", default="app/ml/labels.json")
    args = parser.parse_args()

    model = load_model(args.model, compile=False)
    labels = json.loads(Path(args.labels).read_text(encoding="utf-8"))

    image = cv2.imread(args.image)
    if image is None:
        raise FileNotFoundError(f"No se pudo leer la imagen: {args.image}")

    image = cv2.resize(image, (128, 128), interpolation=cv2.INTER_AREA)
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # No dividir entre 255: el modelo ya tiene Rescaling.
    tensor = np.expand_dims(image.astype("float32"), axis=0)
    prediction = model.predict(tensor, verbose=0)[0]

    index = int(np.argmax(prediction))
    print("Clase:", index)
    print("Etiqueta:", labels[str(index)])
    print("Confianza:", float(prediction[index]))
    print("Probabilidades:")
    for i, value in enumerate(prediction):
        print(f"  {i} - {labels[str(i)]}: {float(value):.4f}")


if __name__ == "__main__":
    main()
