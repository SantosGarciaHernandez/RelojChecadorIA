from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.schemas.dashboard_schema import DashboardSummary, IntrudersByDayItem, RecordsByHourItem
from app.services.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummary)
def summary(db: Session = Depends(get_db)):
    return DashboardService.summary(db)


@router.get("/records-by-hour", response_model=list[RecordsByHourItem])
def records_by_hour(db: Session = Depends(get_db)):
    return DashboardService.records_by_hour(db)


@router.get("/intruders-by-day", response_model=list[IntrudersByDayItem])
def intruders_by_day(days: int = Query(default=7, ge=1, le=30), db: Session = Depends(get_db)):
    return DashboardService.intruders_by_day(db, days=days)
