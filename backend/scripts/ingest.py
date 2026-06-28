import sys
import os
import requests
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List
from sqlalchemy import func

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import Orgao, Licitacao, ItemLicitacao, ArquivoLicitacao, FaseLicitacao, Fornecedor, Contrato

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PNCP_API_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
MAX_PAGES = 100  # Limite para MVP (Aumentado para carga inicial de 6 meses)
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

def fetch_itens(cnpj: str, ano: int, seq: int) -> List[Dict[str, Any]]:
    url = f"https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}/itens"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except requests.exceptions.RequestException as e:
        logger.warning(f"Erro ao buscar itens para {cnpj} {ano}/{seq}: {e}")
    return []

def fetch_arquivos(cnpj: str, ano: int, seq: int) -> List[Dict[str, Any]]:
    url = f"https://pncp.gov.br/api/pncp/v1/orgaos/{cnpj}/compras/{ano}/{seq}/arquivos"
    try:
        resp = requests.get(url, timeout=10)
        if resp.status_code == 200:
            return resp.json()
    except requests.exceptions.RequestException as e:
        logger.warning(f"Erro ao buscar arquivos para {cnpj} {ano}/{seq}: {e}")
    return []

def fetch_pncp_contratos(data_inicial: str, data_final: str, page: int = 1) -> Dict[str, Any]:
    url = "https://pncp.gov.br/api/consulta/v1/contratos"
    params = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "pagina": page,
        "tamanhoPagina": PAGE_SIZE
    }
    logger.info(f"Buscando página {page} de CONTRATOS do PNCP...")
    response = requests.get(url, params=params)
    response.raise_for_status()
    return response.json()

def process_day(db, data_inicial: str, data_final: str) -> tuple[int, int, int]:
    total_inserted = 0
    total_updated = 0
    total_contratos = 0
    
    # --- FASE 1: COMPRAS (LICITAÇÕES) ---
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

            db.flush()
            
            ano_compra = item.get("anoCompra")
            seq_compra = item.get("sequencialCompra")
            
            # Excluir detalhes antigos para evitar duplicação em atualizações
            db.query(ItemLicitacao).filter(ItemLicitacao.licitacao_id == licitacao.id).delete()
            db.query(ArquivoLicitacao).filter(ArquivoLicitacao.licitacao_id == licitacao.id).delete()
            db.query(FaseLicitacao).filter(FaseLicitacao.licitacao_id == licitacao.id).delete()
            db.flush()

            if ano_compra and seq_compra and cnpj:
                itens_data = fetch_itens(cnpj, ano_compra, seq_compra)
                for i_data in itens_data:
                    novo_item = ItemLicitacao(
                        licitacao_id=licitacao.id,
                        descricao=i_data.get("descricao", "Sem descrição")[:200],
                        quantidade=i_data.get("quantidade", 0.0),
                        valor_unitario=i_data.get("valorUnitarioEstimado", 0.0),
                        valor_total=i_data.get("valorTotal") or i_data.get("valorTotalEstimado", 0.0)
                    )
                    db.add(novo_item)
                # Rate limit prevention: sleep após chamar itens
                time.sleep(0.2)

                arquivos_data = fetch_arquivos(cnpj, ano_compra, seq_compra)
                for a_data in arquivos_data:
                    url = a_data.get("url") or a_data.get("linkAcesso") or ""
                    if url:
                        novo_arquivo = ArquivoLicitacao(
                            licitacao_id=licitacao.id,
                            nome=a_data.get("tituloDocumento", "Sem título")[:200],
                            url=url,
                            tipo=str(a_data.get("tipoDocumentoId", "0"))
                        )
                        db.add(novo_arquivo)
                # Rate limit prevention: sleep após chamar arquivos
                time.sleep(0.2)

            fase = FaseLicitacao(
                licitacao_id=licitacao.id,
                data=data_publicacao or datetime.now(),
                descricao=f"Status: {situacao}",
                status=situacao
            )
            db.add(fase)
        
        db.commit()
        
        # Rate limit prevention: sleep de 1.0s entre páginas
        time.sleep(1.0)
        
        paginas_restantes = data.get("paginasRestantes", 0)
        if paginas_restantes == 0:
            break
            
    logger.info(f"Ingestão de compras finalizada para o dia {data_inicial}. {total_inserted} novas licitações, {total_updated} atualizadas. Iniciando contratos...")
    
    # --- FASE 2: CONTRATOS E FORNECEDORES ---
    for page in range(1, MAX_PAGES + 1):
        try:
            c_data = fetch_pncp_contratos(data_inicial, data_final, page)
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao buscar contratos do PNCP: {e}")
            break
            
        contratos_items = c_data.get("data", [])
        if not contratos_items:
            break
            
        for c in contratos_items:
            num_controle_compra = c.get("numeroControlePncpCompra")
            if not num_controle_compra:
                continue
                
            # Só salvamos contratos de licitações que já temos no banco
            lic = db.query(Licitacao).filter(Licitacao.numero_controle == num_controle_compra).first()
            if not lic:
                continue
                
            ni_fornecedor = c.get("niFornecedor")
            if not ni_fornecedor:
                continue
                
            # Checa se fornecedor já existe
            fornecedor = db.query(Fornecedor).filter(Fornecedor.ni == ni_fornecedor).first()
            if not fornecedor:
                fornecedor = Fornecedor(
                    ni=ni_fornecedor,
                    nome=c.get("nomeRazaoSocialFornecedor", "Desconhecido")[:255],
                    tipo=c.get("tipoPessoa", "PJ")[:50]
                )
                db.add(fornecedor)
                db.flush()
                
            # Checa se contrato existe
            num_contrato = c.get("numeroContratoEmpenho") or c.get("numeroControlePNCP") or ""
            contrato = db.query(Contrato).filter(Contrato.licitacao_id == lic.id, Contrato.fornecedor_id == fornecedor.id, Contrato.numero == num_contrato).first()
            
            if not contrato:
                contrato = Contrato(
                    licitacao_id=lic.id,
                    fornecedor_id=fornecedor.id,
                    numero=num_contrato,
                    objeto=c.get("objetoContrato", ""),
                    valor_contrato=c.get("valorGlobal", 0.0),
                    data_assinatura=parse_date(c.get("dataAssinatura")),
                    vigencia_inicio=parse_date(c.get("dataVigenciaInicio")),
                    vigencia_fim=parse_date(c.get("dataVigenciaFim"))
                )
                db.add(contrato)
                total_contratos += 1
        
        db.commit()
        
        # Rate limit prevention: sleep de 1.0s entre páginas de contratos
        time.sleep(1.0)
        
        if c_data.get("paginasRestantes", 0) == 0:
            break

    logger.info(f"Ingestão total para o dia {data_inicial} finalizada. {total_contratos} novos contratos registrados.")
    return total_inserted, total_updated, total_contratos

