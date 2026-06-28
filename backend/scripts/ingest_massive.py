import sys
import os
import requests
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import Orgao, Licitacao, ItemLicitacao, ArquivoLicitacao, FaseLicitacao

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PNCP_API_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
PAGE_SIZE = 50
MAX_PAGES_PER_WINDOW = 20
RETRY_DELAY = 2
MAX_RETRIES = 3

MODALIDADES = [
    (8,  "Pregão Eletrônico"),
    (6,  "Concorrência"),
    (4,  "Tomada de Preços"),
    (3,  "Convite"),
    (12, "Dispensa de Licitação"),
]

DAYS_BACK = 90
WINDOW_SIZE_DAYS = 15


def parse_date(date_str: str) -> datetime | None:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None


def fetch_with_retry(url, params, retries=MAX_RETRIES):
    for attempt in range(retries):
        try:
            resp = requests.get(url, params=params, timeout=30)
            resp.raise_for_status()
            return resp.json()
        except requests.exceptions.RequestException as e:
            if attempt < retries - 1:
                logger.warning(f"Tentativa {attempt + 1} falhou: {e}. Aguardando {RETRY_DELAY}s...")
                time.sleep(RETRY_DELAY)
            else:
                raise


def fetch_pncp_data(data_inicial, data_final, modalidade_cod, page=1):
    params = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "codigoModalidadeContratacao": modalidade_cod,
        "pagina": page,
        "tamanhoPagina": PAGE_SIZE,
    }
    return fetch_with_retry(PNCP_API_URL, params)


def fetch_itens(cnpj, ano, seq):
    url = f"https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}/itens"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except requests.exceptions.RequestException:
        pass
    return []


def fetch_arquivos(cnpj, ano, seq):
    url = f"https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}/arquivos"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except requests.exceptions.RequestException:
        pass
    return []


def process_item(db, item):
    orgao_data = item.get("orgaoEntidade", {})
    unidade_data = item.get("unidadeOrgao", {})

    cnpj = orgao_data.get("cnpj")
    nome_orgao = orgao_data.get("razaoSocial", "Órgão Desconhecido")
    esfera = orgao_data.get("esferaId", "")
    uf = unidade_data.get("ufSigla", "") if unidade_data else ""

    orgao = None
    if cnpj:
        orgao = db.query(Orgao).filter(Orgao.cnpj == cnpj).first()
    if not orgao:
        orgao = db.query(Orgao).filter(Orgao.nome == nome_orgao).first()
    if not orgao:
        orgao = Orgao(cnpj=cnpj, nome=nome_orgao, esfera=esfera, uf=uf)
        db.add(orgao)
        db.flush()

    numero_controle = item.get("numeroControlePNCP")
    if not numero_controle:
        return False

    licitacao = db.query(Licitacao).filter(Licitacao.numero_controle == numero_controle).first()

    objeto = item.get("objetoCompra", "Sem objeto")
    modalidade = item.get("modalidadeNome", "Não informada")
    situacao = item.get("situacaoCompraNome", "Desconhecida")
    valor_estimado = item.get("valorTotalEstimado")
    data_publicacao = parse_date(item.get("dataPublicacaoPncp"))
    data_encerramento = parse_date(item.get("dataEncerramentoProposta"))

    is_new = False
    if licitacao:
        licitacao.objeto = objeto
        licitacao.modalidade = modalidade
        licitacao.situacao = situacao
        licitacao.valor_estimado = valor_estimado
        licitacao.data_publicacao = data_publicacao
        licitacao.data_encerramento = data_encerramento
    else:
        licitacao = Licitacao(
            orgao_id=orgao.id,
            numero_controle=numero_controle,
            objeto=objeto,
            modalidade=modalidade,
            situacao=situacao,
            valor_estimado=valor_estimado,
            data_publicacao=data_publicacao,
            data_encerramento=data_encerramento,
        )
        db.add(licitacao)
        is_new = True

    db.flush()

    db.query(ItemLicitacao).filter(ItemLicitacao.licitacao_id == licitacao.id).delete()
    db.query(ArquivoLicitacao).filter(ArquivoLicitacao.licitacao_id == licitacao.id).delete()
    db.query(FaseLicitacao).filter(FaseLicitacao.licitacao_id == licitacao.id).delete()
    db.flush()

    ano_compra = item.get("anoCompra")
    seq_compra = item.get("sequencialCompra")

    if ano_compra and seq_compra and cnpj:
        for i_data in fetch_itens(cnpj, ano_compra, seq_compra):
            db.add(ItemLicitacao(
                licitacao_id=licitacao.id,
                descricao=i_data.get("descricao", "Sem descrição")[:200],
                quantidade=i_data.get("quantidade", 0.0),
                valor_unitario=i_data.get("valorUnitarioEstimado", 0.0),
                valor_total=i_data.get("valorTotal") or i_data.get("valorTotalEstimado", 0.0),
            ))

        for a_data in fetch_arquivos(cnpj, ano_compra, seq_compra):
            url = a_data.get("url") or a_data.get("linkAcesso") or ""
            if url:
                db.add(ArquivoLicitacao(
                    licitacao_id=licitacao.id,
                    nome=a_data.get("tituloDocumento", "Sem título")[:200],
                    url=url,
                    tipo=str(a_data.get("tipoDocumentoId", "0")),
                ))

    db.add(FaseLicitacao(
        licitacao_id=licitacao.id,
        data=data_publicacao or datetime.now(),
        descricao=f"Status: {situacao}",
        status=situacao,
    ))

    return is_new


