# RelojChecador IA - Backend FastAPI

Backend por capas para exponer un modelo Keras como servicio y registrar entradas, salidas e intrusos en SQL Server.

## Ajuste importante de esta versión

Esta versión ya está ajustada al modelo real del proyecto:

- Modelo: `app/ml/trained_model.keras`
- Labels: `app/ml/labels.json`
- Entrada esperada: `128x128x3`
- El frontend debe mandar una **cara ya recortada**.
- La API **no divide entre 255**, porque el modelo ya incluye una capa `Rescaling(1./255)`.
- La clase `Intruso` se trata como alerta y no como usuario.
- Los usuarios se enlazan con el modelo usando `Usuarios.NombreEtiquetaModelo`.

Ejemplo de labels actual:

```json
{
  "0": "CotoSet",
  "1": "DanielSet",
  "2": "Intruso",
  "3": "Jesus Guzman",
  "4": "Lizbeth Castañeda Rivas",
  "5": "NaomiSet",
  "6": "SantosSet"
}
```

## Estructura principal

```txt
app/
  api/routes/              Endpoints REST
  core/                    Configuración y seguridad
  database/                Sesión SQLAlchemy
  ml/                      Modelo, labels y preprocesamiento
  models/                  Modelos SQLAlchemy
  schemas/                 DTOs Pydantic
  services/                Reglas de negocio
  websockets/              WebSocket de detección
scripts/
  create_tables.sql
  seed_demo.sql
```

## Crear entorno virtual

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Si PowerShell bloquea el entorno:

```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.\.venv\Scripts\Activate.ps1
```

## Instalar dependencias

```powershell
pip install -r requirements.txt
```

## Configurar .env

```powershell
copy .env.example .env
```

Revisa estos valores:

```env
SQL_SERVER=localhost
SQL_DATABASE=RelojChecadorIA
SQL_USERNAME=sa
SQL_PASSWORD=TuPassword
MODEL_PATH=app/ml/trained_model.keras
LABELS_PATH=app/ml/labels.json
MODEL_NORMALIZE_INPUT=false
```

## Crear base de datos

Con autenticación de Windows:

```powershell
sqlcmd -S localhost -E -Q "CREATE DATABASE RelojChecadorIA;"
sqlcmd -S localhost -E -d RelojChecadorIA -i .\scripts\create_tables.sql
sqlcmd -S localhost -E -d RelojChecadorIA -i .\scripts\seed_demo.sql
```

Con usuario `sa`:

```powershell
sqlcmd -S localhost -U sa -P "TuPassword" -Q "CREATE DATABASE RelojChecadorIA;"
sqlcmd -S localhost -U sa -P "TuPassword" -d RelojChecadorIA -i .\scripts\create_tables.sql
sqlcmd -S localhost -U sa -P "TuPassword" -d RelojChecadorIA -i .\scripts\seed_demo.sql
```

## Correr API

```powershell
uvicorn app.main:app --reload
```

Para exponerla en red local:

```powershell
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Swagger:

```txt
http://127.0.0.1:8000/docs
```

## Endpoints principales

### Probar con archivo desde Swagger

```txt
POST /api/detection/predict-file
```

Campos:

```txt
pc_name = PC-ENTRADA-01
file = imagen de cara recortada
```

### Probar con base64

```txt
POST /api/detection/predict
```

Body:

```json
{
  "pc_name": "PC-ENTRADA-01",
  "image_base64": "data:image/jpeg;base64,..."
}
```

### WebSocket

```txt
/ws/detection
```

Mensaje inicial:

```json
{
  "type": "init",
  "pc_name": "PC-ENTRADA-01"
}
```

Mensaje de frame:

```json
{
  "type": "frame",
  "image": "data:image/jpeg;base64,..."
}
```

La imagen debe ser la cara recortada.

## Relación labels.json con Usuarios

La API busca usuarios en este orden:

1. `user_id`, si el label viene como objeto.
2. `employee_number`, si el label viene como objeto.
3. `NombreEtiquetaModelo`, para tu `labels.json` actual.
4. `Nombre`, como fallback.

Por eso la tabla `Usuarios` tiene esta columna:

```sql
NombreEtiquetaModelo NVARCHAR(100) NULL UNIQUE
```

Ejemplo:

```sql
INSERT INTO Usuarios (NumeroEmpleado, Nombre, NombreEtiquetaModelo, Rol, Activo)
VALUES ('E001', 'Santos Garcia Hernandez', 'SantosSet', 'Administrador', 1);
```

## Nota sobre OpenCV

OpenCV se conserva para decodificar imágenes y como fallback en:

```txt
POST /api/detection/predict-full-frame-opencv
```

Pero el flujo real recomendado es enviar la cara recortada desde el frontend.
