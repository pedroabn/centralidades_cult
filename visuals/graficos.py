import plotly.express as px

# Definindo funções
def graph_candidatos(df):
    # Organizando dados
    df = df.sort_values(by='votos', ascending=False)
    df = df.head(10)
    df = df.sort_values(by='votos')

    #Definindo cores
    cores_partidos = {
    'PCO':'white',
    "MDB": "blue",
    "NOVO": "orange",
    "PSD": "cyan",
    "PDT": "pink",
    "PODE": "coral",
    "REPUBLICANOS": "gold",
    "CIDADANIA": "brown",
    'MOBILIZA':'salmon',
    "PL": "darkgreen",
    "PV": "lime",
    "PP": "teal",
    "PRD": "green",
    "SOLIDARIEDADE": "olive",
    "PRTB": "navy",
    "UP": "maroon",
    "PT": "red",
    "REDE": "indigo",
    "PSOL": "purple",
    "AGIR": "skyblue",
    "PSDB": "cornflowerblue",
    "PSB": "yellow",
    "UNIÃO": "darkblue",
    "AVANTE": "darkred",
    "PSTU": "darkorange",
    "PC do B": "darkviolet",
    "DC":'white'
    }

    # Organizando o Plot
    fig = px.bar(df, x='votos', y='nome_candidato',
    hover_data="sigla_partido",title=f"Top 10 mais votados", 
    labels ={"nome_candidato":"","votos":"Quantidade de votos"})

    fig.update_traces(marker_color=[cores_partidos[p] for p in df['sigla_partido']])
    fig.update_layout(title_x=0.2)
    
    return fig

def graph_candidatos_chapa(df, df_candidato):
    # Organizando dados
    sigla_partido = df_candidato["sigla_partido"].iloc[0]
    df = df[df["sigla_partido"] == sigla_partido]
    df = df.groupby(["nome_candidato","genero"],as_index=False)['votos'].sum()
    df = df.sort_values(by='votos', ascending=False)
    df = df.head(10)
    df = df.sort_values(by='votos')
    
    # Definindo as cores
    cores_genero = {"masculino":"blue","feminino":"pink"}

    # Organizando plot
    fig = px.bar(df, x='votos', y='nome_candidato', orientation='h', 
    hover_data="genero",title=f"Top 10 mais votados do {sigla_partido}",
     labels ={"nome_candidato":"", "votos":"Quantidade de votos"})

    fig.update_traces(marker_color=[cores_genero[p] for p in df['genero']])
    fig.update_layout(title_x=0.2)
    return fig

def graph_bairros(df):
    # Organizando dados
    df = df.groupby(['nome_candidato',"RPA","EBAIRRNOMEOF"],as_index=False)['votos_recebidos'].sum()
    df = df.sort_values(by='votos_recebidos', ascending=False)
    df = df.head(10)
    df = df.sort_values(by='votos_recebidos')

    # Definindo as cores
    cores_itens = {
    "RPA1": "#1f77b4",  # Azul
    "RPA2": "#ff7f0e",  # Laranja
    "RPA3": "#2ca02c",  # Verde
    "RPA4": "#d62728",  # Vermelho
    "RPA5": "#9467bd",  # Roxo
    "RPA6": "#8c564b"}  # Marrom    
    # Organizando plot
    fig = px.area(df, x='votos_recebidos', y='EBAIRRNOMEOF', orientation = 'h',
    hover_data="RPA",title=f"Top 10 bairro do(a) candidato(a)", 
     labels ={"EBAIRRNOMEOF":"", "votos_recebidos":"Quantidade de votos"})

    fig.update_traces(marker_color=[cores_itens[p] for p in df['RPA']])
    fig.update_layout(title_x=0.2)

    return fig

def graph_locais(df):
    # Organizando dados
    df = df.groupby(['nome_candidato',"local","EBAIRRNOMEOF","RPA"],as_index=False)['votos_recebidos'].sum()
    df = df.sort_values(by='votos_recebidos', ascending=False)
    df = df.head(10)
    df = df.sort_values(by='votos_recebidos')

    # Definindo as cores
    # Definindo as cores
    cores_itens = {
    "RPA1": "#1f77b4",  # Azul
    "RPA2": "#ff7f0e",  # Laranja
    "RPA3": "#2ca02c",  # Verde
    "RPA4": "#d62728",  # Vermelho
    "RPA5": "#9467bd",  # Roxo
    "RPA6": "#8c564b"}  # Marrom    
    # Organizando plots
    fig = px.bar(df, x='votos_recebidos', y='local', orientation = 'h',
    hover_data=["EBAIRRNOMEOF","RPA"],title=f"Top 10 locais de votação",
     labels ={"local":"", "votos_recebidos":"Votos"})

    fig.update_traces(marker_color=[cores_itens[p] for p in df['RPA']])
    fig.update_layout(title_x=0.2)
    
    return fig
