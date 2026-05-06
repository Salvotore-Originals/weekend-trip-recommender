import streamlit as st
import pandas as pd
import os
from streamlit_geolocation import streamlit_geolocation

from src.route_planner import RoutePlanner
from src.map_utils import create_map
from src.utils import estimate_travel_time, estimate_fuel_cost
from src.risk_engine import TravelRiskEngine
from src.weather import get_weather  # now Open-Meteo based

# ---------------- CONFIG ----------------
st.set_page_config(page_title="Weekend Trip Recommender", layout="wide")
st.title("🌍 Weekend Trip Recommender")
st.success("🤖 ML-powered recommendations enabled")

# ---------------- DATA ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(BASE_DIR, "data", "places.csv")

data = pd.read_csv(file_path, encoding="latin1")
data.columns = data.columns.str.strip().str.lower()
data = data.rename(columns={"popular_destination": "name"})

data["latitude"] = pd.to_numeric(data["latitude"], errors="coerce")
data["longitude"] = pd.to_numeric(data["longitude"], errors="coerce")
data = data.dropna(subset=["latitude", "longitude"])

# ---------------- START ----------------
st.subheader("📍 Starting Point")

start_option = st.radio(
    "Choose starting point:",
    ["Use My Current Location", "Select from Destinations"]
)

gps_location = None
loc = streamlit_geolocation()

if loc and loc.get("latitude") is not None:
    lat, lon = loc["latitude"], loc["longitude"]
    if 6 <= lat <= 38 and 68 <= lon <= 98:
        gps_location = (lat, lon)

if start_option == "Use My Current Location":
    if gps_location is None:
        st.error("❌ Enable GPS access")
        st.stop()
    start_location = gps_location
else:
    start_name = st.selectbox("Select start", sorted(data["name"].dropna().unique()))
    row = data[data["name"] == start_name].iloc[0]
    start_location = (row["latitude"], row["longitude"])

# ---------------- DESTINATION ----------------
st.subheader("🎯 Destination")

destination_name = st.selectbox("Choose destination", sorted(data["name"].dropna().unique()))
row = data[data["name"] == destination_name].iloc[0]
destination = (row["latitude"], row["longitude"])

# ---------------- SETTINGS ----------------
st.sidebar.header("🧭 Trip Settings")

num_stops = st.sidebar.slider("📌 Stops", 1, 10, 5)
num_people = st.sidebar.number_input("👥 People", 1, 20, 2)

# ---------------- PLAN ----------------
if st.button("🚀 Plan Trip"):

    planner = RoutePlanner(data)

    route_places = planner.get_places_along_route(
        start_location,
        destination,
        num_stops
    )

    # ---------------- DISTANCE ----------------
    prev = start_location
    total_distance = 0

    for _, r in route_places.iterrows():
        curr = (r["latitude"], r["longitude"])
        total_distance += planner.get_distance(prev, curr)
        prev = curr

    total_distance += planner.get_distance(prev, destination)

    # ---------------- METRICS ----------------
    travel_time = estimate_travel_time(total_distance)
    fuel_cost = estimate_fuel_cost(total_distance)

    # ---------------- WEATHER (OPEN-METEO - NO API KEY) ----------------
    weather = get_weather(destination[0], destination[1])

    # ---------------- AI RISK ENGINE ----------------
    risk_engine = TravelRiskEngine()

    risk_score = risk_engine.total_risk(
        weather,
        total_distance,
        num_stops
    )

    risk_level = risk_engine.risk_level(risk_score)

    # ---------------- OUTPUT ----------------
    st.subheader("📊 Trip Summary")

    col1, col2, col3 = st.columns(3)

    col1.metric("📏 Distance (km)", f"{total_distance:.2f}")
    col2.metric("⏱ Travel Time (hrs)", f"{travel_time:.2f}")
    col3.metric("⛽ Fuel Cost (₹)", f"{fuel_cost:.2f}")

    st.metric("👥 Travelers", num_people)

    # ---------------- WEATHER ----------------
    st.subheader("🌦 Destination Weather")

    st.write(f"📍 {destination_name}")

    st.write(f"🌡 Temperature: {weather['temp']}°C")
    st.write(f"🌤 Condition: {weather['condition']}")

    # ---------------- AI INTELLIGENCE ----------------
    st.subheader("Crowd Control")

    col1, col2 = st.columns(2)

    col1.metric("⚠️ Risk Score", f"{risk_score}/100")
    col2.metric("🧭 Risk Level", risk_level)

    if risk_score < 30:
        st.success("✔ Safe travel conditions")
    elif risk_score < 60:
        st.warning("⚠ Moderate risk detected")
    else:
        st.error("🚨 High-risk journey")

    # ---------------- MAP ----------------
    st.subheader("🗺 Route Map")

    full_route = route_places.copy()
    full_route.loc[len(full_route)] = {
        "name": destination_name,
        "latitude": destination[0],
        "longitude": destination[1]
    }

    trip_map = create_map(full_route, start_location)
    st.components.v1.html(trip_map._repr_html_(), height=650)