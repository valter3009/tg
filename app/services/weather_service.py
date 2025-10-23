"""
Сервис для работы с погодными данными
"""
import requests
import logging
from typing import Optional, Dict
from datetime import datetime

from ..config import Config
from ..database.db_service import DatabaseService

logger = logging.getLogger(__name__)


class WeatherService:
    """Сервис для получения и кеширования погоды"""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service
        self.api_key = Config.OPENWEATHER_API_KEY
        self.base_url = "https://api.openweathermap.org/data/2.5/weather"

    def get_weather_emoji(self, description: str) -> str:
        """Возвращает эмодзи для описания погоды"""
        description = description.lower()

        if any(word in description for word in ['ясно', 'чистое небо', 'безоблачно']):
            return '☀️'
        elif any(word in description for word in ['облачно с прояснениями', 'переменная облачность']):
            return '⛅'
        elif any(word in description for word in ['облачно', 'пасмурно']):
            return '☁️'
        elif any(word in description for word in ['дождь', 'ливень']):
            return '🌧️'
        elif any(word in description for word in ['гроза']):
            return '⛈️'
        elif any(word in description for word in ['снег', 'снегопад']):
            return '❄️'
        elif any(word in description for word in ['туман', 'мгла']):
            return '🌫️'
        else:
            return '🌦️'

    def get_weather_from_api(self, city: str) -> Optional[Dict]:
        """Получает данные о погоде из OpenWeatherMap API"""
        try:
            params = {
                'q': city,
                'units': 'metric',
                'lang': 'ru',
                'appid': self.api_key
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('cod') == '404':
                logger.warning(f"City not found: {city}")
                return None

            # Извлекаем данные
            temperature = round(data['main']['temp'], 1)
            description = data['weather'][0]['description']
            wind_speed = int(round(data['wind']['speed']))
            emoji = self.get_weather_emoji(description)

            weather_data = {
                'temp': temperature,
                'description': description,
                'wind_speed': wind_speed,
                'emoji': emoji,
                'updated_at': int(datetime.utcnow().timestamp())
            }

            # Сохраняем в кеш
            self.db_service.update_weather_cache(
                city_name=city,
                temperature=temperature,
                description=description,
                emoji=emoji,
                wind_speed=wind_speed
            )

            logger.info(f"Weather data fetched for {city}: {temperature}°C")
            return weather_data

        except requests.RequestException as e:
            logger.error(f"Error fetching weather for {city}: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error getting weather for {city}: {e}")
            return None

    def get_weather(self, city: str) -> Optional[Dict]:
        """
        Получает погоду для города (сначала проверяет кеш)

        Returns:
            Dict с полями: temp, description, wind_speed, emoji, updated_at
            или None если город не найден
        """
        # Сначала проверяем кеш
        cached = self.db_service.get_weather_cache(
            city_name=city,
            max_age_seconds=Config.WEATHER_CACHE_TTL
        )

        if cached:
            logger.debug(f"Using cached weather for {city}")
            return cached

        # Если кеша нет или он устарел, запрашиваем из API
        logger.debug(f"Fetching fresh weather for {city}")
        return self.get_weather_from_api(city)

    def update_all_cities_cache(self):
        """Обновляет кеш погоды для всех городов в базе"""
        cities = self.db_service.get_all_cities()
        logger.info(f"Updating weather cache for {len(cities)} cities")

        for city in cities:
            try:
                self.get_weather_from_api(city)
            except Exception as e:
                logger.error(f"Error updating cache for {city}: {e}")

        logger.info("Weather cache update completed")
