import folium

def create_map(route, start_location):

    dest_lat = route.iloc[-1]["latitude"]
    dest_lon = route.iloc[-1]["longitude"]

    center_lat = (start_location[0] + dest_lat) / 2
    center_lon = (start_location[1] + dest_lon) / 2

    m = folium.Map(location=[center_lat, center_lon], zoom_start=7)

    folium.Marker(start_location, popup="Start",
                  icon=folium.Icon(color="green")).add_to(m)

    points = [start_location]

    for _, row in route.iterrows():
        loc = [row["latitude"], row["longitude"]]
        points.append(loc)
        folium.Marker(loc, popup=row["name"]).add_to(m)

    folium.PolyLine(points, color="blue", weight=3).add_to(m)

    return m