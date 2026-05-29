from pathlib import Path
from threading import Lock
from typing import Any


class ModelLoader:
    """Carga perezosa del modelo. Keras/TensorFlow se importa solo cuando se necesita."""

    def __init__(self, model_path: Path) -> None:
        self.model_path = model_path
        self._model: Any = None
        self._lock = Lock()

    def get_model(self) -> Any:
        if self._model is not None:
            return self._model

        with self._lock:
            if self._model is None:
                if not self.model_path.exists():
                    raise FileNotFoundError(f"No existe el modelo entrenado: {self.model_path}")

                # Formato .keras moderno. Se intenta primero con Keras 3 y luego con tf.keras.
                try:
                    from keras.saving import load_model
                except Exception:  # pragma: no cover - fallback de compatibilidad
                    from tensorflow.keras.models import load_model

                # compile=False es suficiente para inferencia y evita errores con métricas/loss de entrenamiento.
                self._model = load_model(str(self.model_path), compile=False)
        return self._model
