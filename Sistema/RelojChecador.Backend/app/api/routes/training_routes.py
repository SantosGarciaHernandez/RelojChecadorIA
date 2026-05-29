from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.database.session import get_db
from app.schemas.training_schema import TrainingRegisterRequest, TrainingRegisterResponse
from app.schemas.user_schema import UserResponse
from app.services.model_training_service import ModelTrainingService

router = APIRouter(prefix="/training", tags=["Entrenamiento"])


@router.post("/register-user", response_model=TrainingRegisterResponse, status_code=status.HTTP_201_CREATED)
def register_user_with_training(payload: TrainingRegisterRequest, db: Session = Depends(get_db)):
    """
    Registra un usuario solamente si el modelo se reentrena correctamente.

    Flujo esperado:
    1. El frontend captura 320 rostros ya recortados.
    2. El backend guarda 220 en Train y 100 en Validation.
    3. Reentrena el modelo con todo el dataset disponible.
    4. Si el entrenamiento termina bien, actualiza trained_model.keras y labels.json.
    5. Solo entonces crea el usuario en SQL Server.
    """
    service = ModelTrainingService()
    try:
        user, labels = service.register_user_after_successful_training(db, payload)
        settings = get_settings()
        return TrainingRegisterResponse(
            success=True,
            message="Usuario entrenado y guardado correctamente",
            job_id=payload.job_id,
            user=UserResponse.model_validate(user),
            model_labels=labels,
            train_images=settings.training_train_image_count,
            validation_images=settings.training_validation_image_count,
        )
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error durante el entrenamiento: {exc}",
        ) from exc
