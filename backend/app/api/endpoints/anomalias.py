from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Any, List

from app.core.database import get_db
from app.crud import anomalias as crud_anomalias
from app.schemas.anomalias import AnomaliaValor, AnomaliaPrazo, AnomaliaFornecedorRecorrente
from fastapi_cache.decorator import cache

router = APIRouter()

@router.get("/valor-acima-media", response_model=List[AnomaliaValor])
@cache(expire=3600)
def get_anomalias_valor(
    db: Session = Depends(get_db),
    fator: float = Query(3.0, description="Fator multiplicador acima da média"),
    limit: int = Query(20, description="Limite de registros")
) -> Any:
    """
    Detecta licitações com valor estimado muito acima da média da modalidade.
    """
    return crud_anomalias.get_anomalias_valor(db, limite_fator=fator, limit=limit)

@router.get("/prazo-atipico", response_model=List[AnomaliaPrazo])
@cache(expire=3600)
def get_anomalias_prazo(
    db: Session = Depends(get_db),
    dias: int = Query(5, description="Número máximo de dias para ser considerado atípico"),
    limit: int = Query(20, description="Limite de registros")
) -> Any:
    """
    Detecta licitações cujo prazo entre publicação e encerramento é suspeitamente curto.
    """
    return crud_anomalias.get_anomalias_prazo(db, limite_dias=dias, limit=limit)

@router.get("/fornecedor-recorrente", response_model=List[AnomaliaFornecedorRecorrente])
@cache(expire=3600)
def get_anomalias_fornecedor(
    db: Session = Depends(get_db),
    min_vitorias: int = Query(3, description="Mínimo de contratos para alerta"),
    limit: int = Query(20, description="Limite de registros")
) -> Any:
    """
    Detecta fornecedores que ganham muitas licitações (possível favorecimento).
    """
    return crud_anomalias.get_anomalias_fornecedor_recorrente(db, min_vitorias=min_vitorias, limit=limit)
