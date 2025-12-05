#%%
import requests
from pathlib import Path
import pandas as pd
import time
import numpy as np
import unicodedata

def buscar_bairro(lat, lon):
    """
    Busca o bairro a partir de latitude e longitude.
    Retorna None se lat/lon forem inválidos.
    """
    # Verifica se os valores são válidos
    if pd.isna(lat) or pd.isna(lon):
        return None
    url = "https://nominatim.openstreetmap.org/reverse"
    params = {
        'lat': lat,
        'lon': lon,
        'format': 'json',
        'addressdetails': 1}
    headers = {'User-Agent': 'GeoApp/1.0'} 
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            address = data.get('address', {})
            # Retorna o bairro
            bairro = (address.get('suburb') or 
                     address.get('neighbourhood') or 
                     address.get('quarter') or
                     address.get('district') or
                     None)
            print(f'Peguei o bairro')
            time.sleep(1.1)  # Pausa obrigatória entre requisições
            return bairro
    except Exception as e:
        print(f"Erro: {e}")
    return None

def limpar_acento(txt):
    if pd.isnull(txt):
        return txt
    txt = ''.join(ch for ch in unicodedata.normalize('NFKD', txt) 
        if not unicodedata.combining(ch))
    return txt

def api_tre():
    url = "https://apps.tre-pe.jus.br/locaisVotacao/locais"

    # Baixar JSON
    data = requests.get(url).json()

    # Converter para DataFrame
    df = pd.DataFrame(data)

    # Normalizar nomes das colunas (garantia)
    df.columns = df.columns.str.lower()
    # Filtrar Recife (como aparece no JSON real)
    df_recife = df[df["municipio"].str.upper() == "RECIFE"]

    # Selecionar colunas relevantes
    df_recife = df_recife[[
        "numerozona",
        "numerolocal",
        "nome",
        'cep', #Posso testar pegar direto pelo cep usando a API se der errado
        "bairro",
        "latitude",
        "longitude"
    ]].rename(columns={
        "numerozona": "zona",
        "numerolocal": "local_id",
        "nome": "nome_local"
    })
    
    df_recife['zona'] = df_recife['zona'].astype(str)
    
    # Ordenação padrão
    df_recife = df_recife.sort_values(["zona", "nome_local"]).reset_index(drop=True)
    df_recife['local_id'] = df_recife['local_id'].astype(str)
    df_recife['bairro_get'] = df_recife.apply(lambda row: buscar_bairro(row['latitude'], row['longitude']), axis=1)
    df_recife['bairro_get'] =  (df_recife['bairro_get'].str.upper()
                          .apply(limpar_acento)
                          .replace({'COHAB':'COHAB - IBURA DE CIMA',
                          'SITIO DOS PINTOS':'SITIO DOS PINTOS - SAO BRAS'}))   
    return df_recife

DATA_DIR = Path("dados")
def api_tse(path: str | None = None) -> pd.DataFrame:
    if path is None:
        path = DATA_DIR / "locais_tse.csv"
    df = pd.read_csv(path, encoding='latin1',dtype=str, sep=";")
    df = df[df['NM_MUNICIPIO']=="RECIFE"]
    df = df[["NR_ZONA","NR_SECAO","NR_LOCAL_VOTACAO"]]
    df.columns = df.columns.str.lower()
    df = df.rename(columns={
        "nr_zona": "zona",
        "nr_secao": "secao",
        "nr_local_votacao": "local_id"})
    df = df.groupby((['zona','secao','local_id']), as_index=False).sum().reset_index(names='drop')
    df = df.drop(columns={'drop'})
    return df

def loc_base():
    tse = api_tse()
    tre = api_tre()
    # merge usando zona + local_id
    df = tre.merge(
        tse,
        on=["zona", "local_id"],
        how="left",
        suffixes=("_tse", "_tre")
    )
    df['bairro_1'] = np.where(df['bairro_get'] != 0, df['bairro'], df['bairro_get'])
    # organizar 
    df = df.sort_values(["zona", "secao"]).reset_index(drop=True)
    df = df.fillna(0)

    return df

# %%
df = loc_base()
cols = list(df.columns)
# remove 'secao' da posição atual e insere na posição 1
cols.insert(1, cols.pop(cols.index("secao")))
df = df[cols]

df.to_json('dados/locais.json')
df.to_csv('locais_II.csv')