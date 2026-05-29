from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.common_schema import MessageResponse
from app.schemas.device_schema import DeviceCreate, DeviceResponse, DeviceUpdate
from app.services.device_service import DeviceService

router = APIRouter(prefix="/devices", tags=["Equipos"])


@router.get("", response_model=list[DeviceResponse])
def list_devices(only_active: bool | None = Query(default=None), db: Session = Depends(get_db)):
    return DeviceService.list(db, only_active=only_active)


@router.get("/by-name/{pc_name}", response_model=DeviceResponse)
def get_device_by_name(pc_name: str, db: Session = Depends(get_db)):
    device = DeviceService.get_by_name(db, pc_name)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado")
    return device


@router.get("/{device_id}", response_model=DeviceResponse)
def get_device(device_id: int, db: Session = Depends(get_db)):
    device = DeviceService.get(db, device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado")
    return device


@router.post("", response_model=DeviceResponse, status_code=status.HTTP_201_CREATED)
def create_device(payload: DeviceCreate, db: Session = Depends(get_db)):
    existing = DeviceService.get_by_name(db, payload.nombre_pc)
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Ya existe un equipo con ese nombre")
    return DeviceService.create(db, payload)


@router.put("/{device_id}", response_model=DeviceResponse)
def update_device(device_id: int, payload: DeviceUpdate, db: Session = Depends(get_db)):
    device = DeviceService.get(db, device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado")
    return DeviceService.update(db, device, payload)


@router.delete("/{device_id}", response_model=MessageResponse)
def deactivate_device(device_id: int, db: Session = Depends(get_db)):
    device = DeviceService.get(db, device_id)
    if not device:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Equipo no encontrado")
    DeviceService.deactivate(db, device)
    return MessageResponse(message="Equipo desactivado correctamente")
