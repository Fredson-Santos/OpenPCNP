from fastapi import FastAPI
from app.api.api import api_router
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="OpenPNCP API",
    description="Observatório de Licitações Públicas - API REST para dados do PNCP",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_private_network=True,
)

@app.on_event("startup")
async def startup():
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")

app.include_router(api_router, prefix="/api/v1")

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
