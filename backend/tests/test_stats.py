import uuid
from datetime import datetime
from app.models.orgaos import Orgao
from app.models.licitacoes import Licitacao

def create_mock_data(db_session):
    o1 = Orgao(id=uuid.uuid4(), cnpj="111", nome="Orgao A", esfera="Federal", uf="DF")
    o2 = Orgao(id=uuid.uuid4(), cnpj="222", nome="Orgao B", esfera="Estadual", uf="SP")
    
    l1 = Licitacao(
        id=uuid.uuid4(), orgao_id=o1.id, numero_controle="01", objeto="obj1", 
        modalidade="Pregão", situacao="Aberta", valor_estimado=100.0,
        data_publicacao=datetime.now(), data_encerramento=datetime.now()
    )
    l2 = Licitacao(
        id=uuid.uuid4(), orgao_id=o1.id, numero_controle="02", objeto="obj2", 
        modalidade="Pregão", situacao="Aberta", valor_estimado=200.0,
        data_publicacao=datetime.now(), data_encerramento=datetime.now()
    )
    l3 = Licitacao(
        id=uuid.uuid4(), orgao_id=o2.id, numero_controle="03", objeto="obj3", 
        modalidade="Concorrência", situacao="Aberta", valor_estimado=300.0,
        data_publicacao=datetime.now(), data_encerramento=datetime.now()
    )
    
    db_session.add_all([o1, o2, l1, l2, l3])
    db_session.commit()
    return o1, o2

def test_read_stats_empty(client):
    response = client.get("/api/v1/stats/")
    assert response.status_code == 200
    data = response.json()
    assert data["total_licitacoes"] == 0
    assert data["valor_total"] == 0.0
    assert data["orgaos_ativos"] == 0

def test_read_stats_with_data(client, db_session):
    create_mock_data(db_session)
    response = client.get("/api/v1/stats/")
    assert response.status_code == 200
    data = response.json()
    assert data["total_licitacoes"] == 3
    assert data["valor_total"] == 600.0
    assert data["orgaos_ativos"] == 2

def test_evolucao_diaria(client, db_session):
    create_mock_data(db_session)
    response = client.get("/api/v1/stats/evolucao-diaria")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    if len(response.json()) > 0:
        assert "data" in response.json()[0]
        assert "quantidade" in response.json()[0]
