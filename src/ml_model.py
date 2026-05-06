import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from src.utils import calculate_distance


class MLRecommender:

    def __init__(self, data):
        self.data = data
        self.model = RandomForestRegressor(n_estimators=50, random_state=42)
        self._train_model()

    def _train_model(self):
        df = self.data.copy()

        np.random.seed(42)
        df["popularity"] = np.random.randint(1, 100, len(df))

        # Simulated learning target
        df["target_score"] = df["popularity"] * 0.6 + np.random.rand(len(df)) * 10

        X = df[["popularity"]]
        y = df["target_score"]

        self.model.fit(X, y)

    def rank_places(self, start, destination, k=5):

        df = self.data.copy()

        # ---------------- DISTANCES ----------------
        df["dist_start"] = df.apply(
            lambda x: calculate_distance(start, (x["latitude"], x["longitude"])), axis=1
        )

        df["dist_end"] = df.apply(
            lambda x: calculate_distance(destination, (x["latitude"], x["longitude"])), axis=1
        )

        direct_dist = calculate_distance(start, destination)

        # ---------------- ROUTE FILTER (CRITICAL FIX) ----------------
        tolerance = 1.3  # allows 30% detour

        route_df = df[
            (df["dist_start"] + df["dist_end"]) <= (direct_dist * tolerance)
        ]

        # fallback if empty
        if len(route_df) < k:
            route_df = df.copy()

        # ---------------- ML FEATURES ----------------
        route_df["popularity"] = np.random.randint(1, 100, len(route_df))

        route_df["ml_score"] = self.model.predict(route_df[["popularity"]])

        # ---------------- DETOUR PENALTY ----------------
        route_df["detour"] = (
            route_df["dist_start"] + route_df["dist_end"] - direct_dist
        )

        # ---------------- FINAL SCORE ----------------
        route_df["final_score"] = (
            route_df["ml_score"] * 0.4
            - (route_df["dist_start"] + route_df["dist_end"]) * 0.4
            - route_df["detour"] * 0.2
        )

        return route_df.sort_values(by="final_score", ascending=False).head(k)[
            ["name", "latitude", "longitude"]
        ]