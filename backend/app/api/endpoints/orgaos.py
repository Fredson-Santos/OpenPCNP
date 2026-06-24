from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Any

from app.core.database import get_db
from app.crud import orgaos as crud_orgaos
from app.schemas.orgaos import OrgaoResponse, OrgaosResponse

router = APIRouter()

@router.get("/", response_model=OrgaosResponse)
def read_orgaos(
    db: Session = Depends(get_db),
    page: int = Query(1, ge=1, description="Número da página"),
    page_size: int = Query(10, ge=1, le=100, description="Itens por página")
) -> Any:
    """
    Recupera lista de órgãos paginada.
    """
    skip = (page - 1) * page_size
    total, items = crud_orgaos.get_orgaos(db, skip=skip, limit=page_size)
    return {"data": items}

@router.get("/{orgao_id}", response_model=OrgaoResponse)
def read_orgao(
    orgao_id: UUID,
    db: Session = Depends(get_db)
) -> Any:
    """
    Recupera um órgão específico pelo ID.
    """
    orgao = crud_orgaos.get_orgao(db, orgao_id=orgao_id)
    if not orgao:
        raise HTTPException(status_code=404, detail="Órgão não encontrado")
    return orgao
