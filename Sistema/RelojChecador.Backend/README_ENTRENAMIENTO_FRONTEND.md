# Entrenamiento desde frontend

Este flujo registra un usuario solamente si el modelo se reentrena correctamente.

## Flujo

1. El formulario captura datos del usuario.
2. La cámara captura 320 imágenes del rostro ya recortado.
3. El frontend envía las 320 imágenes a `POST /api/training/register-user`.
4. El backend guarda:
   - 220 imágenes en `app/ml/training_dataset/Train/<EtiquetaModelo>`
   - 100 imágenes en `app/ml/training_dataset/Validation/<EtiquetaModelo>`
5. El backend reentrena el modelo con todas las clases existentes.
6. Si el entrenamiento termina bien:
   - Actualiza `app/ml/trained_model.keras`
   - Actualiza `app/ml/labels.json`
   - Crea el usuario en SQL Server
7. Si falla cualquier paso, el usuario no se guarda.

## WebSocket de progreso

```txt
/ws/training/{job_id}
```

El frontend abre este WebSocket antes de mandar el entrenamiento. El backend informa:

- validación
- guardado de imágenes
- carga del dataset
- época actual
- accuracy / val_accuracy
- guardado del modelo
- guardado del usuario
- error si falla

## Requisito importante

Para agregar una nueva clase sin perder las anteriores, el backend necesita tener el dataset histórico del modelo:

```txt
app/ml/training_dataset/Train/CotoSet
app/ml/training_dataset/Train/DanielSet
app/ml/training_dataset/Train/Intruso
app/ml/training_dataset/Train/Jesus Guzman
app/ml/training_dataset/Train/Lizbeth Castañeda Rivas
app/ml/training_dataset/Train/NaomiSet
app/ml/training_dataset/Train/SantosSet

app/ml/training_dataset/Validation/CotoSet
app/ml/training_dataset/Validation/DanielSet
app/ml/training_dataset/Validation/Intruso
app/ml/training_dataset/Validation/Jesus Guzman
app/ml/training_dataset/Validation/Lizbeth Castañeda Rivas
app/ml/training_dataset/Validation/NaomiSet
app/ml/training_dataset/Validation/SantosSet
```

No se puede reconstruir el dataset original desde `trained_model.keras`. Si esas carpetas no existen, el endpoint fallará y no guardará el usuario.

## Configuración `.env`

```env
TRAINING_DATASET_DIR=app/ml/training_dataset
TRAINING_OUTPUT_DIR=app/ml/training_output
TRAINING_CAPTURE_TOTAL_IMAGES=320
TRAINING_TRAIN_IMAGE_COUNT=220
TRAINING_VALIDATION_IMAGE_COUNT=100
TRAINING_EPOCHS=40
TRAINING_BATCH_SIZE=16
TRAINING_SEED=47
TRAINING_EARLY_STOPPING_PATIENCE=8
```
