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

def test_ranking_orgaos(client, db_session):
    o1, o2 = create_mock_data(db_session)
    response = client.get("/api/v1/ranking/orgaos")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["orgao_id"] == str(o1.id)
    assert data[0]["total_licitacoes"] == 2
    assert data[1]["orgao_id"] == str(o2.id)
    assert data[1]["total_licitacoes"] == 1

def test_ranking_estados(client, db_session):
    create_mock_data(db_session)
    response = client.get("/api/v1/ranking/estados")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["uf"] == "DF"
    assert data[0]["total_licitacoes"] == 2
    assert data[1]["uf"] == "SP"
    assert data[1]["total_licitacoes"] == 1

def test_ranking_modalidades(client, db_session):
    create_mock_data(db_session)
    response = client.get("/api/v1/ranking/modalidades")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["modalidade"] == "Pregão"
    assert data[0]["total_licitacoes"] == 2
    assert data[1]["modalidade"] == "Concorrência"
    assert data[1]["total_licitacoes"] == 1
