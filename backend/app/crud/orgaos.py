from sqlalchemy.orm import Session
from uuid import UUID
from app.models.orgaos import Orgao

def get_orgao(db: Session, orgao_id: UUID):
    return db.query(Orgao).filter(Orgao.id == orgao_id).first()

def get_orgaos(db: Session, skip: int = 0, limit: int = 10):
    total = db.query(Orgao).count()
    items = db.query(Orgao).offset(skip).limit(limit).all()
    return total, items

def autocomplete_orgaos(db: Session, q: str, limit: int = 10):
    query = db.query(Orgao.id, Orgao.nome)
    if q:
        query = query.filter(Orgao.nome.ilike(f"%{q}%"))
    return query.limit(limit).all()
