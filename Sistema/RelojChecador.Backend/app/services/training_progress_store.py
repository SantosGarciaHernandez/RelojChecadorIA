from datetime import datetime
from threading import Lock
from typing import Any


class TrainingProgressStore:
    def __init__(self) -> None:
        self._lock = Lock()
        self._states: dict[str, dict[str, Any]] = {}

    def start(self, job_id: str, message: str = "Preparando entrenamiento...") -> dict[str, Any]:
        return self.update(
            job_id=job_id,
            status="running",
            percent=0,
            step="started",
            message=message,
        )

    def update(
        self,
        job_id: str,
        *,
        status: str = "running",
        percent: int | float | None = None,
        step: str | None = None,
        message: str | None = None,
        extra: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        with self._lock:
            previous = self._states.get(job_id, {})
            version = int(previous.get("version", 0)) + 1
            state = {
                "event_type": "training_progress",
                "job_id": job_id,
                "status": status,
                "percent": max(0, min(100, int(percent if percent is not None else previous.get("percent", 0)))),
                "step": step or previous.get("step") or "running",
                "message": message or previous.get("message") or "Entrenamiento en proceso...",
                "updated_at": datetime.now().isoformat(),
                "version": version,
                "extra": extra or previous.get("extra") or {},
            }
            self._states[job_id] = state
            return dict(state)

    def complete(self, job_id: str, message: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.update(
            job_id=job_id,
            status="completed",
            percent=100,
            step="completed",
            message=message,
            extra=extra,
        )

    def fail(self, job_id: str, message: str, extra: dict[str, Any] | None = None) -> dict[str, Any]:
        return self.update(
            job_id=job_id,
            status="failed",
            percent=100,
            step="failed",
            message=message,
            extra=extra,
        )

    def get(self, job_id: str) -> dict[str, Any] | None:
        with self._lock:
            state = self._states.get(job_id)
            return dict(state) if state else None


training_progress_store = TrainingProgressStore()
