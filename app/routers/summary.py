from fastapi import APIRouter

from app.dependencies import Month, SessionDep
from app.schemas.summary import MonthlySummary
from app.services import summary as service

router = APIRouter(prefix="/summary", tags=["Summary"])


@router.get("/{month}", response_model=MonthlySummary, summary="Get the summary of a month")
def get_monthly_summary(month: Month, db: SessionDep) -> MonthlySummary:
    return service.get_monthly_summary(db, month)
