#%%
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from manipulacao.defs import load_partido, load_infoloc, loc_zonas, limpar_acento
from core.carregar import load_infopb
from manipulacao.mapping import bairros, RPA1,RPA2,RPA3,RPA4,RPA5,RPA6
#%%
dfl = load_infoloc()
dfp = load_partido()
dfmap = loc_zonas()
infopb = load_infopb()
#%%
dflc = dfl.copy()
dfpc = dfp.copy()
dfmapc = dfmap.copy()
infopbc = infopb.copy()
# %%
dflc = dflc[['zona', 'secao', 'comparecimento']]

df = dfpc.merge(dflc, on=['zona','secao'], how='left')
df['pct_local'] = round((df['votos_totais'] / df['comparecimento'])*100,2)
# %%
dfmapc['zona'] = dfmapc['zona'].astype(str)
dfmapc['secao'] = dfmapc['secao'].astype(str)
dfmapc = dfmapc[['zona','secao', 'EBAIRRNOMEOF','latitude','longitude','RPA']]
dfmapc['EBAIRRNOMEOF'] = dfmapc['EBAIRRNOMEOF'].map(bairros)
#%%
df_pb = df.merge(dfmapc, on=['zona','secao'], how='left')
df_pbm = df_pb.groupby(['EBAIRRNOMEOF','sigla_partido'], as_index=False).agg(
    votos_bairro = ('votos_totais','sum'))
df_psb = df_pbm[df_pbm['sigla_partido'] == 'PSB']
# %%
infopbc['EBAIRRNOMEOF'] = infopbc['EBAIRRNOMEOF'].apply(limpar_acento).str.upper()
df_psb['EBAIRRNOMEOF'] = df_psb['EBAIRRNOMEOF'].str.upper().replace({'COHAB':'COHAB - IBURA DE CIMA',
                                                                'SÍTIO DOS PINTOS':'SÍTIO DOS PINTOS - SÃO BRÁS',
                                                                })
#%%
df_star = infopbc.merge(df_psb, on='EBAIRRNOMEOF', how='left')
df_star['RPA'] = np.select(
    [   df_star["EBAIRRNOMEOF"].isin(RPA1),
        df_star["EBAIRRNOMEOF"].isin(RPA2),
        df_star["EBAIRRNOMEOF"].isin(RPA3),
        df_star["EBAIRRNOMEOF"].isin(RPA4),
        df_star["EBAIRRNOMEOF"].isin(RPA5),
        df_star["EBAIRRNOMEOF"].isin(RPA6)],
        [   'RPA1',
            'RPA2',
            'RPA3',
            "RPA4",
            'RPA5',
            "RPA6"],
            default="Fora")
cols = ['qtd_quadra', 'qtd_atelie', 'qtd_danca','qtd_Pracas','n_escolas']
df_star['conv_social'] = df_star[cols].fillna(0).sum(axis=1)
# %%
df_num = df_star.select_dtypes(include=['number'])
df_num = df_num.dropna(subset={'votos_bairro'})
corr_inscritos = df_num.corr(method='spearman')['votos_bairro'].drop('votos_bairro').sort_values(ascending=False)
corr_inscritos2 = df_num.corr(method='pearson')['votos_bairro'].drop('votos_bairro').sort_values(ascending=False)
#%%
%matplotlib inline

plt.figure(figsize=(10, 8))
sns.barplot(
    x=corr_inscritos.values,
    y=corr_inscritos.index,
    palette="coolwarm",
)
plt.title("Correlação da coluna 'inscritos' com outras variáveis", fontsize=8, pad=15)
plt.xlabel("Coeficiente de Correlação (spearman)")
plt.ylabel("Variáveis")
plt.xlim(-0.25, 1)  # faixa típica de correlação
plt.grid(axis="x", linestyle="--", alpha=0.5)
plt.tight_layout()
plt.show()

fig = sns.pairplot(df_star[['votos_bairro','Feminino','Infancia', 'inscritos',
                          'Idosos','total_pessoas','RPA'
                          ]], hue = 'RPA')
# %%
# %% Correlação e testes
corr1 = round(df_star['votos_bairro'].corr(df_star['total_pessoas'], method="spearman"),2)*100
corr2 = round(df_star['votos_bairro'].corr(df_star['qtd_empresas_total'], method="spearman"),2)*100
corr3 = round(df_star['votos_bairro'].corr(df_star['Branco'], method="spearman"),2)*100
corr4 = round(df_star['votos_bairro'].corr(df_star['Preto'], method="spearman"),2)*100
corr5 = round(df_star['votos_bairro'].corr(df_star['inscritos'], method="spearman"),2)*100
corr6 = round(df_star['votos_bairro'].corr(df_star['total_casas'], method="spearman"),2)*100
corr7 = round(df_star['votos_bairro'].corr(df_star['qtd_Pracas'], method="spearman"),2)*100
corr8 = round(df_star['votos_bairro'].corr(df_star['pct_homem'], method="spearman"),2)*100
corr9 = round(df_star['votos_bairro'].corr(df_star['pct_mulher'], method="spearman"),2)*100
corr10 =round(df_star['votos_bairro'].corr(df_star['Infancia'], method="spearman"),2)*100
corr11 =round(df_star['votos_bairro'].corr(df_star['Idosos'], method="spearman"),2)*100
corr12 =round(df_star['votos_bairro'].corr(df_star['Pardo'], method="spearman"),2)*100
corr13 =round(df_star['votos_bairro'].corr(df_star['conv_social'], method="spearman"),2)*100
corr14 =round(df_star['votos_bairro'].corr(df_star['n_escolas'], method="spearman"),2)*100

# %% tabela de correlação
tbl_corr = {'corr':["total_pessoas",'qtd_empresas_total','Branco',"Preto",
                    "inscritos","total_casas","qtd_Pracas","pct_homem",'pct_mulher',
                    "Infancia","Idosos","Pardo",'conv_social','n_escolas'],
            'valor':[corr1,corr2, corr3,corr4, corr5 ,corr6,
                     corr7,corr8, corr9,corr10,corr11,corr12,
                     corr13, corr14]}
tbl_corr = pd.DataFrame(tbl_corr)
# %%
df_star
