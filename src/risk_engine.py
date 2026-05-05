class TravelRiskEngine:

    def weather_risk(self, weather):

        temp = weather.get("temp", 25)
        condition = weather.get("condition", "").lower()

        risk = 0

        if "rain" in condition:
            risk += 40

        if temp > 38:
            risk += 30
        elif temp < 15:
            risk += 20

        return min(risk, 100)

    def travel_risk(self, distance_km):

        if distance_km < 50:
            return 10
        elif distance_km < 150:
            return 25
        elif distance_km < 300:
            return 45
        return 70

    def route_risk(self, num_stops):
        return min(num_stops * 8, 40)

    def total_risk(self, weather, distance_km, num_stops):

        w = self.weather_risk(weather)
        t = self.travel_risk(distance_km)
        r = self.route_risk(num_stops)

        return round((0.5 * w) + (0.3 * t) + (0.2 * r), 2)

    def risk_level(self, score):

        if score < 30:
            return "🟢 Safe"
        elif score < 60:
            return "🟡 Moderate"
        return "🔴 High Risk"