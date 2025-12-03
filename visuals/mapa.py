# visuals/mapa.py
import folium
from folium.plugins import MiniMap
import branca.colormap as cm
import pandas as pd
import pygeoif

def csv_para_geojson(df):
    features = []
    
    for _, row in df.iterrows():
        geom = pygeoif.from_wkt(row["geometry"])  # correto

        features.append({
            "type": "Feature",
            "properties": {
                "EBAIRRNOMEOF": row["EBAIRRNOMEOF"],
                "votos_bairro": row["votos_bairro"],
                "inscritos": row["inscritos"],
                "conv_social": row["conv_social"],
                "negros": row["negros"],
                "Infancia": row["Infancia"],
                "Idosos": row["Idosos"],
            },
            "geometry": geom.__geo_interface__,  # GeoJSON direto
        })

    return {
        "type": "FeatureCollection",
        "features": features
    }

def display_mapa(df_filtrado, df_geo):
    geojson = csv_para_geojson(df_geo)
    recife_coords = [-8.014631171614337, -34.9134694067467]
    m = folium.Map(location=recife_coords, zoom_start=13, tiles="Cartodb dark_matter")

    MiniMap(toggle_display=True).add_to(m)
    linear = cm.linear.Blues_08.scale(
        vmin=df_filtrado["votos"].min(),
        vmax=df_filtrado["votos"].max())
    linear.add_to(m)

    # Resumo por bairro
    fgpb = folium.FeatureGroup(name="Resumo por Bairro", show=True)

    folium.GeoJson(
        geojson,
        name="Bairros",
        style_function=lambda f: {
            "color": "grey",
            "weight": 0.5,
            "fillOpacity": 0.2,
        },
        tooltip=folium.GeoJsonTooltip(
            fields=["EBAIRRNOMEOF", "votos_bairro", "inscritos",
                    'conv_social','negros','Infancia','Idosos'],
            
            aliases=["Bairro:", "Votos no bairro:", "Artistas:",
                     'Espaços:', 'Pessoas negras:', 'Crianças', 
                     'Idosos'],
        ),
    ).add_to(fgpb)
    
    m.add_child(fgpb)

    # Cluster geral
    for row in df_filtrado.itertuples():
        popup = folium.Popup(
            f"Votos no PSB: {row.votos} \n % Nosso: {row.pct_local}",
            parse_html=True,
            max_width="100",
        )
        folium.Circle(
            location=(row.latitude, row.longitude),
            radius = max((row.pct_local)*3, 2),
            color = "black",
            weight = 0.2,
            fillColor = linear(row.votos),
            fill = True,
            fillOpacity = 0.8,
            popup=popup,
        ).add_to(m)
        
    return m
