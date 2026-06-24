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

    __table_args__ = (
        Index(
            'ix_licitacoes_objeto_fts',
            text("to_tsvector('portuguese', objeto)"),
            postgresql_using='gin'
        ),
    )