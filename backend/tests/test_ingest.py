import pytest
from datetime import datetime
from scripts.ingest import parse_date, ingest_data
from app.models import Orgao, Licitacao, ItemLicitacao, ArquivoLicitacao, FaseLicitacao

def test_parse_date():
    assert parse_date("2023-10-18T14:30:00") == datetime(2023, 10, 18, 14, 30)
    assert parse_date(None) is None
    assert parse_date("") is None
    assert parse_date("invalid-date") is None

def test_ingest_data(monkeypatch, db_session):
    # Mock para fetch_pncp_data retornando dados simulados
    mock_response = {
        "data": [
            {
                "orgaoEntidade": {
                    "cnpj": "12345678000199",
                    "razaoSocial": "Órgão Teste",
                    "esferaId": "F"
                },
                "unidadeOrgao": {
                    "ufSigla": "SP"
                },
                "numeroControlePNCP": "12345678901234-1-000001/2023",
                "anoCompra": 2023,
                "sequencialCompra": 1,
                "objetoCompra": "Aquisição de computadores",
                "modalidadeNome": "Pregão Eletrônico",
                "situacaoCompraNome": "Divulgada no PNCP",
                "valorTotalEstimado": 150000.0,
                "dataPublicacaoPncp": "2023-10-18T14:30:00",
                "dataEncerramentoProposta": "2023-11-01T09:00:00"
            }
        ],
        "paginasRestantes": 0
    }
    
    mock_itens = [
        {
            "descricao": "Computador Desktop",
            "quantidade": 10,
            "valorUnitarioEstimado": 5000.0,
            "valorTotalEstimado": 50000.0
        }
    ]
    
    mock_arquivos = [
        {
            "tituloDocumento": "Edital.pdf",
            "linkAcesso": "http://pncp.gov.br/arquivo/1",
            "tipoDocumentoId": "1"
        }
    ]

    monkeypatch.setattr("scripts.ingest.fetch_pncp_data", lambda d1, d2, p: mock_response)
    monkeypatch.setattr("scripts.ingest.fetch_itens", lambda c, a, s: mock_itens)
    monkeypatch.setattr("scripts.ingest.fetch_arquivos", lambda c, a, s: mock_arquivos)
    monkeypatch.setattr("scripts.ingest.fetch_pncp_contratos", lambda d1, d2, p: {"data": [], "paginasRestantes": 0})
    monkeypatch.setattr("scripts.ingest.time.sleep", lambda s: None)
    
    # Precisamos mockar o db gerado dentro do ingest_data para usar o nosso in-memory db dos testes
    monkeypatch.setattr("scripts.ingest.SessionLocal", lambda: db_session)
    
    # Executa a ingestão
    ingest_data()
    
    # Verifica inserção do Órgão
    orgaos = db_session.query(Orgao).all()
    assert len(orgaos) == 1
    assert orgaos[0].cnpj == "12345678000199"
    assert orgaos[0].nome == "Órgão Teste"
    assert orgaos[0].esfera == "F"
    assert orgaos[0].uf == "SP"
    
    # Verifica inserção da Licitação
    licitacoes = db_session.query(Licitacao).all()
    assert len(licitacoes) == 1
    assert licitacoes[0].orgao_id == orgaos[0].id
    assert licitacoes[0].numero_controle == "12345678901234-1-000001/2023"
    assert licitacoes[0].objeto == "Aquisição de computadores"
    assert licitacoes[0].modalidade == "Pregão Eletrônico"
    assert licitacoes[0].valor_estimado == 150000.0

    # Verifica novos detalhes inseridos
    itens = db_session.query(ItemLicitacao).all()
    assert len(itens) == 1
    assert itens[0].descricao == "Computador Desktop"

    arquivos = db_session.query(ArquivoLicitacao).all()
    assert len(arquivos) == 1
    assert arquivos[0].nome == "Edital.pdf"

    fases = db_session.query(FaseLicitacao).all()
    assert len(fases) == 1
    assert fases[0].status == "Divulgada no PNCP"
    
    # Testar update rodando a ingestão novamente com um dado modificado
    mock_response_updated = {
        "data": [
            {
                "orgaoEntidade": {
                    "cnpj": "12345678000199",
                    "razaoSocial": "Órgão Teste",
                    "esferaId": "F"
                },
                "unidadeOrgao": {
                    "ufSigla": "SP"
                },
                "numeroControlePNCP": "12345678901234-1-000001/2023",
                "anoCompra": 2023,
                "sequencialCompra": 1,
                "objetoCompra": "Aquisição de computadores - Atualizado",
                "modalidadeNome": "Pregão Eletrônico",
                "situacaoCompraNome": "Encerrada",
                "valorTotalEstimado": 160000.0,
                "dataPublicacaoPncp": "2023-10-18T14:30:00",
                "dataEncerramentoProposta": "2023-11-01T09:00:00"
            }
        ],
        "paginasRestantes": 0
    }
    
    monkeypatch.setattr("scripts.ingest.fetch_pncp_data", lambda d1, d2, p: mock_response_updated)
    ingest_data()
    
    # Não deve criar um novo órgão nem uma nova licitação, mas sim atualizar
    assert db_session.query(Orgao).count() == 1
    assert db_session.query(Licitacao).count() == 1
    
    licitacao_atualizada = db_session.query(Licitacao).first()
    assert licitacao_atualizada.objeto == "Aquisição de computadores - Atualizado"
    assert licitacao_atualizada.situacao == "Encerrada"
    assert licitacao_atualizada.valor_estimado == 160000.0

    # As tabelas filhas devem ter sido recriadas e não duplicadas
    assert db_session.query(ItemLicitacao).count() == 1
    assert db_session.query(ArquivoLicitacao).count() == 1
    assert db_session.query(FaseLicitacao).count() == 1
