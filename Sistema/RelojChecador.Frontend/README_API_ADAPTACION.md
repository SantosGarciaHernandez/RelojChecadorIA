# Adaptación del frontend al backend FastAPI

## Endpoints corregidos

El frontend ya no usa los endpoints antiguos:

- `http://localhost:5000/usuario`
- `http://localhost:5000/upload`

Ahora usa el backend FastAPI:

- `POST /api/detection/predict`
- `POST /api/users`
- `GET /api/health`

## Variables de entorno

Crea un archivo `.env` en la raíz del frontend si quieres cambiar la URL de la API o los equipos simulados:

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
VITE_ENTRY_PC_NAME=PC-ENTRADA-01
VITE_EXIT_PC_NAME=PC-SALIDA-01
```

Los valores de `VITE_ENTRY_PC_NAME` y `VITE_EXIT_PC_NAME` deben existir en la tabla `Equipos` del SQL Server. Con el `seed_demo.sql` del backend existen:

- `PC-ENTRADA-01`, acción `Entrada`
- `PC-SALIDA-01`, acción `Salida`

## Toggle Entrada / Salida

En la pantalla de escaneo facial se agregó un toggle pequeño debajo de la cámara.

- Si eliges `Entrada`, el frontend envía `pc_name = PC-ENTRADA-01`.
- Si eliges `Salida`, el frontend envía `pc_name = PC-SALIDA-01`.

Esto permite simular desde una sola computadora el comportamiento de dos equipos físicos diferentes.

## Flujo de detección

1. El frontend detecta el rostro con `face-api.js`.
2. Recorta la cara en el navegador.
3. Envía la cara recortada como base64 a `POST /api/detection/predict`.
4. El request incluye `pc_name` según el toggle Entrada/Salida.
5. El backend predice con `trained_model.keras`.
6. Si reconoce al usuario, registra entrada/salida según el equipo simulado.
7. Si detecta intruso o confianza baja, registra alerta de intruso.

## Flujo de registro

El registro de usuario ahora llama a `POST /api/users`.

Importante: este flujo no entrena el modelo. Solo registra el usuario en SQL Server. Para que el reconocimiento funcione, `nombre_etiqueta_modelo` debe coincidir con una etiqueta existente en `labels.json`, por ejemplo:

- `SantosSet`
- `NaomiSet`
- `CotoSet`
- `DanielSet`
- `Jesus Guzman`
- `Lizbeth Castañeda Rivas`

## Comandos

```bash
npm install
npm run dev
```

Abrir:

```txt
http://localhost:5173
```
