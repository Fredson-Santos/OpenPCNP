from fastapi import APIRouter
from app.api.endpoints import licitacoes, orgaos, stats, ranking

api_router = APIRouter()
api_router.include_router(licitacoes.router, prefix="/licitacoes", tags=["licitacoes"])
api_router.include_router(orgaos.router, prefix="/orgaos", tags=["orgaos"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(ranking.router, prefix="/ranking", tags=["ranking"])
