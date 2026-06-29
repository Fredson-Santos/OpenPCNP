import pytest
from unittest.mock import MagicMock

def test_sincronizar_pncp_com_datas(client, monkeypatch):
    """
    Testa a inicialização da sincronização enviando datas específicas.
    """
    mock_ingest_data = MagicMock()
    monkeypatch.setattr("app.api.endpoints.sincronizacao.ingest_data", mock_ingest_data)
    
    payload = {
        "data_inicial": "20240101",
        "data_final": "20240102"
    }
    
    response = client.post("/api/v1/sincronizar/", json=payload)
    
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "Sincronização iniciada"
    assert res_data["data_inicial"] == "20240101"
    assert res_data["data_final"] == "20240102"
    
    # Verifica se a tarefa foi enviada ao background com as datas informadas
    mock_ingest_data.assert_called_once_with("20240101", "20240102")

def test_sincronizar_pncp_automatico(client, monkeypatch):
    """
    Testa se o envio de dados vazios ou nulos aciona o modo catch-up automático.
    """
    mock_ingest_data = MagicMock()
    monkeypatch.setattr("app.api.endpoints.sincronizacao.ingest_data", mock_ingest_data)
    
    # Payload vazio para acionar datas automáticas
    payload = {}
    
    response = client.post("/api/v1/sincronizar/", json=payload)
    
    assert response.status_code == 200
    res_data = response.json()
    assert res_data["status"] == "Sincronização iniciada"
    assert res_data["data_inicial"] == "Automática (última data)"
    assert res_data["data_final"] == "Automática (hoje)"
    
    # Verifica se a tarefa foi enviada ao background com None (catch-up automático)
    mock_ingest_data.assert_called_once_with(None, None)
