# visuals/mapa.py
import folium
from folium.plugins import MiniMap
import branca.colormap as cm

def display_mapa(df):
    dfgb = df['votos'].max()
    recife_coords = [-8.05428, -34.88126]
    m = folium.Map(location=recife_coords, zoom_start=12, tiles="OpenStreetMap")

    MiniMap(toggle_display=True).add_to(m)
    linear = cm.linear.viridis.scale(
        vmin=df["votos"].min(),
        vmax=df["votos"].max())
    linear.add_to(m)
        
    for row in df.itertuples(index=False):
        popup = folium.Popup(
            f"Local: {row.local} \\n Votos:{row.votos}" ,
            parse_html=True,
            max_width="100",
        )
        folium.Circle(
            location=(row.latitude, row.longitude),
            radius = max(((row.votos / dfgb) * 300), 10),
            color = "black",
            weight = 0.2,
            fillColor = linear(row.votos),
            fill = True,
            fillOpacity = 0.8,
            popup=popup,
        ).add_to(m)

    return m
