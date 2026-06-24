import uuid
from datetime import datetime
from app.models.orgaos import Orgao
from app.models.licitacoes import Licitacao

def create_mock_data(db_session):
    orgao_id = uuid.uuid4()
    orgao = Orgao(
        id=orgao_id,
        cnpj="11111111000111",
        nome="Órgão SP",
        esfera="Estadual",
        uf="SP"
    )
    
    orgao2_id = uuid.uuid4()
    orgao2 = Orgao(
        id=orgao2_id,
        cnpj="22222222000122",
        nome="Órgão RJ",
        esfera="Municipal",
        uf="RJ"
    )

    licitacao1 = Licitacao(
        id=uuid.uuid4(),
        orgao_id=orgao_id,
        numero_controle="001/2026",
        objeto="Aquisição de computadores para o laboratório",
        modalidade="Pregão Eletrônico",
        situacao="Aberta",
        valor_estimado=150000.00,
        data_publicacao=datetime(2026, 1, 1),
        data_encerramento=datetime(2026, 2, 1)
    )

    licitacao2 = Licitacao(
        id=uuid.uuid4(),
        orgao_id=orgao2_id,
        numero_controle="002/2026",
        objeto="Contratação de empresa para reforma",
        modalidade="Concorrência",
        situacao="Encerrada",
        valor_estimado=500000.00,
        data_publicacao=datetime(2026, 3, 1),
        data_encerramento=datetime(2026, 4, 1)
    )

    db_session.add(orgao)
    db_session.add(orgao2)
    db_session.add(licitacao1)
    db_session.add(licitacao2)
    db_session.commit()
    return licitacao1, licitacao2

def test_read_licitacoes_empty(client):
    response = client.get("/api/v1/licitacoes/")
    assert response.status_code == 200
    assert response.json()["data"] == []

def test_read_licitacoes_with_data(client, db_session):
    create_mock_data(db_session)
    response = client.get("/api/v1/licitacoes/")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 2

def test_read_licitacoes_filters(client, db_session):
    create_mock_data(db_session)

    # Filtro por UF
    resp = client.get("/api/v1/licitacoes/?uf=SP")
    assert len(resp.json()["data"]) == 1
    assert resp.json()["data"][0]["orgao"]["uf"] == "SP"

    # Filtro por Modalidade
    resp = client.get("/api/v1/licitacoes/?modalidade=Concorrência")
    assert len(resp.json()["data"]) == 1
    assert resp.json()["data"][0]["modalidade"] == "Concorrência"

    # Filtro por Situação
    resp = client.get("/api/v1/licitacoes/?situacao=Aberta")
    assert len(resp.json()["data"]) == 1
    assert resp.json()["data"][0]["situacao"] == "Aberta"

    # Filtro por Valor Mínimo
    resp = client.get("/api/v1/licitacoes/?valor_minimo=200000")
    assert len(resp.json()["data"]) == 1
    assert resp.json()["data"][0]["valor_estimado"] == 500000.0

def test_read_licitacoes_fts(client, db_session):
    create_mock_data(db_session)
    # Busca por "computadores"
    resp = client.get("/api/v1/licitacoes/?q=computadores")
    assert len(resp.json()["data"]) == 1
    assert "computadores" in resp.json()["data"][0]["objeto"]

def test_read_licitacoes_pagination(client, db_session):
    create_mock_data(db_session)
    resp = client.get("/api/v1/licitacoes/?page=1&page_size=1")
    assert len(resp.json()["data"]) == 1
    assert resp.json()["total"] == 2
    assert resp.json()["page"] == 1
    assert resp.json()["page_size"] == 1

def test_read_licitacao_by_id(client, db_session):
    l1, _ = create_mock_data(db_session)
    resp = client.get(f"/api/v1/licitacoes/{l1.id}")
    assert resp.status_code == 200
    assert resp.json()["objeto"] == l1.objeto

def test_read_licitacao_not_found(client):
    fake_id = uuid.uuid4()
    resp = client.get(f"/api/v1/licitacoes/{fake_id}")
    assert resp.status_code == 404

def test_read_licitacao_itens(client, db_session):
    l1, _ = create_mock_data(db_session)
    resp = client.get(f"/api/v1/licitacoes/{l1.id}/itens")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_read_licitacao_arquivos(client, db_session):
    l1, _ = create_mock_data(db_session)
    resp = client.get(f"/api/v1/licitacoes/{l1.id}/arquivos")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)

def test_read_licitacao_historico(client, db_session):
    l1, _ = create_mock_data(db_session)
    resp = client.get(f"/api/v1/licitacoes/{l1.id}/historico")
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
