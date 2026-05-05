from src.utils import calculate_distance
import pandas as pd

class TripRecommender:

    def __init__(self, data):
        self.data = data

    # Rank by distance from start (simple + effective)
    def rank_by_distance(self, start_location):
        df = self.data.copy()
        df["distance_from_start"] = df.apply(
            lambda x: calculate_distance(start_location, (x["latitude"], x["longitude"])),
            axis=1
        )
        return df.sort_values(by="distance_from_start")

    # Build route using nearest neighbor
    def optimize_route(self, places, start_location):
        route = []
        current = start_location
        remaining = places.copy()

        while len(remaining) > 0:
            remaining["dist"] = remaining.apply(
                lambda x: calculate_distance(current, (x["latitude"], x["longitude"])),
                axis=1
            )

            nearest = remaining.loc[remaining["dist"].idxmin()]
            route.append(nearest)

            current = (nearest["latitude"], nearest["longitude"])
            remaining = remaining.drop(nearest.name)

        return pd.DataFrame(route)

    def get_distance(self, loc1, loc2):
        return calculate_distance(loc1, loc2)