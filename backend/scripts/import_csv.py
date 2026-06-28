import os
import sys
import csv
from datetime import datetime
import locale

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import SessionLocal
from app.models import Orgao, Licitacao, Fornecedor, Contrato, ItemLicitacao

def parse_date(date_str: str):
    if not date_str:
        return None
    date_str = date_str.strip()
    try:
        if len(date_str) > 10:
            return datetime.strptime(date_str, "%d/%m/%Y %H:%M:%S")
        else:
            return datetime.strptime(date_str, "%d/%m/%Y")
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

def import_data():
    db = SessionLocal()
    
    licitacoes_file = r"c:\Users\Fred\Projetos\OpenPNCP\LicitacaoExportacao.csv"
    contratos_file = r"c:\Users\Fred\Projetos\OpenPNCP\ContratoExportacao.csv"

    print("Importando licitações...")
    try:
        with open(licitacoes_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                nome_orgao = row.get("UnidadeEmitente", "Desconhecido")
                orgao = db.query(Orgao).filter(Orgao.nome == nome_orgao).first()
                if not orgao:
                    orgao = Orgao(nome=nome_orgao, esfera="Federal")
                    db.add(orgao)
                    db.flush()

                num_controle = row.get("Numero_Processo_ou_Edital")
                if not num_controle:
                    continue
                
                licitacao = db.query(Licitacao).filter(Licitacao.numero_controle == num_controle).first()
                if not licitacao:
                    licitacao = Licitacao(
                        orgao_id=orgao.id,
                        numero_controle=num_controle,
                        objeto=row.get("Objeto"),
                        modalidade=row.get("Tipo_de_Licitacao"),
                        situacao=row.get("Situacao_Licitacao"),
                        data_publicacao=parse_date(row.get("DataHoraAbertura"))
                    )
                    db.add(licitacao)
                    db.flush()
    except UnicodeDecodeError:
        print("Erro de encoding UTF-8, tentando ISO-8859-1 para licitações")
        with open(licitacoes_file, mode='r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f)
            for row in reader:
                nome_orgao = row.get("UnidadeEmitente", "Desconhecido")
                orgao = db.query(Orgao).filter(Orgao.nome == nome_orgao).first()
                if not orgao:
                    orgao = Orgao(nome=nome_orgao, esfera="Federal")
                    db.add(orgao)
                    db.flush()

                num_controle = row.get("Numero_Processo_ou_Edital")
                if not num_controle:
                    continue
                
                licitacao = db.query(Licitacao).filter(Licitacao.numero_controle == num_controle).first()
                if not licitacao:
                    licitacao = Licitacao(
                        orgao_id=orgao.id,
                        numero_controle=num_controle,
                        objeto=row.get("Objeto"),
                        modalidade=row.get("Tipo_de_Licitacao"),
                        situacao=row.get("Situacao_Licitacao"),
                        data_publicacao=parse_date(row.get("DataHoraAbertura"))
                    )
                    db.add(licitacao)
                    db.flush()
    db.commit()

    print("Importando contratos e fornecedores...")
    try:
        with open(contratos_file, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                process_contrato_row(db, row)
    except UnicodeDecodeError:
        print("Erro de encoding UTF-8, tentando ISO-8859-1 para contratos")
        with open(contratos_file, mode='r', encoding='iso-8859-1') as f:
            reader = csv.DictReader(f)
            for row in reader:
                process_contrato_row(db, row)
    db.commit()
    db.close()
    print("Carga CSV finalizada com sucesso.")

def process_contrato_row(db, row):
    num_processo = row.get("Numero_do_Processo")
    if not num_processo:
        return
        
    licitacao = db.query(Licitacao).filter(Licitacao.numero_controle == num_processo).first()
    if not licitacao:
        return
        
    ni = row.get("CNPJ_ou_CPF_do_Fornecedor")
    if not ni:
        return
        
    fornecedor = db.query(Fornecedor).filter(Fornecedor.ni == ni).first()
    if not fornecedor:
        fornecedor = Fornecedor(
            ni=ni,
            nome=row.get("Nome_do_Fornecedor", "Desconhecido")
        )
        db.add(fornecedor)
        db.flush()
        
    num_contrato = row.get("Numero_do_Contrato")
    contrato = db.query(Contrato).filter(
        Contrato.licitacao_id == licitacao.id, 
        Contrato.numero == num_contrato,
        Contrato.fornecedor_id == fornecedor.id
    ).first()
    
    if not contrato:
        contrato = Contrato(
            licitacao_id=licitacao.id,
            fornecedor_id=fornecedor.id,
            numero=num_contrato,
            objeto=row.get("Objeto_do_Contrato"),
            valor_contrato=parse_currency(row.get("Valor_Original_do_Contrato")),
            vigencia_inicio=parse_date(row.get("Periodo_de_Vigencia_Inicio")),
            vigencia_fim=parse_date(row.get("Periodo_de_Vigencia_Fim"))
        )
        db.add(contrato)
        
        # O CSV de Licitação não possui o valor, então atualizamos com a soma dos contratos.
        licitacao.valor_estimado = (licitacao.valor_estimado or 0.0) + contrato.valor_contrato
        
        db.flush()

    # Adicionar item se houver
    item_desc = row.get("Item_Descricao")
    if item_desc:
        # Check if item exists to avoid duplication if file repeats
        existing_item = db.query(ItemLicitacao).filter(
            ItemLicitacao.licitacao_id == licitacao.id,
            ItemLicitacao.descricao == item_desc[:200]
        ).first()
        
        if not existing_item:
            qtd = parse_currency(row.get("Item_Quantidade_Contratada"))
            val_uni = parse_currency(row.get("Item_Valor_Unitario"))
            novo_item = ItemLicitacao(
                licitacao_id=licitacao.id,
                descricao=item_desc[:200],
                quantidade=qtd,
                valor_unitario=val_uni,
                valor_total=qtd * val_uni
            )
            db.add(novo_item)

if __name__ == '__main__':
    import_data()
