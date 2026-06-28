from fastapi import APIRouter
from app.api.endpoints import licitacoes, orgaos, stats, ranking, anomalias, sincronizacao

api_router = APIRouter()
api_router.include_router(licitacoes.router, prefix="/licitacoes", tags=["licitacoes"])
api_router.include_router(orgaos.router, prefix="/orgaos", tags=["orgaos"])
api_router.include_router(stats.router, prefix="/stats", tags=["stats"])
api_router.include_router(ranking.router, prefix="/ranking", tags=["ranking"])
api_router.include_router(anomalias.router, prefix="/anomalias", tags=["anomalias"])
api_router.include_router(sincronizacao.router, prefix="/sincronizar", tags=["sincronizar"])
