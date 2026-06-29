import sys
import os
import requests
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List
from sqlalchemy import func
import json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import Orgao, Licitacao, ItemLicitacao, ArquivoLicitacao, FaseLicitacao, Fornecedor, Contrato

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PNCP_API_URL = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
MAX_PAGES = 100  # Limite para MVP (Aumentado para carga inicial de 6 meses)
PAGE_SIZE = 50

def get_state_file_path() -> str:
    db_url = os.getenv("DATABASE_URL", "sqlite:///./openpncp.db")
    if db_url.startswith("sqlite:///"):
        db_path = db_url.replace("sqlite:///", "")
        db_dir = os.path.dirname(db_path)
        if db_dir and os.path.exists(db_dir):
            return os.path.join(db_dir, "sync_state.json")
    return "sync_state.json"

def load_sync_state() -> datetime | None:
    path = get_state_file_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
                date_str = data.get("ultima_data_historica")
                if date_str:
                    return datetime.strptime(date_str, "%Y-%m-%d")
        except Exception as e:
            logger.error(f"Erro ao ler arquivo de estado de sincronização: {e}")
    return None

def save_sync_state(dt: datetime):
    path = get_state_file_path()
    try:
        db_dir = os.path.dirname(path)
        if db_dir and not os.path.exists(db_dir):
            os.makedirs(db_dir, exist_ok=True)
            
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"ultima_data_historica": dt.strftime("%Y-%m-%d")}, f)
        logger.info(f"Progresso da sincronização histórica salvo: {dt.strftime('%Y-%m-%d')}")
    except Exception as e:
        logger.error(f"Erro ao salvar arquivo de estado de sincronização: {e}")

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
    
    # Se dt_inicial ou dt_final foram passados, rodamos a sincronização histórica/manual clássica no intervalo solicitado
    if dt_inicial or dt_final:
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
            # Busca automática no banco clássica
            try:
                max_date = db.query(func.max(Licitacao.data_publicacao)).scalar()
                if max_date:
                    dt_inicial_dt = max_date - timedelta(days=1)
                else:
                    dt_inicial_dt = datetime.now() - timedelta(days=2)
            except Exception as e:
                logger.error(f"Erro ao buscar data mais recente: {e}. Usando fallback.")
                dt_inicial_dt = datetime.now() - timedelta(days=2)
                
        logger.info(f"Sincronização manual solicitada de {dt_inicial_dt.strftime('%Y-%m-%d')} até {dt_final_dt.strftime('%Y-%m-%d')}")
        
        # Executa loop dia a dia clássico
        total_ins = 0
        total_upd = 0
        total_con = 0
        current_dt = dt_inicial_dt
        try:
            while current_dt <= dt_final_dt:
                dia_str = current_dt.strftime("%Y%m%d")
                logger.info(f"\n>>> Sincronizando dia {current_dt.strftime('%Y-%m-%d')}...")
                ins, upd, con = process_day(db, dia_str, dia_str)
                total_ins += ins
                total_upd += upd
                total_con += con
                time.sleep(2.0)
                current_dt += timedelta(days=1)
                
            logger.info(f"\n=== Sincronização Concluída ===")
            logger.info(f"Total de novas licitações: {total_ins}")
            logger.info(f"Total de licitações atualizadas: {total_upd}")
            logger.info(f"Total de novos contratos: {total_con}")
        except Exception as e:
            logger.error(f"Erro inesperado durante a ingestão manual: {e}")
            db.rollback()
        finally:
            db.close()
        return

    # MODO AUTOMÁTICO (sem datas informadas): Sincroniza hoje + 1 dia do histórico (catch-up)
    hoje_dt = datetime.now()
    hoje_str = hoje_dt.strftime("%Y%m%d")
    
    logger.info(f"Iniciando modo de sincronização automática e catch-up incremental...")
    
    # 1. Sincroniza o dia de hoje
    logger.info(f"\n>>> [1/2] Sincronizando o dia de HOJE ({hoje_dt.strftime('%Y-%m-%d')})...")
    total_ins, total_upd, total_con = 0, 0, 0
    try:
        ins, upd, con = process_day(db, hoje_str, hoje_str)
        total_ins += ins
        total_upd += upd
        total_con += con
    except Exception as e:
        logger.error(f"Erro ao processar o dia de hoje: {e}")
        db.rollback()
        db.close()
        return
        
    # 2. Carrega a data da última sincronização histórica (catch-up)
    ultima_data_historica = load_sync_state()
    
    if not ultima_data_historica:
        # Se não há estado salvo no JSON, busca a maior data no banco ANTES da importação de hoje
        try:
            # Para evitar pegar a data de hoje que acabamos de importar, buscamos a data máxima menor que hoje_dt
            max_date = db.query(func.max(Licitacao.data_publicacao)).filter(Licitacao.data_publicacao < hoje_dt.date()).scalar()
            if max_date:
                # Se for datetime, mantemos. Se for string, convertemos
                if isinstance(max_date, str):
                    ultima_data_historica = datetime.strptime(max_date[:10], "%Y-%m-%d")
                else:
                    ultima_data_historica = datetime.combine(max_date, datetime.min.time())
                logger.info(f"Nenhum estado de sincronização encontrado. Inicializado a partir do banco de dados: {ultima_data_historica.strftime('%Y-%m-%d')}")
            else:
                # Se o banco está vazio, inicia o catch-up a partir de 2 dias atrás
                ultima_data_historica = hoje_dt - timedelta(days=2)
                logger.info(f"Banco vazio e nenhum estado de sincronização. Inicializado com fallback de 2 dias atrás: {ultima_data_historica.strftime('%Y-%m-%d')}")
        except Exception as e:
            logger.error(f"Erro ao buscar data inicial do histórico no banco: {e}. Usando fallback.")
            ultima_data_historica = hoje_dt - timedelta(days=2)
            
        save_sync_state(ultima_data_historica)
        
    # 3. Calcula o dia seguinte do histórico a ser processado
    dia_historico_dt = ultima_data_historica + timedelta(days=1)
    
    if dia_historico_dt.date() < hoje_dt.date():
        logger.info(f"\n>>> [2/2] Sincronizando dia histórico de CATCH-UP ({dia_historico_dt.strftime('%Y-%m-%d')})...")
        time.sleep(2.0) # sleep curto entre o dia de hoje e o histórico
        try:
            dia_historico_str = dia_historico_dt.strftime("%Y%m%d")
            ins_h, upd_h, con_h = process_day(db, dia_historico_str, dia_historico_str)
            total_ins += ins_h
            total_upd += upd_h
            total_con += con_h
            
            # Se terminou com sucesso, avança e salva o novo progresso
            save_sync_state(dia_historico_dt)
            logger.info(f"Dia histórico {dia_historico_dt.strftime('%Y-%m-%d')} sincronizado e registrado no arquivo de progresso.")
        except Exception as e:
            logger.error(f"Erro ao processar o dia histórico {dia_historico_dt.strftime('%Y-%m-%d')}: {e}")
            db.rollback()
    else:
        logger.info(f"\n>>> [2/2] Carga histórica está totalmente em dia (último registro: {ultima_data_historica.strftime('%Y-%m-%d')}). Sincronizado com a data de hoje.")
        
    logger.info(f"\n=== Sincronização Automática Concluída ===")
    logger.info(f"Total de novas licitações no ciclo: {total_ins}")
    logger.info(f"Total de licitações atualizadas no ciclo: {total_upd}")
    logger.info(f"Total de novos contratos no ciclo: {total_con}")
    db.close()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Ingestão incremental e histórica do PNCP.")
    parser.add_argument("--inicial", type=str, default=None, help="Data inicial no formato YYYYMMDD")
    parser.add_argument("--final", type=str, default=None, help="Data final no formato YYYYMMDD")
    
    args = parser.parse_args()
    ingest_data(dt_inicial=args.inicial, dt_final=args.final)
