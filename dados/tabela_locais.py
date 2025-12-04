#%%
import requests
import zipfile
import io
from pathlib import Path
import pandas as pd


def api_tre():
    """
    Lê a API oficial do TRE-PE de locais de votação (2024)
    e retorna os locais apenas do município de Recife,
    contendo: zona, local, bairro, latitude, longitude.
    """

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

    # ordenar
    df = df.sort_values(["zona", "secao"]).reset_index(drop=True)

    return df

# %%
df = loc_base()

cols = list(df.columns)
# remove 'secao' da posição atual e insere na posição 1
cols.insert(1, cols.pop(cols.index("secao")))
df = df[cols]

df.to_json('dados/locais.json')
df.to_csv('locais.csv')