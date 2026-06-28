from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Any, List

from app.core.database import get_db
from app.crud import stats as crud_stats
from app.schemas.stats import StatsResponse, EvolucaoDiariaResponse, DistribuicaoContratosOrgao
from fastapi_cache.decorator import cache
from fastapi import Query

router = APIRouter()

@router.get("/evolucao-diaria", response_model=List[EvolucaoDiariaResponse])
@cache(expire=3600)
def get_evolucao_diaria(db: Session = Depends(get_db)) -> Any:
    """
    Recupera a evolução diária da quantidade de licitações publicadas.
    """
    return crud_stats.get_evolucao_diaria(db)

@router.get("/distribuicao-contratos", response_model=List[DistribuicaoContratosOrgao])
@cache(expire=3600)
def get_distribuicao_contratos_orgao(
    db: Session = Depends(get_db),
    limit: int = Query(10, description="Limite de registros para o ranking")
) -> Any:
    """
    Recupera a distribuição de contratos e volume total por órgão.
    """
    return crud_stats.get_distribuicao_contratos_orgao(db, limit=limit)

@router.get("/", response_model=StatsResponse)
@cache(expire=3600)
def get_general_stats(db: Session = Depends(get_db)) -> Any:
    """
    Recupera estatísticas gerais: total de licitações, valor total e órgãos ativos.
    """
    stats = crud_stats.get_general_stats(db)
    return stats
