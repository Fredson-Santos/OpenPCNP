import sys
import os
import requests
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import Orgao, Licitacao

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PNCP_API_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
MAX_PAGES = 5  # Limite para MVP
PAGE_SIZE = 50

def parse_date(date_str: str) -> datetime | None:
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None

def fetch_pncp_data(data_inicial: str, data_final: str, page: int = 1) -> Dict[str, Any]:
    params = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "codigoModalidadeContratacao": 8, # 8: Pregão Eletrônico
        "pagina": page,
        "tamanhoPagina": PAGE_SIZE
    }
    logger.info(f"Buscando página {page} do PNCP...")
    response = requests.get(PNCP_API_URL, params=params)
    response.raise_for_status()
    return response.json()

def ingest_data():
    db = SessionLocal()
    
    data_final = datetime.now().strftime("%Y%m%d")
    data_inicial = (datetime.now() - timedelta(days=2)).strftime("%Y%m%d")
    
    total_inserted = 0
    total_updated = 0
    
    try:
        for page in range(1, MAX_PAGES + 1):
            try:
                data = fetch_pncp_data(data_inicial, data_final, page)
            except requests.exceptions.RequestException as e:
                logger.error(f"Erro ao buscar dados do PNCP: {e}")
                break
            
            items = data.get("data", [])
            if not items:
                logger.info("Nenhum dado retornado na página.")
                break
            
            for item in items:
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
                    db.commit()
                    db.refresh(orgao)
                
                numero_controle = item.get("numeroControlePNCP")
                if not numero_controle:
                    continue
                
                licitacao = db.query(Licitacao).filter(Licitacao.numero_controle == numero_controle).first()
                
                objeto = item.get("objetoCompra", "Sem objeto")
                modalidade = item.get("modalidadeNome", "Não informada")
                situacao = item.get("situacaoCompraNome", "Desconhecida")
                valor_estimado = item.get("valorTotalEstimado")
                data_publicacao = parse_date(item.get("dataPublicacaoPncp"))
                data_encerramento = parse_date(item.get("dataEncerramentoProposta"))
                
                if licitacao:
                    licitacao.objeto = objeto
                    licitacao.modalidade = modalidade
                    licitacao.situacao = situacao
                    licitacao.valor_estimado = valor_estimado
                    licitacao.data_publicacao = data_publicacao
                    licitacao.data_encerramento = data_encerramento
                    total_updated += 1
                else:
                    licitacao = Licitacao(
                        orgao_id=orgao.id,
                        numero_controle=numero_controle,
                        objeto=objeto,
                        modalidade=modalidade,
                        situacao=situacao,
                        valor_estimado=valor_estimado,
                        data_publicacao=data_publicacao,
                        data_encerramento=data_encerramento
                    )
                    db.add(licitacao)
                    total_inserted += 1
            
            db.commit()
            
            paginas_restantes = data.get("paginasRestantes", 0)
            if paginas_restantes == 0:
                break
                
        logger.info(f"Ingestão finalizada. {total_inserted} novas licitações, {total_updated} atualizadas.")
        
    except Exception as e:
        logger.error(f"Erro durante a ingestão: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    ingest_data()
