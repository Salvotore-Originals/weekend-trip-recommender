from src.utils import calculate_distance
from src.ml_model import MLRecommender


class RoutePlanner:

    def __init__(self, data):
        self.recommender = MLRecommender(data)

    def get_nearby_places(self, destination, k):
        return self.recommender.recommend_nearby(destination, k)

    def get_distance(self, loc1, loc2):
        return calculate_distance(loc1, loc2)