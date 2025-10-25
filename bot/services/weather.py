"""
Сервис для работы с погодой
"""
import logging
import requests
from datetime import datetime, timedelta
from typing import Optional, Dict
from sqlalchemy.orm import Session
from bot.models import City, WeatherCache
from bot.config import config
from bot.utils.retry import retry_on_exception

logger = logging.getLogger(__name__)


class WeatherService:
    """Сервис для получения и кэширования погодных данных"""

    @staticmethod
    def get_weather_emoji(description: str) -> str:
        """
        Возвращает эмодзи погоды по описанию

        Args:
            description: Описание погоды

        Returns:
            Эмодзи погоды
        """
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

    @staticmethod
    @retry_on_exception(max_retries=3, delay=1.0, exceptions=(requests.RequestException,))
    def fetch_weather_from_api(city_name: str) -> Optional[Dict]:
        """
        Получает погоду из OpenWeatherMap API

        Args:
            city_name: Название города

        Returns:
            Словарь с данными погоды или None
        """
        url = f'https://api.openweathermap.org/data/2.5/weather'
        params = {
            'q': city_name,
            'units': 'metric',
            'lang': 'ru',
            'appid': config.OPENWEATHER_API_KEY
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()

            weather_data = response.json()

            if weather_data.get('cod') == '404':
                logger.warning(f"Город {city_name} не найден в OpenWeatherMap")
                return None

            temperature = round(weather_data['main']['temp'], 1)
            weather_description = weather_data['weather'][0]['description']
            wind_speed = round(weather_data['wind']['speed'], 1)

            weather_emoji = WeatherService.get_weather_emoji(weather_description)

            return {
                'temp': temperature,
                'emoji': weather_emoji,
                'description': weather_description,
                'wind_speed': wind_speed,
            }

        except requests.RequestException as e:
            logger.error(f'Ошибка при получении погоды для {city_name}: {e}')
            raise
        except Exception as e:
            logger.error(f'Неожиданная ошибка при получении погоды для {city_name}: {e}')
            return None

    @staticmethod
    def get_or_create_city(db: Session, city_name: str) -> Optional[City]:
        """
        Получает город из БД или создает новый

        Args:
            db: Сессия базы данных
            city_name: Название города

        Returns:
            Объект City или None
        """
        try:
            city_name_lower = city_name.lower()

            # Пытаемся найти город
            city = db.query(City).filter(City.name_lower == city_name_lower).first()

            if not city:
                # Определяем часовой пояс для нового города
                from bot.services.timezone import TimezoneService
                timezone = TimezoneService.get_timezone_from_city(city_name)

                # Создаем новый город с timezone
                city = City(
                    name=city_name,
                    name_lower=city_name_lower,
                    timezone=timezone
                )
                db.add(city)
                db.commit()
                db.refresh(city)
                logger.info(f"Создан новый город: {city_name} (timezone: {timezone})")
            elif not city.timezone:
                # Если город существует, но у него нет timezone, определяем и сохраняем
                from bot.services.timezone import TimezoneService
                timezone = TimezoneService.get_timezone_from_city(city_name)
                if timezone:
                    city.timezone = timezone
                    db.commit()
                    logger.info(f"Обновлен timezone для {city_name}: {timezone}")

            return city

        except Exception as e:
            logger.error(f"Ошибка при получении/создании города {city_name}: {e}")
            db.rollback()
            return None

    @staticmethod
    def get_cached_weather(db: Session, city: City) -> Optional[Dict]:
        """
        Получает погоду из кэша

        Args:
            db: Сессия базы данных
            city: Объект города

        Returns:
            Словарь с данными погоды или None
        """
        try:
            cache = db.query(WeatherCache).filter(WeatherCache.city_id == city.id).first()

            if cache:
                # Проверяем, не устарел ли кэш
                cache_age = (datetime.utcnow() - cache.updated_at).total_seconds()

                if cache_age < config.WEATHER_CACHE_TTL:
                    return {
                        'temp': cache.temperature,
                        'emoji': cache.emoji,
                        'description': cache.description,
                        'wind_speed': cache.wind_speed,
                        'updated_at': cache.updated_at
                    }
                else:
                    logger.debug(f"Кэш для {city.name} устарел ({cache_age:.0f}с)")

            return None

        except Exception as e:
            logger.error(f"Ошибка при получении кэша для {city.name}: {e}")
            return None

    @staticmethod
    def update_weather_cache(db: Session, city: City, weather_data: Dict) -> bool:
        """
        Обновляет кэш погоды

        Args:
            db: Сессия базы данных
            city: Объект города
            weather_data: Данные погоды

        Returns:
            True если успешно, False иначе
        """
        try:
            cache = db.query(WeatherCache).filter(WeatherCache.city_id == city.id).first()

            if cache:
                # Обновляем существующий кэш
                cache.temperature = weather_data['temp']
                cache.description = weather_data['description']
                cache.emoji = weather_data['emoji']
                cache.wind_speed = weather_data['wind_speed']
                cache.updated_at = datetime.utcnow()
            else:
                # Создаем новый кэш
                cache = WeatherCache(
                    city_id=city.id,
                    temperature=weather_data['temp'],
                    description=weather_data['description'],
                    emoji=weather_data['emoji'],
                    wind_speed=weather_data['wind_speed']
                )
                db.add(cache)

            db.commit()
            logger.debug(f"Кэш погоды обновлен для {city.name}")
            return True

        except Exception as e:
            logger.error(f"Ошибка при обновлении кэша для {city.name}: {e}")
            db.rollback()
            return False

    @staticmethod
    def get_weather(db: Session, city_name: str, use_cache: bool = True) -> Optional[Dict]:
        """
        Получает погоду для города (из кэша или API)

        Args:
            db: Сессия базы данных
            city_name: Название города
            use_cache: Использовать ли кэш

        Returns:
            Словарь с данными погоды или None
        """
        try:
            # Получаем или создаем город
            city = WeatherService.get_or_create_city(db, city_name)
            if not city:
                return None

            # Пытаемся получить из кэша
            if use_cache:
                cached_weather = WeatherService.get_cached_weather(db, city)
                if cached_weather:
                    logger.debug(f"Использован кэш для {city_name}")
                    return cached_weather

            # Получаем из API
            weather_data = WeatherService.fetch_weather_from_api(city_name)

            if weather_data:
                # Обновляем кэш
                WeatherService.update_weather_cache(db, city, weather_data)
                return weather_data

            return None

        except Exception as e:
            logger.error(f"Ошибка при получении погоды для {city_name}: {e}")
            return None
