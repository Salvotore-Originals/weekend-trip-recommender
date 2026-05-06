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

    def travel_risk(self, distance):
        if distance < 50:
            return 10
        elif distance < 150:
            return 25
        elif distance < 300:
            return 45
        return 70

    def route_risk(self, stops):
        return min(stops * 8, 40)

    def total_risk(self, weather, distance, stops):
        return round(
            0.5 * self.weather_risk(weather)
            + 0.3 * self.travel_risk(distance)
            + 0.2 * self.route_risk(stops),
            2
        )

    def risk_level(self, score):
        if score < 30:
            return "🟢 Safe"
        elif score < 60:
            return "🟡 Moderate"
        return "🔴 High Risk"