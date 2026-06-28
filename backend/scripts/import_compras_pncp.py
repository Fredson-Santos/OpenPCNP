import os
import sys
import csv
import glob
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.orgaos import Orgao
from app.models.licitacoes import Licitacao, ItemLicitacao
from app.models.fornecedores import Fornecedor, Contrato

def parse_date(date_str: str):
    if not date_str:
        return None
    date_str = date_str.strip()
    try:
        if len(date_str) > 10:
            return datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
        else:
            return datetime.strptime(date_str, "%Y-%m-%d").date()
    except ValueError:
        try:
             if len(date_str) > 10:
                 return datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
             else:
                 return datetime.strptime(date_str, "%d/%m/%Y").date()
        except ValueError:
             return None

def parse_currency(val_str: str) -> float:
    if not val_str:
        return 0.0
    val_str = str(val_str).replace('"', '').strip()
    try:
        if ',' in val_str and '.' in val_str:
             val_str = val_str.replace('.', '').replace(',', '.')
        elif ',' in val_str:
             val_str = val_str.replace(',', '.')
        return float(val_str)
    except ValueError:
        return 0.0

def process_compras(db, filepath, orgaos_cache, licitacoes_cache):
    print(f"Processando Compras: {filepath}")
    
    batch_size = 500
    count = 0
    
    try:
        f = open(filepath, mode='r', encoding='utf-8')
        f.read(1024)
        f.seek(0)
    except UnicodeDecodeError:
        f = open(filepath, mode='r', encoding='iso-8859-1')
        
    reader = csv.DictReader(f, delimiter=',')
    if not reader.fieldnames or "numero_controle_PNCP" not in reader.fieldnames:
        f.seek(0)
        reader = csv.DictReader(f, delimiter=';')
        
    for row in reader:
        row = {k.strip('"').strip() if k else k: v for k, v in row.items()}
        
        numero_controle = row.get("numero_controle_PNCP")
        if not numero_controle:
            continue
            
        nome_orgao = row.get("orgao_entidade_razao_social", "Órgão Desconhecido")
        cnpj_orgao = row.get("orgao_entidade_cnpj")
        uf_orgao = row.get("unidade_orgao_uf_sigla")
        objeto = row.get("objeto_compra", "Objeto não informado")
        modalidade = row.get("modalidade_nome", "")
        situacao = row.get("situacao_compra_nome_pncp", "")
        valor_estimado = parse_currency(row.get("valor_total_estimado"))
        data_pub = parse_date(row.get("data_publicacao_pncp"))
        data_enc = parse_date(row.get("data_encerramento_proposta_pncp"))
        
        if nome_orgao not in orgaos_cache:
            orgao = db.query(Orgao).filter(Orgao.nome == nome_orgao).first()
            if not orgao:
                orgao = Orgao(nome=nome_orgao, cnpj=cnpj_orgao, uf=uf_orgao, esfera="Federal")
                db.add(orgao)
                db.flush()
            else:
                if uf_orgao and not orgao.uf:
                    orgao.uf = uf_orgao
                if cnpj_orgao and not orgao.cnpj:
                    orgao.cnpj = cnpj_orgao
            orgaos_cache[nome_orgao] = orgao.id
        orgao_id = orgaos_cache[nome_orgao]
        
        if numero_controle not in licitacoes_cache:
            licitacao = db.query(Licitacao).filter(Licitacao.numero_controle == numero_controle).first()
            if not licitacao:
                licitacao = Licitacao(
                    orgao_id=orgao_id,
                    numero_controle=numero_controle,
                    objeto=objeto,
                    modalidade=modalidade,
                    situacao=situacao,
                    valor_estimado=valor_estimado,
                    data_publicacao=data_pub,
                    data_encerramento=data_enc
                )
                db.add(licitacao)
                db.flush()
            licitacoes_cache[numero_controle] = licitacao.id
            
        count += 1
        if count % batch_size == 0:
            db.commit()
            
    db.commit()
    f.close()
    print(f"Total de Licitações inseridas/atualizadas: {count}")

def process_itens(db, filepath, licitacoes_cache):
    print(f"Processando Itens de Compra: {filepath}")
    
    batch_size = 500
    count = 0
    
    try:
        f = open(filepath, mode='r', encoding='utf-8')
        f.read(1024)
        f.seek(0)
    except UnicodeDecodeError:
        f = open(filepath, mode='r', encoding='iso-8859-1')
        
    reader = csv.DictReader(f, delimiter=',')
    if not reader.fieldnames or "numero_controle_PNCP_compra" not in reader.fieldnames:
        f.seek(0)
        reader = csv.DictReader(f, delimiter=';')
        
    for row in reader:
        row = {k.strip('"').strip() if k else k: v for k, v in row.items()}
        
        numero_controle = row.get("numero_controle_PNCP_compra")
        if not numero_controle or numero_controle not in licitacoes_cache:
            continue
            
        licitacao_id = licitacoes_cache[numero_controle]
        descricao = row.get("descricao_detalhada") or row.get("descricao_resumida", "Item sem descrição")
        quantidade = parse_currency(row.get("quantidade"))
        valor_unit = parse_currency(row.get("valor_unitario_estimado"))
        valor_tot = parse_currency(row.get("valor_total"))
        
        item = ItemLicitacao(
            licitacao_id=licitacao_id,
            descricao=descricao,
            quantidade=quantidade,
            valor_unitario=valor_unit,
            valor_total=valor_tot
        )
        db.add(item)
        
        count += 1
        if count % batch_size == 0:
            db.commit()
            
    db.commit()
    f.close()
    print(f"Total de Itens inseridos: {count}")

