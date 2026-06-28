import os
import sys
import csv
import glob
from datetime import datetime
import uuid

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models.orgaos import Orgao
from app.models.licitacoes import Licitacao
from app.models.fornecedores import Fornecedor, Contrato

def parse_date(date_str: str):
    if not date_str:
        return None
    date_str = date_str.strip()
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
    val_str = val_str.replace('"', '').replace('.', '').replace(',', '.')
    try:
        return float(val_str)
    except ValueError:
        return 0.0

def process_file(db, filepath):
    print(f"Processando arquivo: {filepath}")
    
    # Dicionários de cache para evitar múltiplas queries no mesmo arquivo
    orgaos_cache = {}
    fornecedores_cache = {}
    licitacoes_cache = {}
    
    batch_size = 500
    count = 0
    
    # As the files have headers, but might have encoding issues, let's try utf-8 then iso-8859-1
    try:
        f = open(filepath, mode='r', encoding='utf-8')
        f.read(1024)
        f.seek(0)
    except UnicodeDecodeError:
        f = open(filepath, mode='r', encoding='iso-8859-1')
        
    reader = csv.DictReader(f, delimiter=';')
    
    for row in reader:
        # Prevenindo chaves sujas por BOM ou aspas
        row = {k.strip('"').strip() if k else k: v for k, v in row.items()}
        
        # Obter campos (tratando possíveis divergências de nomes)
        nome_orgao = row.get("Nome Órgão", "Órgão Desconhecido")
        
        ni_fornecedor = row.get("Código Contratado")
        nome_fornecedor = row.get("Nome Contratado", "Desconhecido")
        
        num_licitacao = row.get("Número Licitação")
        if not num_licitacao or num_licitacao.strip() == "":
            num_licitacao = f"DUMMY-{uuid.uuid4().hex[:8]}"
            
        num_contrato = row.get("Número do Contrato", "")
        objeto = row.get("Objeto", "")
        dt_assinatura = parse_date(row.get("Data Assinatura Contrato"))
        dt_inicio = parse_date(row.get("Data Início Vigência"))
        dt_fim = parse_date(row.get("Data Fim Vigência"))
        valor = parse_currency(row.get("Valor Inicial Compra"))
        
        if not ni_fornecedor:
            continue
            
        # 1. Órgão
        if nome_orgao not in orgaos_cache:
            orgao = db.query(Orgao).filter(Orgao.nome == nome_orgao).first()
            if not orgao:
                orgao = Orgao(nome=nome_orgao, esfera="Federal")
                db.add(orgao)
                db.flush()
            orgaos_cache[nome_orgao] = orgao.id
        orgao_id = orgaos_cache[nome_orgao]
        
        # 2. Fornecedor
        if ni_fornecedor not in fornecedores_cache:
            fornecedor = db.query(Fornecedor).filter(Fornecedor.ni == ni_fornecedor).first()
            if not fornecedor:
                fornecedor = Fornecedor(ni=ni_fornecedor, nome=nome_fornecedor)
                db.add(fornecedor)
                db.flush()
            fornecedores_cache[ni_fornecedor] = fornecedor.id
        fornecedor_id = fornecedores_cache[ni_fornecedor]
        
        # 3. Licitação
        if num_licitacao not in licitacoes_cache:
            licitacao = db.query(Licitacao).filter(Licitacao.numero_controle == num_licitacao).first()
            if not licitacao:
                licitacao = Licitacao(
                    orgao_id=orgao_id,
                    numero_controle=num_licitacao,
                    objeto=f"Licitação para o contrato {num_contrato}"
                )
                db.add(licitacao)
                db.flush()
            licitacoes_cache[num_licitacao] = licitacao.id
        licitacao_id = licitacoes_cache[num_licitacao]
        
        # 4. Contrato
        contrato = db.query(Contrato).filter(
            Contrato.numero == num_contrato, 
            Contrato.fornecedor_id == fornecedor_id
        ).first()
        
        if not contrato:
            contrato = Contrato(
                licitacao_id=licitacao_id,
                fornecedor_id=fornecedor_id,
                numero=num_contrato,
                objeto=objeto,
                valor_contrato=valor,
                data_assinatura=dt_assinatura,
                vigencia_inicio=dt_inicio,
                vigencia_fim=dt_fim
            )
            db.add(contrato)
            
        count += 1
        if count % batch_size == 0:
            db.commit()
            print(f"Inseridos {count} registros de {filepath}...")
            
    db.commit()
    f.close()
    print(f"Concluído arquivo {filepath}. Total inserido/atualizado: {count}")

def main():
    base_dir = r"c:\Users\Fred\Projetos\OpenPNCP\contratos"
    
    # Encontrar todas as pastas no padrão 2026XX_Compras
    pastas = sorted(glob.glob(os.path.join(base_dir, "2026*_Compras")))
    
    if not pastas:
        print(f"Nenhuma pasta encontrada em {base_dir}")
        return
        
    db = SessionLocal()
    
    for pasta in pastas:
        print(f"Processando pasta: {pasta}")
        # Encontrar o arquivo Compras correspondente
        basename = os.path.basename(pasta) # ex: 202601_Compras
        csv_file = os.path.join(pasta, f"{basename}.csv")
        
        if os.path.exists(csv_file):
            process_file(db, csv_file)
        else:
            print(f"Arquivo não encontrado: {csv_file}")
            
    db.close()
    print("Ingestão concluída com sucesso.")

if __name__ == "__main__":
    main()
