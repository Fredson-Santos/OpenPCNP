from sqlalchemy.orm import Session
from sqlalchemy import func, desc, text
from app.models.licitacoes import Licitacao
from app.models.orgaos import Orgao
from app.models.fornecedores import Fornecedor, Contrato

def get_general_stats(db: Session):
    total_licitacoes = db.query(func.count(Licitacao.id)).scalar() or 0
    valor_total = db.query(func.sum(Licitacao.valor_estimado)).filter(Licitacao.valor_estimado < 10000000000).scalar() or 0.0
    orgaos_ativos = db.query(func.count(func.distinct(Licitacao.orgao_id))).scalar() or 0
    ultima_atualizacao = db.query(func.max(Licitacao.data_publicacao)).scalar()

    return {
        "total_licitacoes": total_licitacoes,
        "valor_total": valor_total,
        "orgaos_ativos": orgaos_ativos,
        "ultima_atualizacao": ultima_atualizacao.isoformat() if ultima_atualizacao else None
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
        .filter(Licitacao.valor_estimado.is_not(None), Licitacao.valor_estimado < 10000000000)
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

def get_evolucao_diaria(db: Session):
    # Depending on dialect, we extract month/year.
    if db.bind.dialect.name == 'postgresql':
        query = db.query(
            func.to_char(Licitacao.data_publicacao, 'YYYY-MM-DD').label("data"),
            func.count(Licitacao.id).label("quantidade")
        ).group_by(text("data")).order_by(text("data")).all()
    else:
        # SQLite fallback
        query = db.query(
            func.strftime('%Y-%m-%d', Licitacao.data_publicacao).label("data"),
            func.count(Licitacao.id).label("quantidade")
        ).group_by(text("data")).order_by(text("data")).all()

    return [{"data": r.data, "quantidade": r.quantidade} for r in query if r.data]

def get_ranking_fornecedores_vencedores(db: Session, limit: int = 10):
    ranking = (
        db.query(
            Fornecedor.id.label("fornecedor_id"),
            Fornecedor.nome,
            Fornecedor.ni,
            func.count(Contrato.id).label("quantidade_vitorias")
        )
        .join(Contrato, Fornecedor.id == Contrato.fornecedor_id)
        .group_by(Fornecedor.id)
        .order_by(desc("quantidade_vitorias"))
        .limit(limit)
        .all()
    )
    return [
        {
            "fornecedor_id": str(r.fornecedor_id),
            "nome": r.nome,
            "ni": r.ni,
            "quantidade_vitorias": r.quantidade_vitorias
        }
        for r in ranking
    ]

def get_ranking_fornecedores_volume(db: Session, limit: int = 10):
    ranking = (
        db.query(
            Fornecedor.id.label("fornecedor_id"),
            Fornecedor.nome,
            Fornecedor.ni,
            func.sum(Contrato.valor_contrato).label("volume_total"),
            func.count(Contrato.id).label("quantidade_contratos")
        )
        .join(Contrato, Fornecedor.id == Contrato.fornecedor_id)
        .filter(Contrato.valor_contrato < 10000000000)
        .group_by(Fornecedor.id)
        .order_by(desc("volume_total"))
        .limit(limit)
        .all()
    )
    return [
        {
            "fornecedor_id": str(r.fornecedor_id),
            "nome": r.nome,
            "ni": r.ni,
            "volume_total": float(r.volume_total or 0.0),
            "quantidade_contratos": r.quantidade_contratos
        }
        for r in ranking
    ]

def get_distribuicao_contratos_orgao(db: Session, limit: int = 10):
    distribuicao = (
        db.query(
            Orgao.id.label("orgao_id"),
            Orgao.nome.label("orgao_nome"),
            func.count(Contrato.id).label("quantidade_contratos"),
            func.sum(Contrato.valor_contrato).label("volume_total")
        )
        .select_from(Orgao)
        .join(Licitacao, Orgao.id == Licitacao.orgao_id)
        .join(Contrato, Licitacao.id == Contrato.licitacao_id)
        .filter(Contrato.valor_contrato < 10000000000)
        .group_by(Orgao.id)
        .order_by(desc("volume_total"))
        .limit(limit)
        .all()
    )
    return [
        {
            "orgao_id": str(r.orgao_id),
            "orgao_nome": r.orgao_nome,
            "quantidade_contratos": r.quantidade_contratos,
            "volume_total": float(r.volume_total or 0.0)
        }
        for r in distribuicao
    ]
