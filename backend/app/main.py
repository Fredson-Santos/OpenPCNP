from fastapi import FastAPI

app = FastAPI(
    title="OpenPNCP API",
    description="Observatório de Licitações Públicas - API REST para dados do PNCP",
    version="1.0.0",
)

@app.get("/health", tags=["Health"])
def health_check():
    """
    Endpoint para verificar o status da API.
    """
    return {
        "status": "ok",
        "message": "API OpenPNCP está rodando!",
    }


# comando para rodar: 
"""
cd backend 
uvicorn app.main:app --reload
"""
