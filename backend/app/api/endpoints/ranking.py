from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Any, List

from app.core.database import get_db
from app.crud import stats as crud_stats
from app.schemas.stats import RankingOrgao, RankingEstado, RankingModalidade, RankingLicitacao

router = APIRouter()

@router.get("/orgaos", response_model=List[RankingOrgao])
def get_ranking_orgaos(
    db: Session = Depends(get_db),
    limit: int = Query(10, description="Limite de registros para o ranking")
) -> Any:
    """
    Recupera o ranking dos órgãos com mais licitações.
    """
    return crud_stats.get_ranking_orgaos(db, limit=limit)

@router.get("/estados", response_model=List[RankingEstado])
def get_ranking_estados(
    db: Session = Depends(get_db),
    limit: int = Query(10, description="Limite de registros para o ranking")
) -> Any:
    """
    Recupera o ranking dos estados (UF) com mais licitações.
    """
    return crud_stats.get_ranking_estados(db, limit=limit)

@router.get("/modalidades", response_model=List[RankingModalidade])
def get_ranking_modalidades(
    db: Session = Depends(get_db),
    limit: int = Query(10, description="Limite de registros para o ranking")
) -> Any:
    """
    Recupera o ranking das modalidades mais utilizadas.
    """
    return crud_stats.get_ranking_modalidades(db, limit=limit)

@router.get("/licitacoes", response_model=List[RankingLicitacao])
def get_ranking_licitacoes(
    db: Session = Depends(get_db),
    limit: int = Query(10, description="Limite de registros para o ranking")
) -> Any:
    """
    Recupera o ranking das licitações com maior valor estimado.
    """
    return crud_stats.get_ranking_licitacoes(db, limit=limit)
