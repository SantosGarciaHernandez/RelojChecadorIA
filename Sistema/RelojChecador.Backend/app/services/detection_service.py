from datetime import datetime

from sqlalchemy.orm import Session

from app.ml.face_detection_service import FaceDetectionService
from app.ml.face_recognition_service import FaceRecognitionService
from app.ml.image_preprocessing import decode_base64_image, decode_image_bytes, image_to_jpeg_bytes
from app.models.device_model import Equipo
from app.models.user_model import Usuario
from app.schemas.detection_schema import DetectionResponse
from app.services.attendance_service import AttendanceService
from app.services.config_service import ConfigService
from app.services.device_service import DeviceService
from app.services.intruder_alert_service import IntruderAlertService
from app.services.notification_service import NotificationService
from app.services.user_service import UserService
from app.core.config import get_settings


class DetectionService:
    def __init__(self) -> None:
        self._face_detector: FaceDetectionService | None = None
        self._face_recognizer: FaceRecognitionService | None = None
        # Memoria simple por instancia para exigir N detecciones consecutivas
        # antes de intentar guardar un registro de entrada/salida.
        self._validation_streaks: dict[str, dict] = {}

    @property
    def face_detector(self) -> FaceDetectionService:
        if self._face_detector is None:
            self._face_detector = FaceDetectionService()
        return self._face_detector

    @property
    def face_recognizer(self) -> FaceRecognitionService:
        if self._face_recognizer is None:
            self._face_recognizer = FaceRecognitionService()
        return self._face_recognizer

    def reload_face_recognizer(self) -> None:
        """Recarga el modelo y labels en la siguiente predicción."""
        self._face_recognizer = None

    def _resolve_user(
        self,
        db: Session,
        user_id: int | None,
        employee_number: str | None,
        name: str | None,
        model_label: str | None,
    ) -> Usuario | None:
        if user_id is not None:
            user = db.get(Usuario, user_id)
            if user and user.activo:
                return user

        if employee_number:
            user = UserService.get_by_employee_or_email(db, employee_number)
            if user and user.activo:
                return user

        # Este es el enlace principal para tu labels.json actual: SantosSet, NaomiSet, CotoSet, etc.
        if model_label:
            user = UserService.get_by_model_label(db, model_label)
            if user and user.activo:
                return user

        # Fallback para labels que ya vengan con el nombre completo.
        if name:
            user = UserService.get_by_name(db, name)
            if user and user.activo:
                return user

        return None

    def _reset_validation_streak(self, pc_name: str) -> None:
        self._validation_streaks.pop(pc_name, None)

    def _validate_consecutive_detection(
        self,
        pc_name: str,
        user: Usuario,
        device: Equipo,
        confidence: float,
        prediction_extra: dict,
    ) -> DetectionResponse | None:
        """
        Exige varias detecciones consecutivas iguales antes de registrar.

        Regresa None cuando ya se alcanzó el mínimo y se puede registrar.
        Regresa DetectionResponse cuando todavía falta validación.
        """
        settings = get_settings()
        required = max(1, int(settings.attendance_required_consecutive_validations))

        if required <= 1:
            return None

        validation_key = f"{pc_name}|{device.accion}|{user.id_usuario}"
        current = self._validation_streaks.get(pc_name)

        if current and current.get("key") == validation_key:
            count = int(current.get("count", 0)) + 1
        else:
            count = 1

        self._validation_streaks[pc_name] = {
            "key": validation_key,
            "count": count,
            "user_id": user.id_usuario,
            "device_action": device.accion,
            "updated_at": datetime.now(),
        }

        if count < required:
            now = datetime.now()
            extra = {
                **prediction_extra,
                "validation_required": required,
                "validation_count": count,
                "validation_remaining": required - count,
                "validation_key": validation_key,
            }
            return DetectionResponse(
                event_type="validation_pending",
                recognized=True,
                user_id=user.id_usuario,
                employee_number=user.numero_empleado,
                name=user.nombre,
                record_type=device.accion,
                confidence=confidence,
                timestamp=now.isoformat(),
                message=f"Validación {count}/{required} confirmada para {user.nombre}. Mantente frente a la cámara.",
                reason="Se requieren detecciones consecutivas antes de registrar entrada/salida",
                extra=extra,
            )

        return None

    def _register_intruder(
        self,
        db: Session,
        device: Equipo,
        confidence: float,
        frame_bytes: bytes,
        message: str = "Intruso detectado",
        extra: dict | None = None,
    ) -> DetectionResponse:
        alert = IntruderAlertService.create_alert(
            db=db,
            device=device,
            confidence=confidence,
            image_bytes=frame_bytes,
            message=message,
        )
        config = ConfigService.get_or_create(db)
        if config.correos_activos:
            try:
                NotificationService.send_intruder_alert(db, alert)
            except Exception:
                # No se debe romper el registro de intruso si falla el correo.
                pass

        return DetectionResponse(
            event_type="intruder_detected",
            recognized=False,
            confidence=confidence,
            timestamp=alert.fecha_hora.isoformat(),
            message=message,
            extra={"id_intruso": alert.id_intruso, "estado_alerta": alert.estado_alerta, **(extra or {})},
        )

    def _process_face_crop(self, db: Session, pc_name: str, face_crop) -> DetectionResponse:
        device = DeviceService.get_active_by_name(db, pc_name)
        if not device:
            self._reset_validation_streak(pc_name)
            return DetectionResponse(
                event_type="device_not_found",
                message="El equipo no existe o está inactivo",
                reason="Configura el equipo desde el panel administrativo",
            )

        face_bytes = image_to_jpeg_bytes(face_crop)
        config = ConfigService.get_or_create(db)
        prediction = self.face_recognizer.predict(face_crop, threshold=config.umbral_confianza_intruso)

        prediction_extra = {
            "class_index": prediction.class_index,
            "model_label": prediction.model_label,
            "raw_label": prediction.raw_label,
            "probabilities": prediction.probabilities,
            "input_type": "face_crop",
        }

        if prediction.is_intruder_label:
            self._reset_validation_streak(pc_name)
            return self._register_intruder(
                db=db,
                device=device,
                confidence=prediction.confidence,
                frame_bytes=face_bytes,
                message="El modelo clasificó la imagen como Intruso",
                extra=prediction_extra,
            )

        if not prediction.recognized:
            self._reset_validation_streak(pc_name)
            return self._register_intruder(
                db=db,
                device=device,
                confidence=prediction.confidence,
                frame_bytes=face_bytes,
                message="Intruso detectado por confianza menor al umbral",
                extra=prediction_extra,
            )

        user = self._resolve_user(
            db=db,
            user_id=prediction.user_id,
            employee_number=prediction.employee_number,
            name=prediction.name,
            model_label=prediction.model_label,
        )
        if not user:
            self._reset_validation_streak(pc_name)
            return self._register_intruder(
                db=db,
                device=device,
                confidence=prediction.confidence,
                frame_bytes=face_bytes,
                message="Etiqueta reconocida, pero no existe usuario activo relacionado en SQL Server",
                extra=prediction_extra,
            )

        pending_validation = self._validate_consecutive_detection(
            pc_name=pc_name,
            user=user,
            device=device,
            confidence=prediction.confidence,
            prediction_extra=prediction_extra,
        )
        if pending_validation is not None:
            return pending_validation

        result = AttendanceService.register_attendance(
            db=db,
            user=user,
            device=device,
            confidence=prediction.confidence,
            config=config,
        )
        # Después de intentar registrar, se reinicia para exigir nuevamente 3 lecturas
        # antes de otro intento. La regla anti-duplicados sigue activa en AttendanceService.
        self._reset_validation_streak(pc_name)

        timestamp = result.record.fecha_hora if result.record else datetime.now()
        return DetectionResponse(
            event_type=result.event_type,
            recognized=True,
            user_id=user.id_usuario,
            employee_number=user.numero_empleado,
            name=user.nombre,
            record_type=device.accion,
            confidence=prediction.confidence,
            timestamp=timestamp.isoformat(),
            message=result.message,
            reason=result.reason,
            extra=prediction_extra,
        )

    def process_image_bytes(self, db: Session, pc_name: str, image_bytes: bytes) -> DetectionResponse:
        """Procesa una imagen recibida como archivo. Debe ser una cara recortada."""
        face_crop = decode_image_bytes(image_bytes)
        return self._process_face_crop(db, pc_name, face_crop)

    def process_base64_frame(self, db: Session, pc_name: str, image_base64: str) -> DetectionResponse:
        """Procesa una imagen base64. Debe ser una cara recortada enviada por el frontend."""
        face_crop = decode_base64_image(image_base64)
        return self._process_face_crop(db, pc_name, face_crop)

    def process_full_frame_with_opencv(self, db: Session, pc_name: str, image_base64: str) -> DetectionResponse:
        """
        Fallback opcional para pruebas locales: recibe frame completo, detecta rostro con OpenCV y predice.
        El flujo principal del proyecto debe usar process_base64_frame/process_image_bytes con cara recortada.
        """
        frame = decode_base64_image(image_base64)
        frame_bytes = image_to_jpeg_bytes(frame)
        detected_face = self.face_detector.extract_largest_face(frame)

        device = DeviceService.get_active_by_name(db, pc_name)
        if not device:
            self._reset_validation_streak(pc_name)
            return DetectionResponse(
                event_type="device_not_found",
                message="El equipo no existe o está inactivo",
                reason="Configura el equipo desde el panel administrativo",
            )

        if not detected_face:
            self._reset_validation_streak(pc_name)
            return DetectionResponse(
                event_type="no_face_detected",
                recognized=False,
                message="No se detectó rostro en el frame completo",
            )

        face, bounding_box = detected_face
        response = self._process_face_crop(db, pc_name, face)
        response.extra["input_type"] = "full_frame_opencv"
        response.extra["bounding_box"] = bounding_box
        if response.event_type == "intruder_detected":
            # En frame completo conviene guardar la evidencia completa, no solo el crop.
            response.extra["saved_image_note"] = "La evidencia original del frame completo no reemplaza el registro ya creado."
        return response


# Instancia singleton para no recargar detector/modelo en cada request.
detection_service = DetectionService()
