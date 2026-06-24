from fastapi import APIRouter
from app.api.endpoints import licitacoes, orgaos

api_router = APIRouter()
api_router.include_router(licitacoes.router, prefix="/licitacoes", tags=["licitacoes"])
api_router.include_router(orgaos.router, prefix="/orgaos", tags=["orgaos"])
