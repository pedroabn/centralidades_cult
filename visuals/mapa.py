# visuals/mapa.py
import folium
from folium.plugins import MiniMap
import branca.colormap as cm
import pandas as pd

def csv_para_geojson(df):
    features = []
    for _, row in df.iterrows():
        features.append({
            "type": "Feature",
            "properties": {
                "EBAIRRNOMEOF": row["EBAIRRNOMEOF"],
                "inscritos": row["inscritos"],
                "total_pessoas": row["total_pessoas"]
            },
            "geometry": {
                "type": "Point",
                "coordinates": [row["longitude"], row["latitude"]]
            }
        })
    
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    return geojson

def display_mapa(df_filtrado, df_geo, df_t):
    geojson = csv_para_geojson(df_geo)
    recife_coords = [-8.05428, -34.88126]
    m = folium.Map(location=recife_coords, zoom_start=10, tiles="Cartodb dark_matter")

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
            "color": "black",
            "weight": 0.5,
            "fillOpacity": 0.1,
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
            radius = max((row.pct_local), 10),
            color = "black",
            weight = 0.2,
            fillColor = linear(row.votos),
            fill = True,
            fillOpacity = 0.8,
            popup=popup,
        ).add_to(m)
    return m
