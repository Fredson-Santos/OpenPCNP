from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any, List

from app.core.database import get_db
from app.crud import stats as crud_stats
from app.schemas.stats import StatsResponse, EvolucaoMensalResponse

router = APIRouter()

@router.get("/evolucao-mensal", response_model=List[EvolucaoMensalResponse])
def get_evolucao_mensal(db: Session = Depends(get_db)) -> Any:
    """
    Recupera a evolução mensal da quantidade de licitações publicadas.
    """
    return crud_stats.get_evolucao_mensal(db)

@router.get("/", response_model=StatsResponse)
def get_general_stats(db: Session = Depends(get_db)) -> Any:
    """
    Recupera estatísticas gerais: total de licitações, valor total e órgãos ativos.
    """
    stats = crud_stats.get_general_stats(db)
    return stats
