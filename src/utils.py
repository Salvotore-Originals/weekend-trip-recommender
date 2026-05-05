from geopy.distance import geodesic

# ---------------- DISTANCE ----------------
def calculate_distance(loc1, loc2):
    if None in loc1 or None in loc2:
        return 0
    return geodesic(loc1, loc2).km


# ---------------- TRAVEL TIME ----------------
def estimate_travel_time(distance_km, speed_kmph=60):
    return distance_km / speed_kmph


# ---------------- FUEL COST ----------------
def estimate_fuel_cost(distance_km, mileage=15, fuel_price=100):
    return (distance_km / mileage) * fuel_price