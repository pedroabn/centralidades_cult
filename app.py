import streamlit as st
import pandas as pd
import plotly.express as px
from core.carregar import load_comparativo_rpa, load_map, load_rpa, load_corr
from visuals.mapa import display_mapa
from streamlit_folium import st_folium

# =========================================================
# 🔧 CONFIGURAÇÃO DA PÁGINA
# =========================================================
st.set_page_config(
    page_title="Programa Cultura que Pertence",
    layout="wide",
    page_icon="📊"
)

# =========================================================
# 📦 FUNÇÃO DE CARREGAMENTO (CACHE)
# =========================================================
df_bairros = load_rpa()
df_map = load_map()
df_comparativo = load_comparativo_rpa()
df_corr = load_corr()

# =========================================================
# 📊 FUNÇÕES PARA GERAR GRÁFICOS
# =========================================================
#Gráfico de Artista por Voto
def grafico1(df):
    media = int(df['Votos_PSB'].mean())
    cores_itens = {
    "RPA2": "#f9c393", 
    "RPA3": "#0062ff"} 
    fig = px.scatter(df, x="Artistas", y="Votos_PSB", 
                     title="Quantidade de Artistas por quantidade de voto",
                     labels ={"Votos_PSB":"Votos"}
                     )
    fig.update_traces(
        marker_color=[cores_itens[p] for p in df['RPA']])
    fig.update_yaxes(
        tickformat=",")
    fig.update_xaxes(range=[0, 400])    
    fig.add_hline(
    y=media,
    line_dash="dash",
    line_color="grey",
    annotation_text=f"Média = {media:.2f}",
    annotation_position="top left")
    return fig

# Gráfico de Top 5 bairros sem participação do partido
def grafico2(df):
    fig = px.bar(df, x="longitude", y="latitude", title="Gráfico 3")
    return fig

# Gráfico mostrando a correlação
def grafico3(df):
    destacar = "inscritos"
    df["cor"] = df["corr"].apply(
    lambda x: "blue" if x == destacar else "gray")
    df['corr'] = df['corr'].rename()
    fig = px.bar(df, x="corr", y="valor", 
                 title="Taxa de correlação entre Votos e Indicadores Culturais",
                 color='cor', labels={'corr':'Correlações', 'valor':'Força'},
                 subtitle='Correlação forte entre votos e artistas',
                 text='valor')
    fig.update_layout(showlegend=False)
    return fig

# Barplot mostrando as diferenças de impacto de cada bairro
def grafico4(df):
    fig = px.histogram(df, x="valor", title="Gráfico 4")
    return fig

# Dado de cadunico por % de participação e tamanho de artistas
def grafico5(df):
    fig = px.box(df, x="bairro", y="valor", title="Gráfico 5")
    return fig

# Scatter mostrando a relação de negritude e artistas, com tamanho baseado em cadunico
def grafico6(df):
    fig = px.area(df, x="ano", y="valor", title="Gráfico 6")
    return fig

# =========================================================
# 🧱 LAYOUT DA PÁGINA
# =========================================================

st.title("📊 Decisão baseada em informação")

st.markdown("### 🔹 Filtros de visualização")

col_f1, col_f2, col_f3 = st.columns([1.5, 1.5, 1])

with col_f1:
    lista_bairros = ["TODOS"] + sorted(df_map["EBAIRRNOMEOF"].dropna().unique().tolist())
    bairro_select = st.selectbox("Selecione o bairro", lista_bairros)

with col_f2:
    rpa = ["RPA2 & RPA3"] + sorted(df_map["RPA"].dropna().unique().tolist())
    rpa_select = st.selectbox("RPA", rpa)

with col_f3:
    st.write("")
    st.write("")
    aplicar_filtro = st.button("Aplicar")

# filtros respondem mesmo sem clicar
if aplicar_filtro:
    pass

# APLICAÇÃO DOS FILTROS
df_filtrado = df_map.copy()
df_bairro_f = df_bairros.copy()

if bairro_select != "TODOS":
    df_filtrado = df_filtrado[df_filtrado["EBAIRRNOMEOF"] == bairro_select]
    df_bairro_f = df_bairro_f[df_bairro_f["EBAIRRNOMEOF"] == bairro_select]

if rpa_select != "RPA2 & RPA3":
    df_filtrado = df_filtrado[df_filtrado["RPA"] == rpa_select]
    df_bairro_f = df_bairro_f[df_bairro_f["RPA"] == rpa_select]

st.markdown("### 🔹 Sessão de Gráficos")

# ---- Linha 1 ----
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(grafico1(df_bairro_f), use_container_width=True)
with col2:
    st.plotly_chart(grafico3(df_filtrado), use_container_width=True)

# ---- Linha 2 ----
col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(grafico2(df_corr), use_container_width=True)
with col4:
    st.plotly_chart(grafico4(df_filtrado), use_container_width=True)

# ---- Linha 3 ----
col5, col6 = st.columns(2)
with col5:
    st.plotly_chart(grafico5(df_filtrado), use_container_width=True)
with col6:
    st.plotly_chart(grafico6(df_filtrado), use_container_width=True)

# ---- MAPA ----
st.markdown("### 🌍 Mapa Interativo")
mapa_final = display_mapa(df_filtrado)
st_folium(mapa_final, width=1200, height=600)
