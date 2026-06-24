from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Any, Optional

from app.core.database import get_db
from app.crud import licitacoes as crud_licitacoes
from app.schemas.licitacoes import LicitacaoResponse, PaginatedLicitacaoResponse

router = APIRouter()

@router.get("/", response_model=PaginatedLicitacaoResponse)
def read_licitacoes(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página"),
    q: Optional[str] = Query(None, description="Busca Full Text no objeto da licitação"),
    uf: Optional[str] = Query(None, description="Filtrar por UF do órgão"),
    modalidade: Optional[str] = Query(None, description="Filtrar por modalidade"),
    situacao: Optional[str] = Query(None, description="Filtrar por situação"),
    valor: Optional[float] = Query(None, description="Filtrar por valor estimado mínimo")
) -> Any:
    """
    Recupera lista de licitações paginada e com filtros.
    """
    skip = (page - 1) * page_size
    total, items = crud_licitacoes.get_licitacoes(
        db=db,
        skip=skip,
        limit=page_size,
        q=q,
        uf=uf,
        modalidade=modalidade,
        situacao=situacao,
        valor=valor
    )
    return {
        "data": items,
        "page": page,
        "total": total,
        "page_size": page_size
    }

@router.get("/{licitacao_id}", response_model=LicitacaoResponse)
def read_licitacao(
    licitacao_id: UUID,
    db: Session = Depends(get_db)
) -> Any:
    """
    Recupera uma licitação específica pelo ID.
    """
    licitacao = crud_licitacoes.get_licitacao(db, licitacao_id=licitacao_id)
    if not licitacao:
        raise HTTPException(status_code=404, detail="Licitação não encontrada")
    return licitacao
