import streamlit as st
import pandas as pd
import os
from streamlit_geolocation import streamlit_geolocation

from src.ml_model import MLRecommender
from src.map_utils import create_map
from src.utils import calculate_distance, estimate_travel_time, estimate_fuel_cost
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

option = st.radio(
    "Choose starting point:",
    ["Use My Current Location", "Select manually"]
)

loc = streamlit_geolocation()
gps = None

if loc and loc.get("latitude"):
    lat, lon = loc["latitude"], loc["longitude"]
    if 6 <= lat <= 38 and 68 <= lon <= 98:
        gps = (lat, lon)

if option == "Use My Current Location":
    if gps is None:
        st.error("Enable GPS access")
        st.stop()
    start = gps
else:
    name = st.selectbox("Select start", sorted(data["name"].unique()))
    row = data[data["name"] == name].iloc[0]
    start = (row["latitude"], row["longitude"])

# -------- DESTINATION --------
st.subheader("🎯 Destination")

dest_name = st.selectbox("Choose destination", sorted(data["name"].unique()))
row = data[data["name"] == dest_name].iloc[0]
destination = (row["latitude"], row["longitude"])

# -------- SETTINGS --------
st.sidebar.header("Trip Settings")
k = st.sidebar.slider("Nearby places", 3, 10, 6)
people = st.sidebar.number_input("People", 1, 20, 2)

# -------- PLAN --------
if st.button("Plan Trip"):

    # ✅ DIRECT ML CALL (NO route_planner dependency)
    recommender = MLRecommender(data)

    places = recommender.recommend_nearby(destination, k)

    # -------- DISTANCE --------
    dist = calculate_distance(start, destination)
    time = estimate_travel_time(dist)
    cost = estimate_fuel_cost(dist)

    # -------- WEATHER --------
    weather = get_weather(destination[0], destination[1])

    # -------- BEST TIME --------
    temp = weather["temp"]
    if temp > 32:
        best = "October to February"
    elif temp < 20:
        best = "March to June"
    else:
        best = "September to March"

    # -------- RISK --------
    risk_engine = TravelRiskEngine()
    score = risk_engine.total_risk(weather, dist, k)
    level = risk_engine.risk_level(score)

    # -------- OUTPUT --------
    st.subheader("📊 Trip Summary")

    c1, c2, c3 = st.columns(3)
    c1.metric("Distance", f"{dist:.2f} km")
    c2.metric("Time", f"{time:.2f} hrs")
    c3.metric("Fuel", f"₹{cost:.2f}")

    st.metric("People", people)

    st.subheader("🌦 Weather")
    st.write(f"{weather['temp']}°C | {weather['condition']}")

    st.subheader("🧭 Best Time to Visit")
    st.success(best)

    st.subheader("⚠️ Risk Analysis")
    st.metric("Score", score)
    st.metric("Level", level)

    st.subheader("📍 Places Near Destination")

    threshold = places["final_score"].quantile(0.7)

    for _, r in places.iterrows():
        tag = "⭐ Must Visit" if r["final_score"] >= threshold else ""
        st.write(f"{r['name']} — {r['dist_dest']:.1f} km {tag}")

    # -------- MAP --------
    df_map = pd.DataFrame([
        {"name": "Start", "latitude": start[0], "longitude": start[1]},
        {"name": dest_name, "latitude": destination[0], "longitude": destination[1]}
    ])

    m = create_map(df_map, start)
    st.components.v1.html(m._repr_html_(), height=600)