import logging

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

async def get_current_weather(lat: float, lon: float) -> dict:
    api_key = get_settings().openweather_api_key
    if not api_key:
        logger.info("OPENWEATHERMAP_API_KEY not set, using mock weather data.")
        return {
            "temperature": 28.5,
            "description": "scattered clouds",
            "humidity": 65,
            "wind": 4.1,
            "feels_like": 31.0
        }
    
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        if response.status_code == 200:
            data = response.json()
            return {
                "temperature": data["main"]["temp"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind": data["wind"]["speed"],
                "feels_like": data["main"]["feels_like"]
            }
        else:
            logger.error(f"Weather API error: {response.text}")
            return {
                "temperature": 28.5,
                "description": "unknown",
                "humidity": 65,
                "wind": 4.1,
                "feels_like": 31.0
            }
