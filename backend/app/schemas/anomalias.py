from typing import Optional, Any
from uuid import UUID
from pydantic import BaseModel

class AnomaliaBase(BaseModel):
    licitacao_id: UUID
    numero_controle: str
    motivo: str
    detalhes: Optional[Any] = None

class AnomaliaValor(AnomaliaBase):
    valor_estimado: float
    media_categoria: float

class AnomaliaPrazo(AnomaliaBase):
    data_publicacao: str
    data_encerramento: str
    prazo_dias: int

class AnomaliaFornecedorRecorrente(BaseModel):
    fornecedor_id: UUID
    nome: str
    quantidade_vitorias: int
    periodo_dias: int
