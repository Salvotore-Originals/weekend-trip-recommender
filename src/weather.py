import requests

def get_weather(lat, lon):

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current_weather=true"
    )

    res = requests.get(url).json()

    if "current_weather" not in res:
        return {
            "temp": 25,
            "condition": "Unavailable"
        }

    w = res["current_weather"]

    return {
        "temp": w.get("temperature", 25),
        "condition": "Windy / Clear (Open-Meteo)"
    }