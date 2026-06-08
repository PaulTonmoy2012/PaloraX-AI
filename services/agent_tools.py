import requests


WEATHER_CODE_LABELS = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Fog",
    51: "Light drizzle",
    53: "Drizzle",
    55: "Heavy drizzle",
    61: "Light rain",
    63: "Rain",
    65: "Heavy rain",
    80: "Rain showers",
    95: "Thunderstorm",
}


def get_weather(latitude: float, longitude: float):
    response = requests.get(
        "https://api.open-meteo.com/v1/forecast",
        params={
            "latitude": latitude,
            "longitude": longitude,
            "current": "temperature_2m,weather_code,wind_speed_10m",
            "timezone": "auto",
        },
        timeout=10,
    )

    response.raise_for_status()
    data = response.json()

    current = data.get("current", {})
    units = data.get("current_units", {})

    weather_code = current.get("weather_code")

    return {
        "temperature": current.get("temperature_2m"),
        "temperature_unit": units.get("temperature_2m", "C"),
        "condition": WEATHER_CODE_LABELS.get(weather_code, "Unknown"),
        "wind_speed": current.get("wind_speed_10m"),
        "wind_speed_unit": units.get("wind_speed_10m", "km/h"),
        "time": current.get("time"),
    }

def get_location(city: str):
    """
    Get latitude and longitude for a city name.
    Use this first when the user asks weather for a city.
    """
    response = requests.get(
        "https://geocoding-api.open-meteo.com/v1/search",
        params={
            "name": city,
            "count": 1,
            "language": "en",
            "format": "json",
        },
        timeout=10,
    )

    response.raise_for_status()
    data = response.json()

    results = data.get("results", [])

    if not results:
        return {
            "error": f"No location found for {city}"
        }

    location = results[0]

    return {
        "city": location.get("name"),
        "country": location.get("country"),
        "admin_area": location.get("admin1"),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "timezone": location.get("timezone"),
    }
