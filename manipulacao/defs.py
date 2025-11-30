#%%
import numpy as np
import pandas as pd
import re
from manipulacao.mapping import vencedores, RPA1,RPA2,RPA3,RPA4,RPA5,RPA6
from core.carregar import load_vtsec,load_cand, load_partidos_vt, load_locais
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
candidatocru = load_cand()
zonascru = load_locais()
votoscru = load_vtsec()
zonas = zona_sec(zonascru)
zonas = load_cluster(zonas)
#%%
votos_local = votoscru.merge(zonas, on=['secao','zona'], how='left')
# votos_local vai ser o nome do import com os dados de votação de cada candidato, em cada local
#%%
votostotais = votos_local.groupby(['nome_candidato']).agg(
                        votos = ('votos_recebidos','sum')
                                 ).reset_index()
candidato = resultado(candidatocru)
candidato = candidato.merge(votostotais, right_on='nome_candidato',left_on='nome_urna', how='left')
# Candidato vai ser o nome do import com os dados de perfil de cada candidato
#%%
df = load_partidos_vt()
partidos = (df.merge(zonas, on=['secao','zona'], how='left')
            .groupby(['local','sigla_partido','EBAIRRNOMEOF','latitude','longitude','RPA'])
            .agg(
                votos_nominais = ('votos_nominais','sum'),
                votos_legenda = ('votos_legenda','sum'),
                votos_partido = ('votos_totais','sum')
            )
            .reset_index())
# Partidos vai ser o nome do import com os dados de votação de cada partido, em cada local
# %%
