"""
Сервис для работы с часовыми поясами
"""
import logging
from datetime import datetime, time
import pytz
from typing import Optional
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder

logger = logging.getLogger(__name__)

# Инициализация
tf = TimezoneFinder()
geolocator = Nominatim(user_agent="gidmeteo_bot")


class TimezoneService:
    """Сервис для определения и работы с часовыми поясами"""

    @staticmethod
    def get_timezone_from_city(city_name: str) -> Optional[str]:
        """
        Определяет часовой пояс по названию города

        Args:
            city_name: Название города

        Returns:
            Название часового пояса (например, 'Europe/Moscow') или None
        """
        try:
            # Получаем координаты города
            location = geolocator.geocode(city_name, timeout=10)

            if location:
                # Определяем часовой пояс по координатам
                timezone_name = tf.timezone_at(lat=location.latitude, lng=location.longitude)

                if timezone_name:
                    logger.info(f"Определен часовой пояс для {city_name}: {timezone_name}")
                    return timezone_name
                else:
                    logger.warning(f"Не удалось определить часовой пояс для {city_name}")
                    return None
            else:
                logger.warning(f"Не удалось найти координаты для {city_name}")
                return None

        except Exception as e:
            logger.error(f"Ошибка при определении часового пояса для {city_name}: {e}")
            return None

    @staticmethod
    def convert_utc_to_local(utc_hour: int, utc_minute: int, timezone_name: str) -> tuple:
        """
        Конвертирует UTC время в локальное время

        Args:
            utc_hour: Час в UTC
            utc_minute: Минута в UTC
            timezone_name: Название часового пояса

        Returns:
            Кортеж (локальный_час, локальная_минута)
        """
        try:
            # Создаем UTC время на сегодня
            utc_tz = pytz.UTC
            local_tz = pytz.timezone(timezone_name)

            # Используем сегодняшнюю дату
            today = datetime.now(utc_tz).date()
            utc_time = datetime.combine(today, time(utc_hour, utc_minute))
            utc_time = utc_tz.localize(utc_time)

            # Конвертируем в локальное время
            local_time = utc_time.astimezone(local_tz)

            return local_time.hour, local_time.minute

        except Exception as e:
            logger.error(f"Ошибка при конвертации времени: {e}")
            return utc_hour, utc_minute

    @staticmethod
    def get_current_local_time(timezone_name: str) -> datetime:
        """
        Получает текущее локальное время для часового пояса

        Args:
            timezone_name: Название часового пояса

        Returns:
            Текущее локальное время
        """
        try:
            tz = pytz.timezone(timezone_name)
            return datetime.now(tz)
        except Exception as e:
            logger.error(f"Ошибка при получении локального времени: {e}")
            return datetime.now(pytz.UTC)

    @staticmethod
    def should_send_notification(
        user_timezone: str,
        notification_hours: list,
        notification_minute: int = 1
    ) -> bool:
        """
        Проверяет, нужно ли отправлять уведомление пользователю сейчас

        Args:
            user_timezone: Часовой пояс пользователя
            notification_hours: Список часов для уведомлений (в локальном времени)
            notification_minute: Минута для уведомлений

        Returns:
            True, если нужно отправить уведомление
        """
        try:
            local_time = TimezoneService.get_current_local_time(user_timezone)

            # Проверяем, совпадает ли текущее время с временем уведомления
            if local_time.hour in notification_hours and local_time.minute == notification_minute:
                return True

            return False

        except Exception as e:
            logger.error(f"Ошибка при проверке времени уведомления: {e}")
            return False

    @staticmethod
    def format_time_for_user(dt: datetime, timezone_name: str, format_str: str = '%d.%m.%Y %H:%M:%S') -> str:
        """
        Форматирует время для отображения пользователю в его часовом поясе

        Args:
            dt: Datetime объект (UTC)
            timezone_name: Часовой пояс пользователя
            format_str: Формат строки

        Returns:
            Отформатированная строка времени
        """
        try:
            if dt.tzinfo is None:
                dt = pytz.UTC.localize(dt)

            tz = pytz.timezone(timezone_name)
            local_dt = dt.astimezone(tz)

            return local_dt.strftime(format_str)

        except Exception as e:
            logger.error(f"Ошибка при форматировании времени: {e}")
            return dt.strftime(format_str)
