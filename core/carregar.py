#%%
import basedosdados as bd
import pandas as pd
import geopandas as gpd
import streamlit as st
from pathlib import Path
#%%
# As bases de dados serão baseadas em local. A ideia, é trazer todos os dados de votação e buscar forma de criar relaões de impacto do
# partido/candidato com o local. Importante valorizar os dados que buscam evidenciar a participação do partido e dos candidatos, além de
# entender como é o perfil desses eleitores, fazendo no futuro, comparação entre correlação de variáveis com o partido com mais votos.
# Aqui é interessante as seguintes bases:
# Votos geral por local;
# Votos por partido no local;
# Votos por candidato no local;
# Perfil de votantes (Pegar dados dos bairros);


# Colocar cada coluna com um nome diferente
#%% Dados retirados pela API do Base dos Dados as bd
# billing_id = 'dados-eleicao-470222'

# @st.cache_data(ttl=86400)
# def load_cand():
#     candquery = """
#         SELECT
#             nome_urna,
#             sigla_partido,
#             idade,
#             genero,
#             raca,
#         FROM `basedosdados.br_tse_eleicoes.candidatos`
#         WHERE ano = 2024 AND id_municipio = '2611606' and cargo = 'vereador'
#         ORDER BY nome_urna
#     """
#     cadidatos = bd.read_sql(query = candquery, billing_project_id = billing_id)
#     df = pd.DataFrame(cadidatos)
#     return df

# @st.cache_data(ttl=86400)
# def load_vtsec():        
#     vtsquery = """
#         SELECT 
#         c.nome_urna as Nome_candidato,
#         r.secao as Secao,
#         r.zona as Zona,
#         SUM(r.votos) as Votos_recebidos
#         FROM
#         basedosdados.br_tse_eleicoes.resultados_candidato_secao as r
#         LEFT JOIN
#         basedosdados.br_tse_eleicoes.candidatos as c
#         ON (CAST(r.sequencial_candidato as string) = cast(c.sequencial as string) 
#             AND CAST(r.numero_candidato as string) = CAST(c.numero as string))
#         WHERE
#         r.ano = 2024 AND r.id_municipio = "2611606" and r.cargo = "vereador"
#         GROUP BY
#         Nome_candidato,
#         Secao,
#         Zona;
#     """
#     votosecao = bd.read_sql(query = vtsquery, billing_project_id = billing_id)
#     df = pd.DataFrame(votosecao)
#     return df

# def load_infoloc():        
#     locquery =   """
# SELECT
# zona,
# secao,
# comparecimento,
# votos_nominais,
# votos_brancos,
# votos_nulos,
# votos_legenda,
# (votos_nominais + votos_legenda) as votos_validos
# FROM `basedosdados.br_tse_eleicoes.detalhes_votacao_secao`
# WHERE ano = 2024 and id_municipio = "2611606" and cargo = "vereador"
# """
#     infovotacao = bd.read_sql(query = locquery, billing_project_id = billing_id)
#     df = pd.DataFrame(infovotacao)
#     return df

# @st.cache_data(ttl=86400)
# def load_partido():  
#     ptquery =     """
#         with Votos_Partidos as
#         (SELECT 
#         zona,
#         secao,
#         sigla_partido,
#         votos_nominais,
#         votos_legenda,
#         (votos_nominais + votos_legenda) as votos_totais
#         FROM `basedosdados.br_tse_eleicoes.resultados_partido_secao`
#         WHERE ano = 2024 and id_municipio = "2611606")
#         SELECT * FROM Votos_Partidos
#         """
#     votopartido = bd.read_sql(query = ptquery, billing_project_id = billing_id)
#     df = pd.DataFrame(votopartido)
#     return df
#%%
DATA_DIR = Path("dados")

def load_comparativo_rpa(path: str | None = None) -> pd.DataFrame:
    if path is None:
        path = DATA_DIR / "rpa_comparativo.csv"
    return pd.read_csv(path)

@st.cache_data
def load_rpa(path: str | None = None) -> pd.DataFrame:
    if path is None:
        path = DATA_DIR / "df_rpa.csv"
    df = pd.read_csv(path)
    df = df[df['RPA'].isin(['RPA2','RPA3'])]
    return df

@st.cache_data
def load_map(path: str | None = None) -> pd.DataFrame:
    if path is None:
        path = DATA_DIR / "vt_loc.csv"
    df = pd.read_csv(path)
    df = df[df['RPA'].isin(['RPA2','RPA3'])]
    return df

@st.cache_data
def load_corr(path: str | None = None) -> pd.DataFrame:
    if path is None:
        path = DATA_DIR / "correlations.csv"
    df = pd.read_csv(path)
    return df

@st.cache_data
def load_geomap(path: str | None = None) -> pd.DataFrame:
    if path is None:
        path = DATA_DIR / "df_pb.csv"
    df = pd.read_csv(path)
    return df