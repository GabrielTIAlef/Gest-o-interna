import requests
import json
import os
from datetime import datetime, timedelta
import calendar
import pandas as pd
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import logging
import time
from sqlalchemy import create_engine

url = "https:..."
headers = {
    "authorization": "JWT ...
    "Content-Type": "application/json"
}


ano_atual = datetime.now().year
ano_seguinte = ano_atual + 1


mes = datetime.now().month


periodos = [
    (f"{ano_atual}-01-01", f"{ano_atual}-06-30"),
    (f"{ano_atual}-07-01", f"{ano_atual}-12-31"),
    (f"{ano_seguinte}-01-01", f"{ano_seguinte}-06-30"),
    (f"{ano_seguinte}-07-01", f"{ano_seguinte}-12-31")
]

tarefas_filtradas = []

for inicio, fim in periodos:
    start_date = f"{inicio}T00:00:00-03:00"
    end_date = f"{fim}T23:59:59-03:00"

    payload = {
        "type": "CUSTOMER_TASK",
        "dates": {
            "startDate": start_date,
            "endDate": end_date
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    response.raise_for_status()
    data = response.json()

    for item in data:
        created_at = item.get("created_at", "")
        if created_at:
            try:
                dt = datetime.fromisoformat(created_at.replace("Z", "+00:00")).astimezone()
                if dt.year == datetime.now().year and dt.month == mes:
                    tarefas_filtradas.append({
                        "id": item.get("id"),
                        "created_at": item.get("created_at")
                    })
            except Exception as e:
                print(f"Erro ao processar data {created_at}: {e}")


print(f"Total de tarefas encontradas: {len(tarefas_filtradas)}")


headers = {
    "Authorization": "JWT ..."
    "Accept": "application/json"
}

dados_tarefas = []
chaves = ["id", "name", "created_by", "created_at"]
data_hoje = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

DB_CONFIG = {
    "usuario": "postgres",
    "senha": "...",
    "host": "localhost",
    "porta": "5432",
    "banco": "ProjetoImport"
}

def conectar_banco():
    url = f"postgresql+psycopg2://{DB_CONFIG['usuario']}:{DB_CONFIG['senha']}@{DB_CONFIG['host']}:{DB_CONFIG['porta']}/{DB_CONFIG['banco']}"
    engine = create_engine(url)
    try:
        with engine.connect() as conn:
            print("Conexão sucedida")
        return engine
    except Exception as e:
        print(f"Erro: {e}")
        raise

for tarefa in tarefas_filtradas:
    tarefa_id = tarefa.get("id")
    tarefa_data = tarefa["created_at"][:10]
    if tarefa_data != data_hoje:
        continue

    url = f"https://api.gestta.com.br/core/customer/task/{tarefa_id}"

    for tentativa in range(3):
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            break
        except requests.exceptions.RequestException as err:
            print(f"Tentativa {tentativa+1} falhou para tarefa {tarefa_id}: {err}")
            time.sleep(2)
    else:
        print(f"Todas as tentativas falharam para tarefa {tarefa_id}")
        continue

    if isinstance(data, dict):
        registro = {}
        for chave in chaves:
            if chave == "created_by":
                if isinstance(data.get("created_by"), dict) and "name" in data["created_by"]:
                    registro["created_by"] = data["created_by"]["name"]
                else:
                    registro["created_by"] = "Rotinas automáticas"
            elif chave == "created_at":
                registro["created_at"] = tarefa_data
            elif chave == "id":
                registro["id"] = tarefa_id
            else:
                registro[chave] = data.get(chave)
        dados_tarefas.append(registro)
    else:
        print(f"Resposta inesperada para o ID {tarefa_id}: {data}")

if dados_tarefas:
    df_novo = pd.DataFrame(dados_tarefas)
    df_novo = df_novo[chaves]
    df_novo["created_at"] = pd.to_datetime(df_novo["created_at"], errors='coerce').dt.strftime('%Y-%m-%d')

    try:
        engine = conectar_banco()

        with engine.connect() as conn:
            ids_existentes = pd.read_sql("SELECT id FROM criado_por", conn)["id"].tolist()

        df_novo = df_novo[~df_novo["id"].isin(ids_existentes)]

        if df_novo.empty:
            print("Nenhum novo dado")
        else:
            df_novo.to_sql("criado_por", engine, if_exists="append", index=False)
            print("Novos dados salvos no banco de dados")
    except Exception as e:
        print(f"Erro: {e}")
else:
    print("Nenhum dado foi encontrado para salvar.")

