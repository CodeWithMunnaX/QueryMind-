"""GET /api/schema and GET /api/datasets — dynamic schema and dataset metadata."""
from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.connection import get_db
from app.schemas.analytics import DatabaseSchema, Dataset
from app.services import schema_service
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api", tags=["schema"], dependencies=[Depends(get_current_user)])


@router.get("/schema", response_model=DatabaseSchema)
def get_schema() -> DatabaseSchema:
    return schema_service.get_schema_response()


@router.get("/datasets", response_model=list[Dataset])
def get_datasets(db: Session = Depends(get_db)) -> list[Dataset]:
    settings = get_settings()
    count = db.execute(text(f"SELECT COUNT(*) FROM {settings.allowed_table}")).scalar_one()
    return [
        Dataset(
            id="sales",
            name="Superstore Sales",
            description="Order-level retail sales transactions with customer, product, and geography detail.",
            table_name=settings.allowed_table,
            row_count=count,
        )
    ]