def ingest_massive():
    db = SessionLocal()
    total_inserted = 0
    total_updated = 0
    total_errors = 0
    start_time = time.time()

    hoje = datetime.now()

    windows = []
    cursor = hoje
    for _ in range(DAYS_BACK // WINDOW_SIZE_DAYS):
        window_start = cursor - timedelta(days=WINDOW_SIZE_DAYS)
        windows.append((window_start.strftime("%Y%m%d"), cursor.strftime("%Y%m%d")))
        cursor = window_start

    logger.info(f"=== INGESTÃO MASSIVA ===")
    logger.info(f"Período: últimos {DAYS_BACK} dias ({len(windows)} janelas de {WINDOW_SIZE_DAYS} dias)")
    logger.info(f"Modalidades: {len(MODALIDADES)}")
    logger.info(f"Máx páginas por janela: {MAX_PAGES_PER_WINDOW}")

    try:
        for mod_cod, mod_nome in MODALIDADES:
            logger.info(f"\n--- Modalidade: {mod_nome} (código {mod_cod}) ---")
            mod_inserted = 0
            mod_updated = 0

            for win_start, win_end in windows:
                logger.info(f"  Janela: {win_start} → {win_end}")

                for page in range(1, MAX_PAGES_PER_WINDOW + 1):
                    try:
                        data = fetch_pncp_data(win_start, win_end, mod_cod, page)
                    except requests.exceptions.RequestException as e:
                        logger.error(f"    Erro na API (pág {page}): {e}")
                        total_errors += 1
                        break

                    items = data.get("data", [])
                    if not items:
                        break

                    for item in items:
                        try:
                            is_new = process_item(db, item)
                            if is_new:
                                total_inserted += 1
                                mod_inserted += 1
                            else:
                                total_updated += 1
                                mod_updated += 1
                        except Exception as e:
                            logger.warning(f"    Erro processando item: {e}")
                            total_errors += 1
                            db.rollback()

                    db.commit()

                    paginas_restantes = data.get("paginasRestantes", 0)
                    if paginas_restantes == 0:
                        break

                    time.sleep(0.3)

            logger.info(f"  {mod_nome}: +{mod_inserted} novas, {mod_updated} atualizadas")

    except KeyboardInterrupt:
        logger.info("Interrompido pelo usuário.")
        db.commit()
    except Exception as e:
        logger.error(f"Erro fatal: {e}")
        db.rollback()
    finally:
        db.close()

    elapsed = time.time() - start_time
    logger.info(f"\n=== RESULTADO ===")
    logger.info(f"Novas: {total_inserted}")
    logger.info(f"Atualizadas: {total_updated}")
    logger.info(f"Erros: {total_errors}")
    logger.info(f"Tempo: {elapsed:.1f}s ({elapsed/60:.1f} min)")


if __name__ == "__main__":
    ingest_massive()
