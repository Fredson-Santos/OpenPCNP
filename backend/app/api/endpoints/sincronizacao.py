from fastapi import APIRouter, BackgroundTasks
from pydantic import BaseModel
import sys
import os

# Adiciona o diretorio base para importar scripts
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))
from scripts.ingest import ingest_data

router = APIRouter()

class SyncRequest(BaseModel):
    data_inicial: str
    data_final: str

@router.post("/")
def sincronizar_pncp(request: SyncRequest, background_tasks: BackgroundTasks):
    """
    Aciona a sincronização do PNCP para uma faixa de datas específica.
    Roda em background para não travar a resposta da API.
    As datas devem estar no formato YYYYMMDD (ex: '20240101').
    """
    # Adiciona a tarefa ao background
    background_tasks.add_task(ingest_data, request.data_inicial, request.data_final)
    
    return {
        "status": "Sincronização iniciada",
        "mensagem": "A ingestão dos dados está ocorrendo em segundo plano.",
        "data_inicial": request.data_inicial,
        "data_final": request.data_final
    }
