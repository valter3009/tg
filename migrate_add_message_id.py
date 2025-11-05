#!/usr/bin/env python3
"""
Миграция: добавление поля last_weather_message_id в таблицу users
"""
import os
import sys
import logging
from sqlalchemy import create_engine, text, inspect

# Добавляем путь к модулям проекта
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bot.database import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate():
    """Добавляет поле last_weather_message_id в таблицу users"""
    DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///gidmeteo.db')

    logger.info(f"Подключение к базе данных: {DATABASE_URL.split('@')[-1] if '@' in DATABASE_URL else DATABASE_URL}")

    engine = create_engine(DATABASE_URL)

    try:
        # Проверяем, существует ли таблица users
        inspector = inspect(engine)
        if 'users' not in inspector.get_table_names():
            logger.info("Таблицы не существуют, инициализируем базу данных...")
            init_db()
            logger.info("✅ База данных успешно инициализирована с новым полем last_weather_message_id")
            return

        with engine.connect() as conn:
            # Проверяем, существует ли уже колонка
            if DATABASE_URL.startswith('sqlite'):
                result = conn.execute(text("PRAGMA table_info(users)"))
                columns = [row[1] for row in result]

                if 'last_weather_message_id' in columns:
                    logger.info("Колонка last_weather_message_id уже существует")
                    return

                # Для SQLite добавляем колонку
                conn.execute(text("ALTER TABLE users ADD COLUMN last_weather_message_id INTEGER"))
                conn.commit()
                logger.info("✅ Миграция успешно выполнена: добавлено поле last_weather_message_id")

            else:
                # Для PostgreSQL
                result = conn.execute(text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name='users' AND column_name='last_weather_message_id'"
                ))

                if result.fetchone():
                    logger.info("Колонка last_weather_message_id уже существует")
                    return

                conn.execute(text("ALTER TABLE users ADD COLUMN last_weather_message_id INTEGER"))
                conn.commit()
                logger.info("✅ Миграция успешно выполнена: добавлено поле last_weather_message_id")

    except Exception as e:
        logger.error(f"❌ Ошибка при выполнении миграции: {e}")
        sys.exit(1)


if __name__ == '__main__':
    migrate()
