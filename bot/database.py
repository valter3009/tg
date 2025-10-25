"""
Настройка подключения к базе данных
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.pool import StaticPool
from bot.models import Base
import logging

logger = logging.getLogger(__name__)

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///gidmeteo.db')

# Для SQLite добавляем параметры для многопоточности
if DATABASE_URL.startswith('sqlite'):
    engine = create_engine(
        DATABASE_URL,
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
        echo=False
    )
else:
    # Для PostgreSQL
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

# Создаем фабрику сессий
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))


def init_db():
    """Инициализация базы данных (создание всех таблиц)"""
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("База данных успешно инициализирована")
    except Exception as e:
        logger.error(f"Ошибка при инициализации базы данных: {e}")
        raise


def get_db():
    """Получение сессии базы данных"""
    db = SessionLocal()
    try:
        return db
    except Exception:
        db.close()
        raise


def close_db():
    """Закрытие всех соединений с базой данных"""
    SessionLocal.remove()
