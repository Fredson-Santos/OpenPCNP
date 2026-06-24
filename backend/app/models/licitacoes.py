import uuid
from app.core.database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Index, text, Uuid
from sqlalchemy.orm import relationship

class Licitacao(Base):
    __tablename__ = 'licitacoes'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    orgao_id = Column(Uuid(as_uuid=True), ForeignKey('orgaos.id'), nullable=False)
    numero_controle = Column(String(100), unique=True, index=True)
    objeto = Column(Text, nullable=False)
    modalidade = Column(String(100))
    situacao = Column(String(100))
    valor_estimado = Column(Float)
    data_publicacao = Column(DateTime)
    data_encerramento = Column(DateTime)

    orgao = relationship("Orgao", back_populates="licitacoes")
    itens = relationship("ItemLicitacao", back_populates="licitacao", cascade="all, delete-orphan")
    arquivos = relationship("ArquivoLicitacao", back_populates="licitacao", cascade="all, delete-orphan")
    fases = relationship("FaseLicitacao", back_populates="licitacao", cascade="all, delete-orphan")

    __table_args__ = (
        Index(
            'ix_licitacoes_objeto_fts',
            text("to_tsvector('portuguese', objeto)"),
            postgresql_using='gin'
        ),
    )

class ItemLicitacao(Base):
    __tablename__ = 'itens_licitacao'
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    licitacao_id = Column(Uuid(as_uuid=True), ForeignKey('licitacoes.id'), nullable=False)
    descricao = Column(Text, nullable=False)
    quantidade = Column(Float, nullable=False)
    valor_unitario = Column(Float)
    valor_total = Column(Float)

    licitacao = relationship("Licitacao", back_populates="itens")

class ArquivoLicitacao(Base):
    __tablename__ = 'arquivos_licitacao'
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    licitacao_id = Column(Uuid(as_uuid=True), ForeignKey('licitacoes.id'), nullable=False)
    nome = Column(String(255), nullable=False)
    url = Column(Text, nullable=False)
    tipo = Column(String(100))

    licitacao = relationship("Licitacao", back_populates="arquivos")

class FaseLicitacao(Base):
    __tablename__ = 'fases_licitacao'
    
    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    licitacao_id = Column(Uuid(as_uuid=True), ForeignKey('licitacoes.id'), nullable=False)
    data = Column(DateTime, nullable=False)
    descricao = Column(String(255), nullable=False)
    status = Column(String(100))

    licitacao = relationship("Licitacao", back_populates="fases")