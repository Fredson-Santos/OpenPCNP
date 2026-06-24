from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Any, Optional, List
from datetime import datetime

from app.core.database import get_db
from app.crud import licitacoes as crud_licitacoes
from app.schemas.licitacoes import (
    LicitacaoResponse, PaginatedLicitacaoResponse, 
    ItemLicitacaoResponse, ArquivoLicitacaoResponse, FaseLicitacaoResponse
)

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
    valor_minimo: Optional[float] = Query(None, description="Filtrar por valor estimado mínimo"),
    valor_maximo: Optional[float] = Query(None, description="Filtrar por valor estimado máximo"),
    data_inicio: Optional[datetime] = Query(None, description="Filtrar publicações a partir desta data"),
    data_fim: Optional[datetime] = Query(None, description="Filtrar publicações até esta data"),
    sort: Optional[str] = Query(None, description="Ordenação (ex: data_publicacao_desc, valor_desc)")
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
        valor_minimo=valor_minimo,
        valor_maximo=valor_maximo,
        data_inicio=data_inicio,
        data_fim=data_fim,
        sort=sort
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

@router.get("/{licitacao_id}/itens", response_model=List[ItemLicitacaoResponse])
def read_licitacao_itens(
    licitacao_id: UUID,
    db: Session = Depends(get_db)
) -> Any:
    """
    Recupera os itens de uma licitação específica.
    """
    return crud_licitacoes.get_itens(db, licitacao_id=licitacao_id)

@router.get("/{licitacao_id}/arquivos", response_model=List[ArquivoLicitacaoResponse])
def read_licitacao_arquivos(
    licitacao_id: UUID,
    db: Session = Depends(get_db)
) -> Any:
    """
    Recupera os arquivos anexos de uma licitação específica.
    """
    return crud_licitacoes.get_arquivos(db, licitacao_id=licitacao_id)

@router.get("/{licitacao_id}/historico", response_model=List[FaseLicitacaoResponse])
def read_licitacao_historico(
    licitacao_id: UUID,
    db: Session = Depends(get_db)
) -> Any:
    """
    Recupera o histórico de fases de uma licitação específica.
    """
    return crud_licitacoes.get_fases(db, licitacao_id=licitacao_id)