def process_resultados(db, filepath, licitacoes_cache, fornecedores_cache):
    print(f"Processando Resultados de Compra: {filepath}")
    
    batch_size = 500
    count = 0
    contratos_cache = {}
    
    try:
        f = open(filepath, mode='r', encoding='utf-8')
        f.read(1024)
        f.seek(0)
    except UnicodeDecodeError:
        f = open(filepath, mode='r', encoding='iso-8859-1')
        
    reader = csv.DictReader(f, delimiter=',')
    if not reader.fieldnames or "numero_controle_PNCP_compra" not in reader.fieldnames:
        f.seek(0)
        reader = csv.DictReader(f, delimiter=';')
        
    for row in reader:
        row = {k.strip('"').strip() if k else k: v for k, v in row.items()}
        
        numero_controle = row.get("numero_controle_PNCP_compra")
        if not numero_controle or numero_controle not in licitacoes_cache:
            continue
            
        licitacao_id = licitacoes_cache[numero_controle]
        ni_fornecedor = row.get("ni_fornecedor")
        if not ni_fornecedor:
            continue
            
        nome_fornecedor = row.get("nome_razao_social_fornecedor", "Desconhecido")
        valor_homologado = parse_currency(row.get("valor_total_homologado"))
        
        if ni_fornecedor not in fornecedores_cache:
            fornecedor = db.query(Fornecedor).filter(Fornecedor.ni == ni_fornecedor).first()
            if not fornecedor:
                fornecedor = Fornecedor(ni=ni_fornecedor, nome=nome_fornecedor)
                db.add(fornecedor)
                db.flush()
            fornecedores_cache[ni_fornecedor] = fornecedor.id
        fornecedor_id = fornecedores_cache[ni_fornecedor]
        
        cache_key = (licitacao_id, fornecedor_id)
        if cache_key not in contratos_cache:
            contrato = db.query(Contrato).filter(
                Contrato.licitacao_id == licitacao_id,
                Contrato.fornecedor_id == fornecedor_id
            ).first()
            
            if not contrato:
                contrato = Contrato(
                    licitacao_id=licitacao_id,
                    fornecedor_id=fornecedor_id,
                    numero=f"Resultado-{numero_controle}",
                    valor_contrato=valor_homologado,
                    objeto="Resultado Homologado de Compra"
                )
                db.add(contrato)
                db.flush() # Importante para evitar StaleDataError com novos objetos
            else:
                contrato.valor_contrato += valor_homologado
                
            contratos_cache[cache_key] = contrato
        else:
            # Pega do cache da sessão (o objeto já está attached no db)
            contrato = contratos_cache[cache_key]
            contrato.valor_contrato += valor_homologado
            
        count += 1
        if count % batch_size == 0:
            db.commit()
            
    db.commit()
    f.close()
    print(f"Total de Resultados/Contratos inseridos: {count}")

def main():
    base_dir = r"c:\Users\Fred\Projetos\OpenPNCP\csv"
    
    compras_files = sorted(glob.glob(os.path.join(base_dir, "comprasGOV-mensal-VW_FT_PNCP_COMPRA-*.csv")))
    itens_files = sorted(glob.glob(os.path.join(base_dir, "comprasGOV-mensal-VW_FT_PNCP_COMPRA_ITEM-*.csv")))
    resultados_files = sorted(glob.glob(os.path.join(base_dir, "comprasGOV-mensal-VW_DM_PNCP_ITEM_RESULTADO-*.csv")))
    
    if not compras_files:
        print("Nenhum arquivo de Compras encontrado.")
        return
        
    db = SessionLocal()
    
    orgaos_cache = {}
    licitacoes_cache = {}
    fornecedores_cache = {}
    
    for f in compras_files:
        process_compras(db, f, orgaos_cache, licitacoes_cache)
        
    for f in itens_files:
        process_itens(db, f, licitacoes_cache)
        
    for f in resultados_files:
        process_resultados(db, f, licitacoes_cache, fornecedores_cache)
        
    db.close()
    print("Ingestão PNCP concluída com sucesso.")

if __name__ == "__main__":
    main()
