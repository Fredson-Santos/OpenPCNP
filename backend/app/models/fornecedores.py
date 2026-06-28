import uuid
from app.core.database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Uuid, Date
from sqlalchemy.orm import relationship

class Fornecedor(Base):
    __tablename__ = 'fornecedores'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    ni = Column(String(20), unique=True, index=True, nullable=False) # CNPJ, CPF, etc.
    nome = Column(String(255), nullable=False)
    tipo = Column(String(50)) # PJ, PF, Estrangeiro, etc.
    uf = Column(String(2))
    porte = Column(String(100))

    contratos = relationship("Contrato", back_populates="fornecedor", cascade="all, delete-orphan")

class Contrato(Base):
    __tablename__ = 'contratos'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    licitacao_id = Column(Uuid(as_uuid=True), ForeignKey('licitacoes.id'), nullable=False)
    fornecedor_id = Column(Uuid(as_uuid=True), ForeignKey('fornecedores.id'), nullable=False)
    
    numero = Column(String(100))
    objeto = Column(Text)
    valor_contrato = Column(Float, nullable=False)
    data_assinatura = Column(Date)
    vigencia_inicio = Column(Date)
    vigencia_fim = Column(Date)

    fornecedor = relationship("Fornecedor", back_populates="contratos")
    licitacao = relationship("Licitacao", back_populates="contratos")
