from typing import Optional, List
from uuid import UUID
from datetime import date
from pydantic import BaseModel

class FornecedorBase(BaseModel):
    ni: str
    nome: str
    tipo: Optional[str] = None
    uf: Optional[str] = None
    porte: Optional[str] = None

class FornecedorCreate(FornecedorBase):
    pass

class Fornecedor(FornecedorBase):
    id: UUID

    class Config:
        from_attributes = True

class ContratoBase(BaseModel):
    numero: Optional[str] = None
    objeto: Optional[str] = None
    valor_contrato: float
    data_assinatura: Optional[date] = None
    vigencia_inicio: Optional[date] = None
    vigencia_fim: Optional[date] = None

class ContratoCreate(ContratoBase):
    licitacao_id: UUID
    fornecedor_id: UUID

class Contrato(ContratoBase):
    id: UUID
    licitacao_id: UUID
    fornecedor_id: UUID
    fornecedor: Optional[Fornecedor] = None

    class Config:
        from_attributes = True

class FornecedorRankingVolume(BaseModel):
    fornecedor_id: UUID
    nome: str
    ni: str
    volume_total: float
    quantidade_contratos: int

class FornecedorRankingVencedor(BaseModel):
    fornecedor_id: UUID
    nome: str
    ni: str
    quantidade_vitorias: int
