"""
Конфигурация приложения
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла (для локальной разработки)
load_dotenv()


class Config:
    """Конфигурация приложения"""

    # Telegram Bot
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN не установлен в переменных окружения")

    # OpenWeatherMap API
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    if not OPENWEATHER_API_KEY:
        raise ValueError("OPENWEATHER_API_KEY не установлен в переменных окружения")

    # База данных
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///gidmeteo.db")

    # Кэширование
    WEATHER_CACHE_TTL = int(os.getenv("WEATHER_CACHE_TTL", "3600"))  # 1 час

    # Уведомления
    AUTO_UPDATE_HOURS = [0, 4, 8, 12, 16, 20]  # Часы для автообновлений (UTC)
    AUTO_UPDATE_MINUTE = 1  # Минута для автообновлений

    # Retry настройки
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_DELAY = int(os.getenv("RETRY_DELAY", "1"))  # секунды

    # Логирование
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE = os.getenv("LOG_FILE", "bot_errors.log")

    # Timezone
    DEFAULT_TIMEZONE = os.getenv("DEFAULT_TIMEZONE", "UTC")

    # Flask keepalive (для Railway)
    FLASK_PORT = int(os.getenv("PORT", "8000"))


# Экспортируем экземпляр конфигурации
config = Config()
