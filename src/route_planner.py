from src.utils import calculate_distance
from src.ml_model import MLRecommender


class RoutePlanner:

    def __init__(self, data):
        self.data = data
        self.ml_model = MLRecommender(data)

    def get_places_along_route(self, start, end, k=5):
        return self.ml_model.rank_places(start, end, k)

    def get_distance(self, loc1, loc2):
        return calculate_distance(loc1, loc2)