def ingest_data(dt_inicial: str = None, dt_final: str = None):
    db = SessionLocal()
    
    # 1. Determinar datas final e inicial
    if dt_final:
        try:
            dt_final_dt = datetime.strptime(dt_final, "%Y%m%d")
        except ValueError:
            logger.error("Formato de data final inválido. Deve ser YYYYMMDD.")
            db.close()
            return
    else:
        dt_final_dt = datetime.now()
        
    if dt_inicial:
        try:
            dt_inicial_dt = datetime.strptime(dt_inicial, "%Y%m%d")
        except ValueError:
            logger.error("Formato de data inicial inválido. Deve ser YYYYMMDD.")
            db.close()
            return
    else:
        # Busca automática no banco
        try:
            max_date = db.query(func.max(Licitacao.data_publicacao)).scalar()
            if max_date:
                # Volta 1 dia para evitar perder dados publicados parcialmente no mesmo dia
                dt_inicial_dt = max_date - timedelta(days=1)
                logger.info(f"Data mais recente no banco: {max_date.strftime('%Y-%m-%d')}. "
                            f"Catch-up automático iniciando em: {dt_inicial_dt.strftime('%Y-%m-%d')}")
            else:
                dt_inicial_dt = datetime.now() - timedelta(days=2)
                logger.info(f"Nenhum registro encontrado no banco. "
                            f"Iniciando fallback padrão de 2 dias atrás: {dt_inicial_dt.strftime('%Y-%m-%d')}")
        except Exception as e:
            logger.error(f"Erro ao buscar data mais recente no banco: {e}. Usando fallback de 2 dias.")
            dt_inicial_dt = datetime.now() - timedelta(days=2)
            
    logger.info(f"Sincronização agendada de {dt_inicial_dt.strftime('%Y-%m-%d')} até {dt_final_dt.strftime('%Y-%m-%d')}")
    
    total_ins = 0
    total_upd = 0
    total_con = 0
    
    # 2. Loop dia a dia
    current_dt = dt_inicial_dt
    try:
        while current_dt <= dt_final_dt:
            dia_str = current_dt.strftime("%Y%m%d")
            logger.info(f"\n>>> Sincronizando dia {current_dt.strftime('%Y-%m-%d')}...")
            
            ins, upd, con = process_day(db, dia_str, dia_str)
            total_ins += ins
            total_upd += upd
            total_con += con
            
            # Rate limit prevention: sleep de 2.0s entre dias
            time.sleep(2.0)
            current_dt += timedelta(days=1)
            
        logger.info(f"\n=== Sincronização Concluída ===")
        logger.info(f"Total de novas licitações: {total_ins}")
        logger.info(f"Total de licitações atualizadas: {total_upd}")
        logger.info(f"Total de novos contratos: {total_con}")
        
    except Exception as e:
        logger.error(f"Erro inesperado durante a ingestão do período: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingestão incremental e histórica do PNCP.")
    parser.add_argument("--inicial", type=str, default=None, help="Data inicial no formato YYYYMMDD")
    parser.add_argument("--final", type=str, default=None, help="Data final no formato YYYYMMDD")
    
    args = parser.parse_args()
    ingest_data(dt_inicial=args.inicial, dt_final=args.final)
