from sqlalchemy.orm import Session
from sqlalchemy import text, or_, desc, asc
from uuid import UUID
from datetime import datetime
from app.models.licitacoes import Licitacao, ItemLicitacao, ArquivoLicitacao, FaseLicitacao
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
    valor_minimo: float = None,
    valor_maximo: float = None,
    data_inicio: datetime = None,
    data_fim: datetime = None,
    sort: str = None
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
    if valor_minimo is not None:
        query = query.filter(Licitacao.valor_estimado >= valor_minimo)
    if valor_maximo is not None:
        query = query.filter(Licitacao.valor_estimado <= valor_maximo)
    if data_inicio:
        query = query.filter(Licitacao.data_publicacao >= data_inicio)
    if data_fim:
        query = query.filter(Licitacao.data_publicacao <= data_fim)

    if sort == "data_publicacao_desc":
        query = query.order_by(desc(Licitacao.data_publicacao))
    elif sort == "data_publicacao_asc":
        query = query.order_by(asc(Licitacao.data_publicacao))
    elif sort == "valor_desc":
        query = query.order_by(desc(Licitacao.valor_estimado))
    elif sort == "valor_asc":
        query = query.order_by(asc(Licitacao.valor_estimado))
    else:
        # Default sort
        query = query.order_by(desc(Licitacao.data_publicacao))

    total = query.count()
    items = query.offset(skip).limit(limit).all()
    
    return total, items

def get_itens(db: Session, licitacao_id: UUID):
    return db.query(ItemLicitacao).filter(ItemLicitacao.licitacao_id == licitacao_id).all()

def get_arquivos(db: Session, licitacao_id: UUID):
    return db.query(ArquivoLicitacao).filter(ArquivoLicitacao.licitacao_id == licitacao_id).all()

def get_fases(db: Session, licitacao_id: UUID):
    return db.query(FaseLicitacao).filter(FaseLicitacao.licitacao_id == licitacao_id).order_by(FaseLicitacao.data).all()