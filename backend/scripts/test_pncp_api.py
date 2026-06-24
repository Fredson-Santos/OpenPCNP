import requests
import json
from datetime import datetime, timedelta

def fetch_data():
    url = "https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao"
    # Modalidade 8: Pregão Eletrônico (usually)
    data_inicial = (datetime.now() - timedelta(days=2)).strftime("%Y%m%d")
    data_final = datetime.now().strftime("%Y%m%d")
    
    params = {
        "dataInicial": data_inicial,
        "dataFinal": data_final,
        "codigoModalidadeContratacao": 8,
        "pagina": 1,
        "tamanhoPagina": 10
    }
    print(f"Fetching {url} with params {params}")
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print(json.dumps(response.json(), indent=2, ensure_ascii=False))
        else:
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    fetch_data()
