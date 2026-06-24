import uuid
from app.models.orgaos import Orgao

def test_read_orgaos_empty(client):
    response = client.get("/api/v1/orgaos/")
    assert response.status_code == 200
    assert response.json()["data"] == []

def test_read_orgaos_with_data(client, db_session):
    orgao = Orgao(
        id=uuid.uuid4(),
        cnpj="12345678000199",
        nome="Órgão Teste",
        esfera="Federal",
        uf="DF"
    )
    db_session.add(orgao)
    db_session.commit()

    response = client.get("/api/v1/orgaos/")
    assert response.status_code == 200
    data = response.json()["data"]
    assert len(data) == 1
    assert data[0]["nome"] == "Órgão Teste"
    assert data[0]["uf"] == "DF"

def test_read_orgao_by_id(client, db_session):
    orgao_id = uuid.uuid4()
    orgao = Orgao(
        id=orgao_id,
        cnpj="98765432000199",
        nome="Órgão Específico",
        esfera="Estadual",
        uf="SP"
    )
    db_session.add(orgao)
    db_session.commit()

    response = client.get(f"/api/v1/orgaos/{orgao_id}")
    assert response.status_code == 200
    assert response.json()["nome"] == "Órgão Específico"

def test_read_orgao_not_found(client):
    orgao_id = uuid.uuid4()
    response = client.get(f"/api/v1/orgaos/{orgao_id}")
    assert response.status_code == 404

def test_autocomplete_orgaos(client, db_session):
    orgao = Orgao(
        id=uuid.uuid4(),
        cnpj="99999999000199",
        nome="Prefeitura de Teste",
        esfera="Municipal",
        uf="MG"
    )
    db_session.add(orgao)
    db_session.commit()

    response = client.get("/api/v1/orgaos/autocomplete?q=teste")
    assert response.status_code == 200
    assert len(response.json()) >= 1
    assert "Teste" in response.json()[0]["nome"]
