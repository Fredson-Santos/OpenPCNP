import uuid
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from .orgaos import OrgaoResponse

class LicitacaoResponse(BaseModel):
    id: uuid.UUID
    orgao_id: uuid.UUID
    orgao: Optional[OrgaoResponse] = None
    numero_controle: Optional[str] = None
    objeto: str
    modalidade: Optional[str] = None
    situacao: Optional[str] = None
    valor_estimado: Optional[float] = None
    data_publicacao: Optional[datetime] = None
    data_encerramento: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class LicitacoesResponse(BaseModel):
    data: List[LicitacaoResponse]

class PaginatedLicitacaoResponse(BaseModel):
    data: List[LicitacaoResponse]
    page: int
    total: int
    page_size: int