from mcp.server import MCPServer
import httpx

mcp = MCPServer("Simple Weather Connector")

@mcp.tool()
async def get_weather(city: str) -> str:
    """Get the current weather for a city.
    
    Use this tool whenever the user asks about the weather, temperature, 
    or conditions in a specific city.
    
    Args:
        city: The name of the city (e.g. "London", "New York", "Tokyo")
    """
    # Open-Meteo geocoding + weather (free, no key)
    async with httpx.AsyncClient() as client:
        # Get coordinates
        geo = await client.get(
            "https://geocoding-api.open-meteo.com/v1/search",
            params={"name": city, "count": 1}
        )
        geo_data = geo.json()
        
        if not geo_data.get("results"):
            return f"Could not find a city named '{city}'."
        
        loc = geo_data["results"][0]
        lat, lon = loc["latitude"], loc["longitude"]
        name = loc.get("name", city)
        country = loc.get("country", "")
        
        # Get current weather
        weather = await client.get(
            "https://api.open-meteo.com/v1/forecast",
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "temperature_2m,weather_code,wind_speed_10m",
                "timezone": "auto"
            }
        )
        w = weather.json()["current"]
        
        temp = w["temperature_2m"]
        wind = w["wind_speed_10m"]
        code = w["weather_code"]
        
        # Simple weather code mapping
        conditions = {
            0: "Clear", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast",
            45: "Foggy", 48: "Depositing rime fog",
            51: "Light drizzle", 53: "Moderate drizzle", 55: "Dense drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain",
            71: "Slight snow", 73: "Moderate snow", 75: "Heavy snow",
            95: "Thunderstorm"
        }
        condition = conditions.get(code, "Unknown conditions")
        
        location = f"{name}, {country}" if country else name
        return (
            f"Current weather in {location}: {condition}, "
            f"{temp}°C, wind {wind} km/h."
        )

if __name__ == "__main__":
    mcp.run(transport="streamable-http", port=8000)