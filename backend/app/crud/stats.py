from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from app.models.licitacoes import Licitacao
from app.models.orgaos import Orgao

def get_general_stats(db: Session):
    total_licitacoes = db.query(func.count(Licitacao.id)).scalar() or 0
    valor_total = db.query(func.sum(Licitacao.valor_estimado)).scalar() or 0.0
    orgaos_ativos = db.query(func.count(func.distinct(Licitacao.orgao_id))).scalar() or 0

    return {
        "total_licitacoes": total_licitacoes,
        "valor_total": valor_total,
        "orgaos_ativos": orgaos_ativos
    }

def get_ranking_orgaos(db: Session, limit: int = 10):
    ranking = (
        db.query(
            Orgao.id.label("orgao_id"), 
            Orgao.nome, 
            func.count(Licitacao.id).label("total_licitacoes")
        )
        .join(Licitacao, Orgao.id == Licitacao.orgao_id)
        .group_by(Orgao.id)
        .order_by(desc("total_licitacoes"))
        .limit(limit)
        .all()
    )
    return [
        {
            "orgao_id": str(r.orgao_id),
            "nome": r.nome,
            "total_licitacoes": r.total_licitacoes
        }
        for r in ranking
    ]

def get_ranking_estados(db: Session, limit: int = 10):
    ranking = (
        db.query(
            Orgao.uf, 
            func.count(Licitacao.id).label("total_licitacoes")
        )
        .join(Licitacao, Orgao.id == Licitacao.orgao_id)
        .group_by(Orgao.uf)
        .order_by(desc("total_licitacoes"))
        .limit(limit)
        .all()
    )
    return [dict(r._mapping) for r in ranking]

def get_ranking_modalidades(db: Session, limit: int = 10):
    ranking = (
        db.query(
            Licitacao.modalidade, 
            func.count(Licitacao.id).label("total_licitacoes")
        )
        .group_by(Licitacao.modalidade)
        .order_by(desc("total_licitacoes"))
        .limit(limit)
        .all()
    )
    return [dict(r._mapping) for r in ranking]
