from src.utils import calculate_distance
import pandas as pd

class RoutePlanner:

    def __init__(self, data):
        self.data = data

    def get_places_along_route(self, start, end, k=5):

        df = self.data.copy()

        df["dist_start"] = df.apply(
            lambda x: calculate_distance(start, (x["latitude"], x["longitude"])),
            axis=1
        )

        df["dist_end"] = df.apply(
            lambda x: calculate_distance(end, (x["latitude"], x["longitude"])),
            axis=1
        )

        df["score"] = 0.3 * df["dist_start"] + 0.7 * df["dist_end"]

        return df.sort_values("score").head(k)[["name", "latitude", "longitude"]]

    def get_distance(self, a, b):
        return calculate_distance(a, b)