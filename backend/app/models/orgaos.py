import uuid
from app.core.database import Base
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Index, text, Uuid
from sqlalchemy.orm import relationship

class Orgao(Base):
    __tablename__ = 'orgaos'

    id = Column(Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    cnpj = Column(String(14), unique=True, index=True)
    nome = Column(String(255), nullable=False)
    esfera = Column(String(50))
    uf = Column(String(2))

    licitacoes = relationship("Licitacao", back_populates="orgao")