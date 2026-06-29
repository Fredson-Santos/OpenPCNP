from fastapi import FastAPI
from app.api.api import api_router
from fastapi_cache import FastAPICache
from fastapi_cache.backends.inmemory import InMemoryBackend
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Configuração do logger da aplicação
logger = logging.getLogger("app.main")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização do cache
    FastAPICache.init(InMemoryBackend(), prefix="fastapi-cache")
    logger.info("Cache em memória inicializado.")

    # Inicialização do agendador diário
    from apscheduler.schedulers.background import BackgroundScheduler
    from scripts.ingest import ingest_data

    def run_daily_sync():
        logger.info("Iniciando sincronização diária programada com o PNCP...")
        try:
            # Roda ingest_data sem parâmetros para realizar catch-up a partir da última data no BD
            ingest_data()
            logger.info("Sincronização diária programada concluída com sucesso.")
        except Exception as e:
            logger.error(f"Erro na execução da sincronização diária programada: {e}")

    scheduler = BackgroundScheduler()
    # Agenda a sincronização automática diariamente às 03:00 da manhã
    scheduler.add_job(run_daily_sync, "cron", hour=3, minute=0, id="daily_sync_job")
    scheduler.start()
    logger.info("Scheduler de sincronização diária iniciado (agendado para executar todos os dias às 03:00).")

    yield

    # Encerra o scheduler de forma limpa no desligamento
    scheduler.shutdown()
    logger.info("Scheduler de sincronização finalizado.")

app = FastAPI(
    title="OpenPNCP API",
    description="Observatório de Licitações Públicas - API REST para dados do PNCP",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
