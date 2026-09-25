"""GET /api/dashboard — aggregate KPI cards and chart feeds, computed live from PostgreSQL."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.analytics import DashboardResponse
from app.services.analytics_service import get_dashboard_metrics
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api", tags=["dashboard"], dependencies=[Depends(get_current_user)])


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db)) -> DashboardResponse:
    try:
        return get_dashboard_metrics(db)
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=503, detail="Could not load dashboard metrics from the database.") from exc
