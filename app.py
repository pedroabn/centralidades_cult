#%%
# Importando bibliotecas #
import streamlit as st
from streamlit_folium import st_folium
from visuals.mapa import display_mapa
from core.header import dict_candidato
from core.dados_pt import dados_pt
from core.dados_voto import dados_votocao
from core.carregar import load_cand, load_vt_edit, load_map, load_partidos_vt
from visuals.graficos import graph_locais, graph_bairros, graph_candidatos, graph_candidatos_chapa
#%%
df_cand = load_cand()
df_votos = load_vt_edit()
df_map = load_map()
df_partidos = load_partidos_vt()

with st.sidebar:
    st.title("Resultado Eleições 2024 - Recife")
    candidato = st.selectbox("Candidato (a)",df_cand["nome_urna"].sort_values().unique())
    RPA = st.selectbox("RPA",["TODOS","RPA1","RPA2","RPA3","RPA4","RPA5","RPA6"])

#dados de voto
df_filtrado_VotoPorLocal = df_votos.copy()
#dados candidato
df_candidato = df_cand.copy()
#usado no mapa
df_map = df_map.copy()
#dados de candidato + partido
df_candidato_partidos = df_cand.copy()

#Dados filtrados pelo input do usuário
df_filtrado_VotoPorLocal = df_filtrado_VotoPorLocal[df_filtrado_VotoPorLocal['nome_candidato'] == candidato]
df_candidato = df_candidato[df_candidato["nome_urna"] == candidato]
df_map = df_map[df_map['nome_candidato']== candidato]

if RPA == "TODOS":
    pass
else:
    df_filtrado_VotoPorLocal = df_votos[df_votos["RPA"] == RPA]
    df_map = df_map[df_map["RPA"] == RPA]
    
    
# FICHA DO CANDIDATO
# Criando a função para obtenção dos dados
header = dict_candidato(df_candidato)
st.markdown(f"#  Dados da eleição de: {candidato}")
st.markdown(
    f"""
<style>
.table-full {{
    width: 100%;
    border-collapse: collapse;
}}
.table-full th, .table-full td {{
    border: 0.5px solid #ddd;
    padding: 8px;
}}
.table-full th {{
    font-weight: bold;
    text-align: center;
}}
.table-full td:nth-child(2) {{
    text-align: center;
}}
</style>

<table class="table-full">
    <tr><th>Métrica</th><th>Valor</th></tr>
    <tr><td>Número de votos</td><td>{header["VOTOS"]}</td></tr>
    <tr><td>Partido</td><td>{header["PARTIDO"]}</td></tr>
    <tr><td>Idade</td><td>{header["IDADE"]} anos</td></tr>
    <tr><td>Gênero</td><td>{header["GÊNERO"]}</td></tr>
    <tr><td>Raça</td><td>{header["RAÇA"]}</td></tr>
    <tr><td>Eleito?</td><td>{header["RESULTADO"]}</td></tr>
</table>
""",
    unsafe_allow_html=True,
)

# MAPA DE VOTAÇÃO
mapa = display_mapa(df_map)
st.markdown(f"### :round_pushpin: **Mapa de votação {candidato}**")
st_folium(mapa, width=800, height=700)

# Dados de votação
infovoto = dados_votocao(df_map)

infopartido = dados_pt(df_partidos, df_candidato)

st.markdown("###  :ballot_box_with_ballot: **Dados eleitorais & Partidários**")
#Definindo estrutura de exposição
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.metric(
            label = "Total de votos",
            value = infovoto["Total de votos"]
        )
    with st.container(border=True):    
        st.metric(
            label = "% votos em relação à chapa",
            value = infopartido["Percentual votos"]        
        )

with col2:
    with st.container(border=True):
        st.metric(
            label = "Mediana dos votos",
            value = infovoto["Mediana"],
       )
    with st.container(border=True):
        st.metric(
            label = "Total votos da chapa",
            value = infopartido["Votos totais da chapa"]
        )
        
# GRÁFICOS
st.markdown("""\n""")
st.markdown("### :bar_chart: **Gráficos**")

# Plotando gráficos
col1, col2 = st.columns(2)

plot_votos_candidatos = graph_candidatos(df_cand)
plot_bairros = graph_bairros(df_filtrado_VotoPorLocal)
with col1:
    with st.container(border=True):
        st.plotly_chart(plot_votos_candidatos, use_container_width=True)
    with st.container(border=True):
        st.plotly_chart(plot_bairros, use_container_width=True)


plot_votos_chapa = graph_candidatos_chapa(df_candidato_partidos, df_candidato)
plot_locais = graph_locais(df_filtrado_VotoPorLocal)
with col2:
        with st.container(border=True):
            st.plotly_chart(plot_votos_chapa, use_container_width=True)
            
        with st.container(border=True):
            st.plotly_chart(plot_locais, use_container_width=True)