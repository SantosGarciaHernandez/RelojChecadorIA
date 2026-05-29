# RelojChecador IA

Aplicación web para registro automático de entrada y salida mediante reconocimiento facial con una red neuronal convolucional. El sistema usa un frontend en React, un backend en FastAPI, SQL Server como base de datos y un modelo entrenado en TensorFlow/Keras.

## 1. Requisitos previos

Antes de ejecutar el proyecto, instalar lo siguiente:

- Python 3.11 recomendado.
- Node.js LTS.
- SQL Server o SQL Server Express.
- SQL Server Management Studio, recomendado para ejecutar el script SQL.
- Microsoft ODBC Driver 18 for SQL Server.
- Git, opcional.
- Una cámara web funcional.

> Nota: se recomienda Python 3.11 para evitar problemas de compatibilidad con TensorFlow. Si se usa una versión más nueva de Python y falla la instalación de TensorFlow, crear el entorno virtual con Python 3.11.

## 2. Descomprimir el proyecto

Descomprimir el archivo `.zip` principal del proyecto en una carpeta local, por ejemplo:

```txt
C:\Proyectos\RelojChecadorIA
```

Después de descomprimir, la estructura principal debe quedar parecida a esta:

```txt
RelojChecadorIA/
  BD/
    script.sql

  RelojChecador.Backend/
    app/
    requirements.txt
    .env.example
    .env

  RelojChecador.Frontend/
    src/
    public/
    package.json
    .env.example

  Training/
    Notebooks/
    DataSet/
```

No ejecutar el proyecto directamente dentro del `.zip`. Primero debe estar completamente descomprimido.

## 3. Descomprimir o copiar el dataset

El entrenamiento desde el frontend necesita que el backend tenga disponible el dataset histórico del modelo. Si el dataset viene comprimido en un archivo separado, por ejemplo `DataSet.zip`, `training_dataset.zip` o similar, se debe descomprimir antes de ejecutar el entrenamiento.

El dataset debe quedar dentro de:

```txt
RelojChecador.Backend/app/ml/training_dataset/
```

La estructura correcta debe ser:

```txt
RelojChecador.Backend/app/ml/training_dataset/
  Train/
    CotoSet/
    DanielSet/
    Intruso/
    Lizbeth Castañeda Rivas/
    NaomiSet3/
    SantosSet/
    angelito/

  Validation/
    CotoSet/
    DanielSet/
    Intruso/
    Lizbeth Castañeda Rivas/
    NaomiSet3/
    SantosSet/
    angelito/
```

Cada carpeta debe contener las imágenes correspondientes a esa clase.

No se debe dejar el dataset como archivo `.zip` dentro de `training_dataset`. El backend necesita las carpetas reales `Train` y `Validation` con las imágenes descomprimidas.

Si el dataset está en la carpeta `Training/DataSet`, copiar o descomprimir su contenido hacia:

```txt
RelojChecador.Backend/app/ml/training_dataset/
```

El modelo ya entrenado se encuentra en:

```txt
RelojChecador.Backend/app/ml/trained_model.keras
```

Y las etiquetas del modelo en:

```txt
RelojChecador.Backend/app/ml/labels.json
```

## 4. Crear la base de datos

Abrir SQL Server Management Studio y ejecutar el script:

```txt
BD/script.sql
```

Este script crea la base de datos:

```txt
RelojChecadorIA
```

También crea las tablas principales:

```txt
Usuarios
Equipos
RegistroUsuarios
RegistroIntrusos
ConfiguracionSistema
```

Los equipos demo que usa el frontend son:

```txt
PC-ENTRADA-01
PC-SALIDA-01
```

Después de ejecutar el script, se recomienda validar el umbral de intruso. El proyecto está configurado para trabajar con `0.70` como umbral recomendado.

Ejecutar esta consulta en SQL Server:

```sql
USE RelojChecadorIA;

UPDATE ConfiguracionSistema
SET UmbralConfianzaIntruso = 0.70
WHERE IdConfiguracion = 1;
```

## 5. Configurar el backend

Entrar a la carpeta del backend:

```powershell
cd RelojChecador.Backend
```

Crear el entorno virtual:

```powershell
python -m venv .venv
```

Activar el entorno virtual:

