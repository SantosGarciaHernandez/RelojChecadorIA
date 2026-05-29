from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import (
    attendance_routes,
    auth_routes,
    config_routes,
    dashboard_routes,
    detection_routes,
    devices_routes,
    health_routes,
    intruder_routes,
    users_routes,
    training_routes,
)
from app.core.config import get_settings
from app.database.init_db import create_database_tables
from app.websockets.detection_socket import router as detection_ws_router
from app.websockets.attendance_socket import router as attendance_ws_router
from app.websockets.training_socket import router as training_ws_router

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins if settings.cors_origins != ["*"] else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    if settings.auto_create_tables:
        create_database_tables()


app.include_router(health_routes.router, prefix=settings.api_prefix)
app.include_router(auth_routes.router, prefix=settings.api_prefix)
app.include_router(users_routes.router, prefix=settings.api_prefix)
app.include_router(devices_routes.router, prefix=settings.api_prefix)
app.include_router(attendance_routes.router, prefix=settings.api_prefix)
app.include_router(intruder_routes.router, prefix=settings.api_prefix)
app.include_router(config_routes.router, prefix=settings.api_prefix)
app.include_router(dashboard_routes.router, prefix=settings.api_prefix)
app.include_router(detection_routes.router, prefix=settings.api_prefix)
app.include_router(training_routes.router, prefix=settings.api_prefix)
app.include_router(detection_ws_router)
app.include_router(attendance_ws_router)
app.include_router(training_ws_router)
