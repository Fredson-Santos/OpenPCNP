from typing import Optional, List
from pydantic import BaseModel, ConfigDict

class StatsResponse(BaseModel):
    total_licitacoes: int
    valor_total: float
    orgaos_ativos: int

    model_config = ConfigDict(from_attributes=True)

class RankingOrgao(BaseModel):
    orgao_id: str
    nome: str
    total_licitacoes: int

    model_config = ConfigDict(from_attributes=True)

class RankingEstado(BaseModel):
    uf: str
    total_licitacoes: int

    model_config = ConfigDict(from_attributes=True)

class RankingModalidade(BaseModel):
    modalidade: str
    total_licitacoes: int

    model_config = ConfigDict(from_attributes=True)

class RankingLicitacao(BaseModel):
    licitacao_id: str
    objeto: str
    valor_estimado: float
    orgao_nome: str

    model_config = ConfigDict(from_attributes=True)

class StatsRankingResponse(BaseModel):
    ranking_orgaos: List[RankingOrgao]
    ranking_estados: List[RankingEstado]
    ranking_modalidades: List[RankingModalidade]

class EvolucaoMensalResponse(BaseModel):
    mes: str
    quantidade: int

    model_config = ConfigDict(from_attributes=True)
