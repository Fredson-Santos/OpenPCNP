from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any

from app.core.database import get_db
from app.crud import stats as crud_stats
from app.schemas.stats import StatsResponse

router = APIRouter()

@router.get("/", response_model=StatsResponse)
def get_general_stats(db: Session = Depends(get_db)) -> Any:
    """
    Recupera estatísticas gerais: total de licitações, valor total e órgãos ativos.
    """
    stats = crud_stats.get_general_stats(db)
    return stats
