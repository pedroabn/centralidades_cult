#%%
import numpy as np
import pandas as pd
import streamlit as st
import unicodedata
from shapely.geometry import Point
from utils.mapping import vencedores, RPA1,RPA2,RPA3,RPA4,RPA5,RPA6, bairros
from core.carregar import load_partido,load_infoloc, load_locais, load_infopb, load_bairros
#%%
def limpar_acento(txt):
    if pd.isnull(txt):
        return txt
    txt = ''.join(ch for ch in unicodedata.normalize('NFKD', txt) 
        if not unicodedata.combining(ch))
    return txt

def load_cluster(df):
    # Leitura do tse e divisão para cada seção e 
    df = df.fillna(0)
    df["RPA"] = np.select(
        [   df["EBAIRRNOMEOF"].isin(RPA1),
            df["EBAIRRNOMEOF"].isin(RPA2),
            df["EBAIRRNOMEOF"].isin(RPA3),
            df["EBAIRRNOMEOF"].isin(RPA4),
            df["EBAIRRNOMEOF"].isin(RPA5),
            df["EBAIRRNOMEOF"].isin(RPA6)],
            [   'RPA1',
                'RPA2',
                'RPA3',
                "RPA4",
                'RPA5',
                "RPA6"],
                default="Fora")
    return df 

def resultado(df):
    df["Resultado"] = np.select(
        [df["nome_urna"].isin(vencedores)],
            ['Eleito'],
                default="Não foi eleito")
    return df

def limpar_col(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(' ', '_')
        .str.replace('-', '_')
    )
    return df

def get_local(df, mapa,col):
    """
        Retorna o nome do bairro para cada linha do DataFrame `df`
        usando latitude e longitude, com base no GeoDataFrame `map`
        e os nomes de referência, com base na coluna "col".
        Parâmetros:
        - df: DataFrame contendo colunas 'Latitude' e 'Longitude'
        - map: GeoDataFrame com polígonos dos bairros e coluna 'bairro' (ou nome equivalente)
        - col: Coluna com o nome que vai receber
    """
    local = []
    for _, row in df.iterrows():
        lat = row["latitude"]
        lon = row["longitude"]
        try:
            lon = float(str(lon).replace(",", "."))
            lat = float(str(lat).replace(",", "."))            
            # Caso latitude ou longitude seja zero → retorna NaN
        except:
            if pd.isna(lat) or pd.isna(lon) or lat == 0 or lon == 0:
                local.append(np.nan)
            continue
        ponto = Point(lon, lat)  # Shapely espera (x, y) = (lon, lat)
        # Busca o polígono que contém o ponto
        match = mapa[mapa.geometry.contains(ponto)]
        if not match.empty:
            local.append(match.iloc[0][col])  # Ajustar para o nome real da coluna no 
        else:
            local.append(np.nan)
    return local

# %%
@st.cache_data(ttl=86400)
def loc_basico():
    db = load_locais()
    map_bairro = load_bairros()
    db['bairro_local'] = get_local(db,map_bairro,'bairro_local')
    db['EBAIRRNOMEOF'] = np.where(db['bairro_local'] != 0, db['bairro_1'], db['bairro_local'])
    db = db.drop(columns=['bairro_1','bairro','bairro_get','bairro_local']) #Revisão completa dos dados de bairros feita.
    db['secao'] = db['secao'].fillna(0)
    db['secao'] = db['secao'].astype(int).astype(str)
    db['zona'] = db['zona'].astype(int).astype(str)
    db['local_id'] = db['local_id'].astype(int).astype(str)
    df = load_cluster(db)
    return df

@st.cache_data(ttl=86400)
def info_loc():
    dfz = loc_basico()
    infoloc = load_infoloc()
    dfl = infoloc.merge(dfz, on=['secao','zona'], how='left')
    df = dfl.groupby((['zona','local_id', 'nome_local',
       'EBAIRRNOMEOF', 'latitude', 'longitude', 'RPA']), as_index=False).agg(
           comparecimento  =  ('comparecimento','sum'),
           votos_validos = ('votos_validos','sum')).reset_index()
    df = df.drop(columns=['index'])
    return df

@st.cache_data(ttl=86400)
def loc_votos():
    dfz = loc_basico()
    ptd = load_partido()   
    dfc = (ptd.merge(dfz, on = ['zona','secao'], how='left')
      .groupby(['zona','nome_local','EBAIRRNOMEOF','RPA',
                'latitude','longitude'])
      .agg(votos = ('votos_partido','sum'),
           votos_legenda = ('votos_legenda','sum'),
           votos_nominais = ('votos_nominais','sum')
            ).reset_index())
    # dfc['soma_teste'] = dfc['votos_legenda'] + dfc['votos_nominais'] Teste da soma vista em votos. Tudo certo
    df_iloc = info_loc()
    df = (dfc.merge(df_iloc, on=['nome_local','zona','EBAIRRNOMEOF',
                                 'latitude','longitude','RPA'], how='left'))
    df['pct_local'] =(df['votos']/ df['comparecimento'])*100
    return df

@st.cache_data(ttl=86400)
def info_pbvoto():
    infopb = load_infopb()
    infopb = infopb.drop(columns={'Unnamed: 0'})
    locvotos = loc_votos()
    ptd = (locvotos.groupby(['EBAIRRNOMEOF','RPA'])
      .agg(votos = ('votos','sum'),
           votos_legenda = ('votos_legenda','sum'),           
           votos_nominais = ('votos_nominais','sum'),
           qtd_locais = ('nome_local','count')).reset_index())
    df = ptd.merge(infopb, on='EBAIRRNOMEOF', how='left')
    return df