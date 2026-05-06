import streamlit as st
import pandas as pd
import os
from streamlit_geolocation import streamlit_geolocation

from src.route_planner import RoutePlanner
from src.map_utils import create_map
from src.utils import estimate_travel_time, estimate_fuel_cost
from src.risk_engine import TravelRiskEngine
from src.weather import get_weather

st.set_page_config(page_title="Weekend Trip Recommender", layout="wide")
st.title("🌍 Weekend Trip Recommender")

# -------- LOAD DATA --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "data", "places.csv")

data = pd.read_csv(file_path, encoding="latin1")
data.columns = data.columns.str.strip().str.lower()
data = data.rename(columns={"popular_destination": "name"})

data["latitude"] = pd.to_numeric(data["latitude"], errors="coerce")
data["longitude"] = pd.to_numeric(data["longitude"], errors="coerce")
data = data.dropna(subset=["latitude", "longitude"])

# -------- START --------
st.subheader("📍 Starting Point")

start_option = st.radio(
    "Choose starting point:",
    ["Use My Current Location", "Select from Destinations"]
)

gps_location = None
loc = streamlit_geolocation()

if loc and loc.get("latitude"):
    lat, lon = loc["latitude"], loc["longitude"]
    if 6 <= lat <= 38 and 68 <= lon <= 98:
        gps_location = (lat, lon)

if start_option == "Use My Current Location":
    if gps_location is None:
        st.error("Enable GPS access")
        st.stop()
    start_location = gps_location
else:
    start_name = st.selectbox("Select start", sorted(data["name"].unique()))
    row = data[data["name"] == start_name].iloc[0]
    start_location = (row["latitude"], row["longitude"])

# -------- DESTINATION --------
st.subheader("🎯 Destination")

destination_name = st.selectbox("Choose destination", sorted(data["name"].unique()))
row = data[data["name"] == destination_name].iloc[0]
destination = (row["latitude"], row["longitude"])

# -------- SETTINGS --------
st.sidebar.header("Trip Settings")
num_stops = st.sidebar.slider("Nearby Places", 3, 10, 6)
num_people = st.sidebar.number_input("People", 1, 20, 2)

# -------- PLAN --------
if st.button("Plan Trip"):

    planner = RoutePlanner(data)

    nearby_places = planner.get_nearby_places(destination, num_stops)

    total_distance = planner.get_distance(start_location, destination)
    travel_time = estimate_travel_time(total_distance)
    fuel_cost = estimate_fuel_cost(total_distance)

    weather = get_weather(destination[0], destination[1])

    # -------- BEST TIME --------
    temp = weather["temp"]
    if temp > 32:
        best_time = "October to February"
    elif temp < 20:
        best_time = "March to June"
    else:
        best_time = "September to March"

    risk_engine = TravelRiskEngine()
    risk_score = risk_engine.total_risk(weather, total_distance, num_stops)
    risk_level = risk_engine.risk_level(risk_score)

    # -------- OUTPUT --------
    st.subheader("📊 Trip Summary")

    col1, col2, col3 = st.columns(3)
    col1.metric("Distance (km)", f"{total_distance:.2f}")
    col2.metric("Travel Time (hrs)", f"{travel_time:.2f}")
    col3.metric("Fuel Cost (₹)", f"{fuel_cost:.2f}")

    st.metric("Travelers", num_people)

    st.subheader("🌦 Weather")
    st.write(f"{weather['temp']}°C - {weather['condition']}")

    st.subheader("🧭 Best Time to Visit")
    st.success(best_time)

    st.subheader("⚠️ Risk Analysis")
    st.metric("Risk Score", risk_score)
    st.metric("Risk Level", risk_level)

    st.subheader("📍 Places to Visit Near Destination")

    threshold = nearby_places["final_score"].quantile(0.7)

    for _, r in nearby_places.iterrows():
        tag = "⭐ Must Visit" if r["final_score"] >= threshold else ""
        st.write(f"{r['name']} — {r['dist_dest']:.1f} km {tag}")

    # -------- MAP --------
    route_df = pd.DataFrame([
        {"name": "Start", "latitude": start_location[0], "longitude": start_location[1]},
        {"name": destination_name, "latitude": destination[0], "longitude": destination[1]}
    ])

    trip_map = create_map(route_df, start_location)
    st.components.v1.html(trip_map._repr_html_(), height=600)