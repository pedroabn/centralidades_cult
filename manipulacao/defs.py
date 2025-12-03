#%%
import numpy as np
import pandas as pd
import re
import streamlit as st
import unicodedata
from manipulacao.mapping import vencedores, RPA1,RPA2,RPA3,RPA4,RPA5,RPA6, bairros
from core.carregar import load_cand, load_partido,load_vtsec,load_infoloc, load_geo, load_infopb
#%%
def limpar_acento(txt):
    if pd.isnull(txt):
        return txt
    txt = ''.join(ch for ch in unicodedata.normalize('NFKD', txt) 
        if not unicodedata.combining(ch))
    return txt

def get_ze(valor):
    """Explode string de seções em lista de inteiros"""
    if pd.isna(valor): return []
    s = str(valor)
    parts = [p.strip() for p in re.split(r",|;|\n", s) if p.strip()]
    secoes = []
    for p in parts:
        m = re.match(r"^(\d{1,4})\s*(?:-|–|a|até)\s*(\d{1,4})$", p)
        if m:
            a, b = int(m.group(1)), int(m.group(2))
            secoes.extend(range(min(a,b), max(a,b)+1))
        else:
            num = re.sub(r"[^\d]", "", p)
            if num: secoes.append(int(num))
    return secoes

def zona_sec(df):
    df['CD_Local'] = df['CD_Local'].astype(int)
    linhas = []
    for _, r in df.iterrows():
        for s in get_ze(r["secao"]):
            linhas.append({
                "zona": int(r["zona"]),
                "secao": s,
                "CD_Local": int(r["CD_Local"]),
                "local": r["Nome do Local"],
                "endereco": r["Endereço"],
                "EBAIRRNOMEOF": r["Bairro"],
                "latitude": str(r["Latitude"]),
                "longitude": str(r["Longitude"])
            })
    zonas = pd.DataFrame(linhas)
    return zonas

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

# %%
def loc_zonas():
    zonascru = load_geo()
    dfcru = zona_sec(zonascru)
    df = load_cluster(dfcru)
    df['EBAIRRNOMEOF'] = df['EBAIRRNOMEOF'].map(bairros).fillna(df['EBAIRRNOMEOF'])
    return df

def vt_loc():
    dfz = loc_zonas()
    votoscru = load_vtsec()
    df = votoscru.merge(dfz, on=['secao','zona'], how='left')
    return df
# votos_local vai ser o nome do import com os dados de votação de cada candidato, em cada local


def perfil_cand():
    votos_local = vt_loc()
    candidatocru = load_cand()    
    votostotais = votos_local.groupby(['nome_candidato']).agg(
                            votos = ('votos_recebidos','sum')
                                    ).reset_index()
    candidato = resultado(candidatocru)
    df = candidato.merge(votostotais, right_on='nome_candidato',left_on='nome_urna', how='left')
    return df
# Candidato vai ser o nome do import com os dados de perfil de cada candidato

def infoloc():
    dfz = loc_zonas()    
    infolocru = load_infoloc()
    df = infolocru.merge(dfz, on=['secao','zona'], how='left')
    return df


def db_partido():
    dfz = infoloc()
    ptd = load_partido()   
    df = (ptd.merge(dfz, on = ['zona','secao'], how='left')
      .groupby(['local','zona','EBAIRRNOMEOF','RPA',
                'latitude','longitude','sigla_partido'])
      .agg( votos = ('votos_partido','sum'),
            comparecimento = ('comparecimento','mean')
            ).reset_index())
    df['pct_local'] = df['pct_local']
    return df


def info_pbvoto():
    infopb = load_infopb()
    ptd = db_partido()
    df = ptd.merge(infopb, on='EBAIRRNOMEOF', how='left')
    return df
# %%
