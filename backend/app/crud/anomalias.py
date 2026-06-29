from sqlalchemy.orm import Session
from sqlalchemy import func, text, desc
from app.models.licitacoes import Licitacao
from app.models.fornecedores import Contrato, Fornecedor

from datetime import datetime, timedelta

def get_anomalias_valor(db: Session, limite_fator: float = 3.0, limit: int = 20):
    # Calcula a média por modalidade e compara com o valor da licitação
    # Retorna licitações onde valor_estimado > media_modalidade * limite_fator
    query = text("""
        WITH media_modalidade AS (
            SELECT modalidade, AVG(valor_estimado) as media_valor
            FROM licitacoes
            WHERE valor_estimado IS NOT NULL AND valor_estimado > 0
            GROUP BY modalidade
        )
        SELECT l.id as licitacao_id, l.numero_controle, l.valor_estimado, m.media_valor
        FROM licitacoes l
        JOIN media_modalidade m ON l.modalidade = m.modalidade
        WHERE l.valor_estimado > (m.media_valor * :fator)
        LIMIT :limit
    """)
    result = db.execute(query, {"fator": limite_fator, "limit": limit}).fetchall()
    
    anomalias = []
    for row in result:
        anomalias.append({
            "licitacao_id": str(row.licitacao_id),
            "numero_controle": row.numero_controle or "S/N",
            "motivo": f"Valor estimado ({row.valor_estimado}) é mais de {limite_fator}x a média da modalidade",
            "valor_estimado": float(row.valor_estimado),
            "media_categoria": float(row.media_valor)
        })
    return anomalias

def get_anomalias_prazo(db: Session, limite_dias: int = 5, limit: int = 20):
    # Calcula a diferença entre data_encerramento e data_publicacao < limite_dias
    # Note: SQLite uses Julian day differences, Postgres uses Extract.
    # To be dialect-agnostic without raw SQL, we can query and filter in Python if dataset is small,
    # or use dialect specific. For MVP, we will do it in python memory if SQLite date math is tricky,
    # or just use a raw query if it's standard.
    # We will use Python filter for simplicity in SQLite dev.
    
    licitacoes = db.query(
        Licitacao.id, 
        Licitacao.numero_controle, 
        Licitacao.data_publicacao, 
        Licitacao.data_encerramento
    ).filter(
        Licitacao.data_publicacao.is_not(None),
        Licitacao.data_encerramento.is_not(None)
    ).all()

    anomalias = []
    for l in licitacoes:
        if type(l.data_publicacao) is str:
            # handle sqlite string dates if not parsed
            continue
        try:
            diff = (l.data_encerramento - l.data_publicacao).days
            if diff >= 0 and diff < limite_dias:
                anomalias.append({
                    "licitacao_id": str(l.id),
                    "numero_controle": l.numero_controle or "S/N",
                    "motivo": f"Prazo entre publicação e encerramento é muito curto ({diff} dias)",
                    "data_publicacao": l.data_publicacao.isoformat(),
                    "data_encerramento": l.data_encerramento.isoformat(),
                    "prazo_dias": diff
                })
                if len(anomalias) >= limit:
                    break
        except Exception:
            pass

    return anomalias

def get_anomalias_fornecedor_recorrente(db: Session, min_vitorias: int = 3, periodo_dias: int = 30, limit: int = 20):
    # Detecta fornecedores com múltiplos contratos num curto período
    # Isso seria ideal com Window Functions no SQL, mas faremos uma heurística por agregação.
    
    # Query agrupa por fornecedor e mês/ano (ou simplesmente contar total e exibir)
    # Como não temos datas de contratos sempre preenchidas no mock, vamos apenas
    # retornar os fornecedores que ganharam >= min_vitorias contratos no total por enquanto,
    # assumindo que a base é recente.
    
    query = (
        db.query(
            Fornecedor.id,
            Fornecedor.nome,
            func.count(Contrato.id).label("total_vitorias")
        )
        .join(Contrato, Fornecedor.id == Contrato.fornecedor_id)
        .group_by(Fornecedor.id)
        .having(func.count(Contrato.id) >= min_vitorias)
        .order_by(desc("total_vitorias"))
        .limit(limit)
        .all()
    )

    anomalias = []
    for row in query:
        anomalias.append({
            "fornecedor_id": str(row.id),
            "nome": row.nome,
            "motivo": f"Fornecedor venceu {row.total_vitorias} licitações, indicando alta recorrência.",
            "quantidade_vitorias": row.total_vitorias,
            "periodo_dias": periodo_dias # placeholder for V2 rules
        })
    return anomalias
