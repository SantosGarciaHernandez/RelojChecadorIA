# Parche SQL Server Boolean + CORS 5174

Este parche corrige el error de SQL Server:

```sql
WHERE [Equipos].[NombrePc] = ? AND [Equipos].[Activo] IS 1
```

SQL Server no acepta `IS 1` para columnas BIT. El backend debe generar `= 1`.

## Archivos a reemplazar

Copia estas rutas sobre tu backend actual:

```txt
app/services/device_service.py
app/services/notification_service.py
app/services/dashboard_service.py
```

## CORS

Tu frontend está corriendo en `http://localhost:5174`, así que agrega ese origen en tu `.env` del backend:

```env
CORS_ORIGINS=["http://localhost:5173","http://127.0.0.1:5173","http://localhost:5174","http://127.0.0.1:5174","http://localhost:3000","http://127.0.0.1:3000"]
```

Después reinicia Uvicorn.
