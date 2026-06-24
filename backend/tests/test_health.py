def test_health_check(client):
    """Verifica se o endpoint de health check está respondendo corretamente."""
    response = client.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "rodando" in data["message"].lower()
