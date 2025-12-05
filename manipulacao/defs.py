#%%
import numpy as np
import pandas as pd
import re
import streamlit as st
import unicodedata
from manipulacao.mapping import vencedores, RPA1,RPA2,RPA3,RPA4,RPA5,RPA6, bairros
from core.carregar import load_partido,load_infoloc, load_locais, load_infopb
#%%
def limpar_acento(txt):
    if pd.isnull(txt):
        return txt
    txt = ''.join(ch for ch in unicodedata.normalize('NFKD', txt) 
        if not unicodedata.combining(ch))
    return txt

import pandas as pd
import re
from typing import List

def extrair_secoes(valor_secao: str) -> List[int]:
    """
    Extrai e expande seções a partir de string com formatos variados.    
    Args:
        valor_secao: String contendo seções
        
    Returns:
        Lista de números de seção únicos e ordenados
    """
    if pd.isna(valor_secao):
        return []
    
    secoes = []
    partes = re.split(r'[,;\n]', str(valor_secao))
    
    for parte in partes:
        parte = parte.strip()
        if not parte:
            continue
            
        # Detecta intervalos (ex: "100-105", "100 a 105", "100–105")
        intervalo = re.match(r'^(\d{1,4})\s*(?:-|–|a|até)\s*(\d{1,4})$', parte)
        if intervalo:
            inicio, fim = int(intervalo.group(1)), int(intervalo.group(2))
            secoes.extend(range(min(inicio, fim), max(inicio, fim) + 1))
        else:
            # Extrai apenas dígitos
            numeros = re.findall(r'\d+', parte)
            if numeros:
                secoes.append(int(numeros[0]))
    
    # Remove duplicatas e ordena
    return sorted(set(secoes))

def expandir_secoes_por_local(df: pd.DataFrame) -> pd.DataFrame:
    # Garante tipo correto do código do local
    df['Código do Local'] = df['Código do Local'].astype(int)
    
    linhas_expandidas = []
    
    for _, registro in df.iterrows():
        secoes_local = extrair_secoes(registro['Seções'])
        
        for secao in secoes_local:
            linhas_expandidas.append({
                'zona': registro['Zona'],
                'secao': secao,
                'CD_Local': int(registro['Código do Local']),
                'local': registro['Nome do Local'],
                'endereco': registro['Endereço'],
                'EBAIRRNOMEOF': registro['Bairro'],
                'latitude': float(registro['Latitude']) if pd.notna(registro['Latitude']) else None,
                'longitude': float(registro['Longitude']) if pd.notna(registro['Longitude']) else None
            })
    
    df_expandido = pd.DataFrame(linhas_expandidas)
    df_expandido['zona'] = df_expandido['zona'].astype(str)
    df_expandido['secao'] = df_expandido['secao'].astype(str)
    
    # Validação básica
    if df_expandido.empty:
        raise ValueError("Nenhuma seção foi extraída do DataFrame")
    
    return df_expandido

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
def loc_basico():
    db = load_locais()
    db['EBAIRRNOMEOF'] =np.where((db['bairro_get'])!= 0, db['bairro_get'], db['bairro'])
    db = db.drop(columns=['bairro_get','bairro'])
    db['EBAIRRNOMEOF'] = db['EBAIRRNOMEOF'].map(bairros).fillna(db['EBAIRRNOMEOF']).str.upper().apply(limpar_acento)
    db['secao'] = db['secao'].fillna(0)
    db['secao'] = db['secao'].astype(int).astype(str)
    db['zona'] = db['zona'].astype(int).astype(str)
    db['local_id'] = db['local_id'].astype(int).astype(str)
    df = load_cluster(db)
    return df

def info_loc():
    dfz = loc_basico()
    infoloc = load_infoloc()
    dfl = infoloc.merge(dfz, on=['secao','zona'], how='left')
    df = dfl.groupby((['zona','local_id', 'nome_local',
       'EBAIRRNOMEOF', 'latitude', 'longitude', 'RPA']), as_index=False).agg(
           comparecimento  =  ('comparecimento','sum'),
           votos_validos = ('votos_validos','sum')).reset_index()
    return df

def loc_votos():
    dfz = loc_basico()
    ptd = load_partido()   
    dfc = (ptd.merge(dfz, on = ['zona','secao'], how='left')
      .groupby(['zona','nome_local','EBAIRRNOMEOF','RPA',
                'latitude','longitude'])
      .agg( votos = ('votos_partido','sum'),
           votos_nominais = ('votos_nominais','sum')
            ).reset_index())
    df_iloc = info_loc()
    df = (dfc.merge(df_iloc, on=['nome_local','zona','EBAIRRNOMEOF',
                                 'latitude','longitude','RPA'], how='left'))
    df['pct_local'] =(df['votos']/ df['comparecimento'])*100
    return df

def info_pbvoto():
    infopb = load_infopb()
    infopb = infopb.drop(columns={'Unnamed: 0'})
    locvotos = loc_votos()
    ptd = (locvotos.groupby(['EBAIRRNOMEOF','RPA'])
      .agg(votos = ('votos','sum'),
           votos_nominais = ('votos_nominais','sum'),
           qtd_locais = ('nome_local','count')
            ).reset_index())
    df = ptd.merge(infopb, on='EBAIRRNOMEOF', how='left')
    return df