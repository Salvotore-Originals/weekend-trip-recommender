from geopy.distance import geodesic

def calculate_distance(loc1, loc2):
    return geodesic(loc1, loc2).km

def estimate_travel_time(distance):
    return distance / 50

def estimate_fuel_cost(distance):
    return distance * 7