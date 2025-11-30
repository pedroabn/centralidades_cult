#%%
import numpy as np
import pandas as pd
import re
from manipulacao.mapping import vencedores, RPA1,RPA2,RPA3,RPA4,RPA5,RPA6
from core.carregar import load_geo,load_votos, load_candcru
#%%
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

# %%
candidatocru = load_candcru()
zonascru = load_geo()
votoscru = load_votos()
zonas = zona_sec(zonascru)
zonas = load_cluster(zonas)
local_voto = votoscru.merge(zonas, on=['secao','zona'], how='left')
local_voto.to_csv('dados/vt_edit.csv')
votostotais = local_voto.groupby(['nome_candidato']).agg(
                        votos = ('votos_recebidos','sum')
                                 ).reset_index()
candidato = resultado(candidatocru)
candidato = candidato.merge(votostotais, right_on='nome_candidato',left_on='nome_urna', how='left')

#%%
voto_por_loc = (local_voto.merge(candidato, on='nome_candidato', how='left')
                    .groupby(['local','nome_candidato','EBAIRRNOMEOF','RPA',
                    'latitude','longitude','sigla_partido']).agg(
                    votos = ('votos_recebidos','sum')).reset_index())

#%%
partidos = pd.read_csv('dados\partidos.csv')
partidos = (partidos.merge(zonas, on=['secao','zona'], how='left')
            .groupby(['local','sigla_partido','EBAIRRNOMEOF','latitude','longitude','RPA'])
            .apply(lambda g: (g['votos_legenda'] + g['votos_nominais']).sum())
            .reset_index(name='votos'))
# %%