```powershell
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea la activación del entorno virtual, ejecutar:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

Actualizar `pip`:

```powershell
python -m pip install --upgrade pip
```

Instalar las dependencias del backend:

```powershell
pip install -r requirements.txt
```

El archivo `requirements.txt` instala las dependencias principales:

```txt
fastapi
uvicorn
sqlalchemy
pyodbc
pydantic-settings
python-dotenv
python-multipart
numpy
opencv-python-headless
Pillow
tensorflow
keras
passlib[bcrypt]
python-jose[cryptography]
email-validator
```

## 6. Configurar el archivo `.env` del backend

Si no existe el archivo `.env`, copiar el ejemplo:

```powershell
copy .env.example .env
```

Editar el archivo `.env` y ajustar la conexión a SQL Server:

```env
APP_NAME=RelojChecador IA API
ENVIRONMENT=development
DEBUG=true
API_PREFIX=/api

CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","http://localhost:5174","http://127.0.0.1:5174","http://localhost:3000","http://127.0.0.1:3000"]

SQL_SERVER=localhost\SQLEXPRESS
SQL_DATABASE=RelojChecadorIA
SQL_USERNAME=sa
SQL_PASSWORD=TuPassword
SQL_DRIVER=ODBC Driver 18 for SQL Server
SQL_TRUST_SERVER_CERTIFICATE=yes
SQL_ENCRYPT=yes

SECRET_KEY=cambia_esta_clave_en_produccion
ACCESS_TOKEN_EXPIRE_MINUTES=480

MODEL_PATH=app/ml/trained_model.keras
LABELS_PATH=app/ml/labels.json
MODEL_INPUT_WIDTH=128
MODEL_INPUT_HEIGHT=128
MODEL_INPUT_CHANNELS=3
MODEL_NORMALIZE_INPUT=false
FRONTEND_SENDS_FACE_CROP=true
DEFAULT_INTRUDER_THRESHOLD=0.70
INTRUDER_LABEL_NAME=Intruso

ATTENDANCE_REQUIRED_CONSECUTIVE_VALIDATIONS=3

AUTO_CREATE_TABLES=false

SMTP_ENABLED=false
SMTP_HOST=
SMTP_PORT=587
SMTP_USERNAME=
SMTP_PASSWORD=
SMTP_FROM=
SMTP_USE_TLS=true

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

Cambiar estos valores según la instalación local:

```env
SQL_SERVER=localhost\SQLEXPRESS
SQL_USERNAME=sa
SQL_PASSWORD=TuPassword
```

Si SQL Server no usa instancia `SQLEXPRESS`, puede ser:

```env
SQL_SERVER=localhost
```

Si se usa el nombre de una instancia específica, usar el formato:

```env
SQL_SERVER=NOMBRE_EQUIPO\NOMBRE_INSTANCIA
```

## 7. Ejecutar el backend

Desde la carpeta `RelojChecador.Backend`, con el entorno virtual activado, ejecutar:

```powershell
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Para exponerlo en la red local:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Probar el backend en el navegador:

```txt
http://127.0.0.1:8000/docs
```

También se puede probar el endpoint de salud:

```txt
http://127.0.0.1:8000/api/health
```

## 8. Configurar el frontend

Abrir otra terminal y entrar a la carpeta del frontend:

```powershell
cd RelojChecador.Frontend
```

Instalar dependencias:

```powershell
npm install
```

Las dependencias principales del frontend son:

```txt
react
react-dom
vite
face-api.js
react-webcam
```

Crear el archivo `.env` en la raíz del frontend:

```powershell
New-Item .env -ItemType File
```

Agregar este contenido:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
VITE_ENTRY_PC_NAME=PC-ENTRADA-01
VITE_EXIT_PC_NAME=PC-SALIDA-01
```

Los valores `PC-ENTRADA-01` y `PC-SALIDA-01` deben existir en la tabla `Equipos` de SQL Server.

## 9. Ejecutar el frontend

Desde la carpeta `RelojChecador.Frontend`, ejecutar:

```powershell
npm run dev
```

Abrir la aplicación en el navegador:

```txt
http://localhost:5173
```

Si Vite usa otro puerto, por ejemplo `5174`, abrir la URL que aparezca en la terminal.

## 10. Orden recomendado para ejecutar todo

1. Descomprimir el ZIP del proyecto.
2. Descomprimir o copiar el dataset en `RelojChecador.Backend/app/ml/training_dataset`.
3. Ejecutar `BD/script.sql` en SQL Server.
4. Actualizar `UmbralConfianzaIntruso` a `0.70`.
5. Configurar el `.env` del backend.
6. Crear y activar el entorno virtual del backend.
7. Instalar dependencias con `pip install -r requirements.txt`.
8. Ejecutar el backend con `uvicorn`.
9. Configurar el `.env` del frontend.
10. Instalar dependencias con `npm install`.
11. Ejecutar el frontend con `npm run dev`.
12. Abrir la aplicación en el navegador.

