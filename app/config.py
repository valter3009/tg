"""
Конфигурация GidMeteo бота
Все секретные данные загружаются из переменных окружения
"""
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла (для локальной разработки)
load_dotenv()


class Config:
    """Класс конфигурации приложения"""

    # Telegram Bot Token (обязательно)
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    if not TELEGRAM_TOKEN:
        raise ValueError("TELEGRAM_TOKEN environment variable is required!")

    # OpenWeatherMap API Key (обязательно)
    OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
    if not OPENWEATHER_API_KEY:
        raise ValueError("OPENWEATHER_API_KEY environment variable is required!")

    # Database URL (обязательно для продакшена, опционально для локальной разработки)
    DATABASE_URL = os.getenv("DATABASE_URL")
    if not DATABASE_URL:
        # Для локальной разработки используем SQLite
        DATABASE_URL = "sqlite:///./gidmeteo.db"
        print("WARNING: Using SQLite database for local development")
    else:
        # Railway предоставляет DATABASE_URL в формате postgres://
        # SQLAlchemy требует postgresql://
        if DATABASE_URL.startswith("postgres://"):
            DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    # ProjectEOL Token (опционально)
    PROJECTEOL_TOKEN = os.getenv("PROJECTEOL_TOKEN", "")

    # Настройки кеширования погоды
    WEATHER_CACHE_TTL = int(os.getenv("WEATHER_CACHE_TTL", "3600"))  # 1 час по умолчанию

    # Интервал обновления кеша погоды (секунды)
    CACHE_UPDATE_INTERVAL = int(os.getenv("CACHE_UPDATE_INTERVAL", "600"))  # 10 минут

    # Логирование
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

    # Список дополнительных пользователей для автообновлений
    # Эти пользователи будут добавлены в БД при старте бота
    ADDITIONAL_USERS = [
        471789857, 425748474, 6118023060, 6488366997, 5934413419, 6615704791,
        1134118381, 1823348752, 6579300547, 5174302370, 1344487460, 7791445179,
        1276348447, 278283980, 6556640321, 1521820146, 7523695427, 7880850349,
        832185475, 149653247, 1775572520, 7643533302, 352808232, 7456672724,
        5969931672, 993675994, 543397394, 5935464436, 1812257315, 6260364812,
        434939312
    ]

    @classmethod
    def validate(cls):
        """Проверяет, что все обязательные конфигурации установлены"""
        if not cls.TELEGRAM_TOKEN:
            raise ValueError("TELEGRAM_TOKEN is not set")
        if not cls.OPENWEATHER_API_KEY:
            raise ValueError("OPENWEATHER_API_KEY is not set")
        if not cls.DATABASE_URL:
            raise ValueError("DATABASE_URL is not set")


# Валидируем конфигурацию при импорте
Config.validate()
