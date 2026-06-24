import uuid
from app.core.database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Index, text, Uuid
from sqlalchemy.orm import relationship

class Stats(Base):
    __tablename__ = 'stats'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    total_licitacoes = Column(Integer, default=0)
    valor_total = Column(Float, default=0)
    orgaos_ativos = Column(Integer, default=0)

class RankingOrgao(Base):
    __tablename__ = 'ranking_orgao'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    orgao_id = Column(Uuid(as_uuid=True), ForeignKey('orgaos.id'), nullable=False)
    nome = Column(String(255), nullable=False)
    total_licitacoes = Column(Integer, default=0)

class RankingEstado(Base):
    __tablename__ = 'ranking_estado'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    uf = Column(String(2), nullable=False)
    total_licitacoes = Column(Integer, default=0)

class RankingModalidade(Base):
    __tablename__ = 'ranking_modalidade'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    modalidade = Column(String(100), nullable=False)
    total_licitacoes = Column(Integer, default=0)