## 11. Uso básico del sistema

### Registro de entrada o salida

1. Abrir la aplicación web.
2. Permitir acceso a la cámara.
3. Seleccionar modo `Entrada` o `Salida`.
4. Colocar el rostro frente a la cámara.
5. El frontend detecta el rostro con `face-api.js`.
6. El frontend recorta el rostro y lo envía al backend.
7. El backend predice con `trained_model.keras`.
8. Si se cumplen las validaciones consecutivas, se registra la entrada o salida en SQL Server.

### Detección de intruso

El sistema registra un intruso cuando:

- El modelo predice la clase `Intruso`.
- La confianza del modelo es menor al umbral configurado.

El registro se guarda en la tabla:

```txt
RegistroIntrusos
```

La evidencia de imagen se guarda en el campo:

```txt
ImagenBinaria
```

### Registro de nuevo usuario con entrenamiento

Para usar el flujo de entrenamiento desde el frontend:

1. Verificar que el dataset histórico exista en `app/ml/training_dataset`.
2. Abrir la pantalla de registro de usuario.
3. Capturar los datos del usuario.
4. Capturar las imágenes del rostro.
5. El backend guarda las imágenes.
6. El backend reentrena el modelo.
7. El backend actualiza `trained_model.keras` y `labels.json`.
8. Si el entrenamiento termina correctamente, el usuario se guarda en SQL Server.

La configuración esperada es:

```env
TRAINING_CAPTURE_TOTAL_IMAGES=320
TRAINING_TRAIN_IMAGE_COUNT=220
TRAINING_VALIDATION_IMAGE_COUNT=100
```

## 12. Endpoints principales

Swagger:

```txt
http://127.0.0.1:8000/docs
```

Predicción facial:

```txt
POST /api/detection/predict
```

Registros recientes:

```txt
GET /api/attendance/recent
```

Registro de usuario con entrenamiento:

```txt
POST /api/training/register-user
```

WebSocket de registros recientes:

```txt
/ws/attendance/recent
```

WebSocket de progreso de entrenamiento:

```txt
/ws/training/{job_id}
```

## 13. Problemas comunes

### Error de conexión a SQL Server

Revisar:

- Que SQL Server esté iniciado.
- Que la base de datos `RelojChecadorIA` exista.
- Que el usuario y contraseña del `.env` sean correctos.
- Que el valor `SQL_SERVER` sea correcto.
- Que esté instalado `ODBC Driver 18 for SQL Server`.

### Error con `pyodbc`

Instalar el Microsoft ODBC Driver 18 for SQL Server y verificar que el nombre coincida con el `.env`:

```env
SQL_DRIVER=ODBC Driver 18 for SQL Server
```

### Error al entrenar un nuevo usuario

Revisar que exista el dataset histórico:

```txt
RelojChecador.Backend/app/ml/training_dataset/Train
RelojChecador.Backend/app/ml/training_dataset/Validation
```

También revisar que el frontend y backend usen la misma cantidad de imágenes:

```txt
320 total
220 entrenamiento
100 validación
```

### El frontend no conecta con el backend

Revisar el archivo `.env` del frontend:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

También revisar que el backend esté corriendo en:

```txt
http://127.0.0.1:8000
```

### El navegador no abre la cámara

Revisar:

- Permisos de cámara del navegador.
- Que otra aplicación no esté usando la cámara.
- Probar en Chrome o Edge.
- Usar `localhost` o `127.0.0.1`.

## 14. Archivos importantes

```txt
BD/script.sql
```

Script para crear la base de datos.

```txt
RelojChecador.Backend/requirements.txt
```

Dependencias del backend.

```txt
RelojChecador.Backend/.env
```

Configuración del backend.

```txt
RelojChecador.Backend/app/ml/trained_model.keras
```

Modelo entrenado.

```txt
RelojChecador.Backend/app/ml/labels.json
```

Etiquetas del modelo.

```txt
RelojChecador.Backend/app/ml/training_dataset
```

Dataset histórico necesario para reentrenamiento.

```txt
RelojChecador.Frontend/package.json
```

Dependencias y scripts del frontend.

```txt
RelojChecador.Frontend/.env
```

Configuración del frontend.

## 15. Comandos rápidos

Backend:

```powershell
cd RelojChecador.Backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Frontend:

```powershell
cd RelojChecador.Frontend
npm install
npm run dev
```

Abrir:

```txt
http://localhost:5173
```

