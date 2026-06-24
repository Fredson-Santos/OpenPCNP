from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
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

def get_ranking_licitacoes(db: Session, limit: int = 10):
    ranking = (
        db.query(
            Licitacao.id.label("licitacao_id"),
            Licitacao.objeto,
            Licitacao.valor_estimado,
            Orgao.nome.label("orgao_nome")
        )
        .join(Orgao, Orgao.id == Licitacao.orgao_id)
        .filter(Licitacao.valor_estimado.is_not(None))
        .order_by(desc(Licitacao.valor_estimado))
        .limit(limit)
        .all()
    )
    return [
        {
            "licitacao_id": str(r.licitacao_id),
            "objeto": r.objeto,
            "valor_estimado": r.valor_estimado,
            "orgao_nome": r.orgao_nome
        }
        for r in ranking
    ]

def get_evolucao_mensal(db: Session):
    # Depending on dialect, we extract month/year.
    if db.bind.dialect.name == 'postgresql':
        query = db.query(
            func.to_char(Licitacao.data_publicacao, 'YYYY-MM').label("mes"),
            func.count(Licitacao.id).label("quantidade")
        ).group_by(text("mes")).order_by(text("mes")).all()
    else:
        # SQLite fallback
        query = db.query(
            func.strftime('%Y-%m', Licitacao.data_publicacao).label("mes"),
            func.count(Licitacao.id).label("quantidade")
        ).group_by(text("mes")).order_by(text("mes")).all()

    return [{"mes": r.mes, "quantidade": r.quantidade} for r in query if r.mes]
