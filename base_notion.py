import requests
import pandas as pd
import json
from datetime import datetime
import os
import time

NOTION_API_URL = "https:..."
NOTION_PAGE_URL = "https:..."
NOTION_VERSION = "2022-06-28"
DATABASE_ID = "28ed16..."
NOTION_TOKEN = "ntn_..."

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": NOTION_VERSION,
    "Content-Type": "application/json"
}

def buscar_paginas(database_id):
    url = NOTION_API_URL.format(database_id)
    all_pages = []
    has_more = True
    start_cursor = None

    while has_more:
        payload = {"page_size": 100}
        if start_cursor:
            payload["start_cursor"] = start_cursor

        response = requests.post(url, headers=HEADERS, json=payload)
        data = response.json()

        if response.status_code != 200:
            print(f"Erro: {response.status_code} - {data}")
            break

        all_pages.extend(data.get('results', []))

        has_more = data.get('has_more', False)
        start_cursor = data.get('next_cursor', None)

    return all_pages


def obter_titulo_relacionado(page_id, cache):
    if page_id in cache:
        return cache[page_id]

    url = NOTION_PAGE_URL.format(page_id)
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        data = response.json()
        props = data.get('properties', {})
        titulo = ''

        for prop in props.values():
            if prop.get('type') == 'title':
                titulo_raw = prop.get('title', [])
                if titulo_raw:
                    titulo = titulo_raw[0].get('plain_text', '')
                break

        cache[page_id] = titulo
        return titulo
    else:
        cache[page_id] = 'Erro ao obter'
        return 'Erro ao obter'


def formatar_data(data_iso):
    try:
        data_obj = datetime.strptime(data_iso, '%Y-%m-%d')
        return data_obj.strftime('%d/%m/%Y')
    except:
        return 'Sem dado'


def extrair_dados(paginas):
    dados = []
    cache_relacoes = {}

    for idx, page in enumerate(paginas, 1):
        props = page.get('properties', {})

        codigo_dominio_raw = props.get('Código Domínio', {}).get('title')
        if codigo_dominio_raw and isinstance(codigo_dominio_raw, list) and len(codigo_dominio_raw) > 0:
            codigo_dominio = codigo_dominio_raw[0].get('plain_text', 'Sem dado')
        else:
            codigo_dominio = 'Sem dado'

        nome_fantasia_raw = props.get('Nome Fantasia', {}).get('rich_text')
        if nome_fantasia_raw and isinstance(nome_fantasia_raw, list) and len(nome_fantasia_raw) > 0:
            nome_fantasia = nome_fantasia_raw[0].get('plain_text', 'Sem dado')
        else:
            nome_fantasia = 'Sem dado'

        competencia_raw = props.get('1ª Competência IZZI', {}).get('date')
        competencia_data = competencia_raw.get('start') if competencia_raw else None
        competencia = formatar_data(competencia_data) if competencia_data else 'Sem dado'

        estado_raw = props.get('Estado', {}).get('select')
        estado = estado_raw.get('name') if estado_raw else 'Sem dado'

        gestao_nomes = []
        relacoes = props.get('Gestão de Clientes', {}).get('relation')
        if relacoes and isinstance(relacoes, list):
            for rel in relacoes:
                rel_id = rel.get('id')
                if rel_id:
                    nome_rel = obter_titulo_relacionado(rel_id, cache_relacoes)
                    gestao_nomes.append(nome_rel)
                    time.sleep(0.05)

        gestao_clientes = "; ".join(gestao_nomes) if gestao_nomes else 'Sem dado'

        print(f"[{idx}/{len(paginas)}] Código: {codigo_dominio} | Gestão: {gestao_clientes}")

        dados.append({
            'Código Domínio': codigo_dominio,
            'Gestão de Clientes': gestao_clientes,
            'Nome Fantasia': nome_fantasia,
            '1ª Competência IZZI': competencia,
            'Estado': estado
        })

    return dados

def exportar_csv(data, filename):
    df = pd.DataFrame(data)
    df = df.drop_duplicates()
    df.to_csv(filename, index=False, encoding='utf-8-sig')
    print(f"CSV exportado com {len(df)} registros: {filename}")

#exportar JSON
def exportar_json(data, filename):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"JSON exportado com {len(data)} registros: {filename}")


if __name__ == "__main__":
    try:
        paginas = buscar_paginas(DATABASE_ID)
        print(f"Total de páginas encontradas: {len(paginas)}")

        dados = extrair_dados(paginas)

     
        pasta_destino = r"C:\Users\Gabriel Alef\Projeto\dados"
        os.makedirs(pasta_destino, exist_ok=True)
      
        caminho_csv = os.path.join(pasta_destino, "base_notion.csv")
        caminho_json = os.path.join(pasta_destino, "base_notion.json")

        exportar_csv(dados, caminho_csv)
        exportar_json(dados, caminho_json)

        print("Processo concluído com sucesso!")

    except Exception as e:
        print(f"Erro: {e}")
