import folium

def create_map(df, start_location):
    m = folium.Map(location=start_location, zoom_start=6)

    folium.Marker(start_location, tooltip="Start", icon=folium.Icon(color="green")).add_to(m)

    coords = [start_location]

    for _, row in df.iterrows():
        loc = (row["latitude"], row["longitude"])
        coords.append(loc)
        folium.Marker(loc, tooltip=row["name"]).add_to(m)

    folium.PolyLine(coords, color="blue").add_to(m)

    return m