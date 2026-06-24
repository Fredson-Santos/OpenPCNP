from sqlalchemy.orm import Session
from sqlalchemy import text, or_
from uuid import UUID
from app.models.licitacoes import Licitacao
from app.models.orgaos import Orgao

def get_licitacao(db: Session, licitacao_id: UUID):
    return db.query(Licitacao).filter(Licitacao.id == licitacao_id).first()

def get_licitacoes(
    db: Session, 
    skip: int = 0, 
    limit: int = 10,
    q: str = None,
    uf: str = None,
    modalidade: str = None,
    situacao: str = None,
    valor: float = None
):
    query = db.query(Licitacao).join(Orgao)

    if q:
        # Check dialect to avoid breaking SQLite in tests
        if db.bind.dialect.name == 'postgresql':
            query = query.filter(
                text("to_tsvector('portuguese', licitacoes.objeto) @@ plainto_tsquery('portuguese', :q)")
            ).params(q=q)
        else:
            # Fallback for SQLite in tests
            query = query.filter(Licitacao.objeto.ilike(f"%{q}%"))

    if uf:
        query = query.filter(Orgao.uf == uf)
    if modalidade:
        query = query.filter(Licitacao.modalidade == modalidade)
    if situacao:
        query = query.filter(Licitacao.situacao == situacao)
    if valor is not None:
        query = query.filter(Licitacao.valor_estimado >= valor)

    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return total, items