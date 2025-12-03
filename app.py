import streamlit as st
import plotly.express as px
from core.carregar import load_comparativo_rpa, load_map, load_rpa, load_corr, load_geomap
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
df_local = load_map()
df_comparativo = load_comparativo_rpa()
df_corr = load_corr()
df_geomapa = load_geomap()
# =========================================================
# 📊 FUNÇÕES PARA GERAR GRÁFICOS
# =========================================================
#Gráfico de Artista por Voto
def grafico1(df):
    media = int(df['Votos_PSB'].mean())
    df = df.rename(columns={'EBAIRRNOMEOF':'Bairro'})
    cores_itens = {
    "RPA2": "#f9c393", 
    "RPA3": "#0062ff"} 
    fig = px.scatter(df, x="Artistas", y="Votos_PSB", 
                     title="Quantidade de Artistas por quantidade de voto",
                     labels ={"Votos_PSB":"Votos"},
                     hover_data='Bairro'
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

def grafico2(df):
    df = df.sort_values(by='inscritos', ascending=True)
    df = df.groupby(['RPA','sigla_partido'], as_index=False).agg(
        Artistas = ('inscritos','sum'),
        conv_social = ('conv_social','sum'),
        votos_bairro = ('votos_bairro','sum')
    )    
    cores_itens = {
        "RPA2": "#f9c393", 
        "RPA3": "#0062ff"} 
    fig = px.bar(df, y='Artistas', x='RPA', orientation='v', 
    hover_data=["votos_bairro",'conv_social'] ,title=f" Quantitativo de Artistas na {rpa_select}",
    subtitle='Os números mostram uma boa base de fazedores de cultura',
    text='Artistas',)
    fig.update_traces(
        marker_color=[cores_itens[p] for p in df['RPA']])    
    fig.update_layout(
        title_x=0.2,
        title_subtitle_font_lineposition='over'  
    )
    return fig

# Gráfico mostrando a correlação
def grafico3(df):
    df = df.sort_values(by='valor', ascending = False)
    destacar = "Artistas"
    df["cor"] = df["corr"].apply(
    lambda x: "blue" if x == destacar else "gray")
    fig = px.bar(df, x="corr", y="valor", 
                 title="Taxa de correlação entre Votos e Indicadores Culturais",
                 color='cor', labels={'corr':'Correlações', 'valor':'Força'},
                 subtitle='Correlação forte entre votos e artistas',
                 text='valor',
                 hover_data='valor')
    fig.update_layout(showlegend=False)
    return fig

# Plot de gráfico de barra 100% com participação da RPA por partido
def grafico4(df):
    df = df.copy()
    destacar = ["PL", "PSD"]
    df = df[df['sigla_partido']!= "PSB"]
    df = df.groupby(['RPA','sigla_partido'], as_index=False).agg(
        comparecimento = ('comparecimento','sum'),
        votos_totais = ('votos_totais','sum')
    )
    db = df[df['RPA'].isin(['RPA2','RPA3'])]
    db['pct'] = ((db['votos_totais']/db['comparecimento'])*100).round()
    db['sigla_partido'] = db['sigla_partido'].where(
    db['sigla_partido'].isin(destacar),
    'Outros')
    cores_destacar = ["green", "blue"]
    color_map = {p: c for p, c in zip(destacar, cores_destacar)}
    color_map["Outros"] = "gray"

    # Organizando o Plot
    fig = px.scatter(db, x="votos_totais", y="pct", 
                     title="Quantidade de votos por comparecimento",
                     subtitle='Precisamos observar os nossos adversários políticos',
                     size='pct',
                     color='sigla_partido',
                     color_discrete_map=color_map,
                     labels ={"pct":"Participação",'votos_totais':'Votos'},
                     custom_data=["sigla_partido", "RPA", "pct"],)
    fig.update_layout(title_x=0.2,
                      title_subtitle_font_lineposition='over')
    fig.update_yaxes(tickformat=".2f", ticksuffix="%")
    
    fig.update_traces(
    hovertemplate=
        "<b>Partido:</b> %{customdata[0]}<br>" +
        "<b>RPA:</b> %{customdata[1]}<br>" +
        "<b>Pct:</b> %{customdata[2]:.2f}%<br>" +
        "<extra></extra>"
                        )
    return fig

# =========================================================
# 🧱 LAYOUT DA PÁGINA
# =========================================================

st.title("📊 Decisão baseada em informação")

st.markdown(" Toda a escolha deve ser baseada na metodologia, e construída sendo fundamentada pelo framework criado.")
st.page_link("https://docs.google.com/document/d/1XE6YAs84X5LuonRStvP7PYYPF5GT74Qz34U7Tm0yK7U/edit?usp=sharing", label="Leia a metodologia", icon="📄")

st.markdown("### 🔹 Filtros de visualização")

col_f1, col_f2 = st.columns(2)

with col_f1:
    lista_bairros = ["TODOS"] + sorted(df_local["EBAIRRNOMEOF"].dropna().unique().tolist())
    bairro_select = st.selectbox("Selecione o bairro", lista_bairros)

with col_f2:
    rpa = ["RPA2 & RPA3"] + sorted(df_local["RPA"].dropna().unique().tolist())
    rpa_select = st.selectbox("RPA", rpa)


# APLICAÇÃO DOS FILTROS
df_filtrado = df_local.copy()
df_bairro_f = df_bairros.copy()
df_geo = df_geomapa.copy()

if bairro_select != "TODOS":
    df_filtrado = df_filtrado[df_filtrado["EBAIRRNOMEOF"] == bairro_select]
    df_bairro_f = df_bairro_f[df_bairro_f["EBAIRRNOMEOF"] == bairro_select]
    df_geo = df_geo[df_geo["EBAIRRNOMEOF"] == bairro_select]
    df_comparativo = df_comparativo[df_comparativo["EBAIRRNOMEOF"] == bairro_select]

if rpa_select != "RPA2 & RPA3":
    df_filtrado = df_filtrado[df_filtrado["RPA"] == rpa_select]
    df_bairro_f = df_bairro_f[df_bairro_f["RPA"] == rpa_select]
    df_geo = df_geo[df_geo["RPA"] == rpa_select]
    df_comparativo = df_comparativo[df_comparativo["RPA"] == rpa_select]

st.markdown("### 🔹 Sessão de Gráficos")

# ---- Linha 1 ----
col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(grafico3(df_corr), use_container_width=True)
with col2:
    st.plotly_chart(grafico2(df_geo), use_container_width=True)

# ---- Linha 2 ----
col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(grafico1(df_bairro_f), use_container_width=True)
with col4:
    st.plotly_chart(grafico4(df_comparativo), use_container_width=True)

# ---- MAPA ----
st.markdown("### 🌍 Mapa Interativo")
mapa_final = display_mapa(df_filtrado,df_geo)
st_folium(mapa_final, width=1200, height=600)
