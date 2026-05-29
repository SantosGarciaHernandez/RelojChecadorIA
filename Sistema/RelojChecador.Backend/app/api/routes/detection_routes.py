from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.detection_schema import DetectionFrameRequest, DetectionResponse
from app.services.detection_service import detection_service

router = APIRouter(prefix="/detection", tags=["Detección"])


@router.post("/predict", response_model=DetectionResponse)
def predict_face_crop_base64(payload: DetectionFrameRequest, db: Session = Depends(get_db)):
    """Predice usando una cara ya recortada enviada en base64."""
    try:
        return detection_service.process_base64_frame(db, payload.pc_name, payload.image_base64)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/predict-file", response_model=DetectionResponse)
async def predict_face_crop_file(
    pc_name: str = Form(..., description="Nombre del equipo configurado en SQL Server"),
    file: UploadFile = File(..., description="Imagen de la cara ya recortada"),
    db: Session = Depends(get_db),
):
    """Predice usando una cara ya recortada subida como archivo. Ideal para probar desde Swagger."""
    try:
        image_bytes = await file.read()
        return detection_service.process_image_bytes(db, pc_name, image_bytes)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc


@router.post("/predict-full-frame-opencv", response_model=DetectionResponse)
def predict_full_frame_opencv(payload: DetectionFrameRequest, db: Session = Depends(get_db)):
    """Fallback para pruebas: recibe frame completo, OpenCV recorta el rostro y luego predice."""
    try:
        return detection_service.process_full_frame_with_opencv(db, payload.pc_name, payload.image_base64)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
