import numpy as np
from sklearn.ensemble import RandomForestRegressor
from src.utils import calculate_distance


class MLRecommender:

    def __init__(self, data):
        self.data = data
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)
        self._train()

    def _train(self):
        df = self.data.copy()
        df["popularity"] = np.random.randint(1, 100, len(df))
        self.model.fit(df[["popularity"]], df["popularity"])

    def recommend_nearby(self, destination, k=6):
        df = self.data.copy()

        # Remove duplicates
        df = df.drop_duplicates(subset=["name"])

        # Compute distance
        df["dist_dest"] = df.apply(
            lambda x: calculate_distance(destination, (x["latitude"], x["longitude"])),
            axis=1
        )

        # Keep nearby (<= 80 km)
        df = df[df["dist_dest"] <= 80]

        if df.empty:
            df = self.data.copy()

        # ML scoring
        df["popularity"] = np.random.randint(1, 100, len(df))
        df["ml_score"] = self.model.predict(df[["popularity"]])

        df["final_score"] = df["ml_score"] * 0.6 - df["dist_dest"] * 0.4

        df = df.sort_values(by="final_score", ascending=False).head(k)

        return df.sort_values(by="dist_dest")[[
            "name", "latitude", "longitude", "dist_dest", "final_score"
        ]]