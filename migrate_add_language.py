"""
Миграция: добавление поля language в таблицу users
"""
import logging
from sqlalchemy import text
from bot.database import get_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def migrate_add_language():
    """Добавляет поле language в таблицу users"""
    db = get_db()

    try:
        # Проверяем, существует ли уже поле language
        result = db.execute(text("PRAGMA table_info(users)")).fetchall()
        columns = [row[1] for row in result]

        if 'language' in columns:
            logger.info("Поле 'language' уже существует в таблице users")
            return

        # Добавляем поле language
        logger.info("Добавление поля 'language' в таблицу users...")
        db.execute(text("ALTER TABLE users ADD COLUMN language VARCHAR(10) DEFAULT 'ru' NOT NULL"))
        db.commit()

        logger.info("✅ Поле 'language' успешно добавлено в таблицу users")

        # Проверяем количество пользователей
        user_count = db.execute(text("SELECT COUNT(*) FROM users")).scalar()
        logger.info(f"Всего пользователей в базе: {user_count}")

    except Exception as e:
        logger.error(f"Ошибка при миграции: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    logger.info("=" * 50)
    logger.info("Запуск миграции: добавление поля language")
    logger.info("=" * 50)

    migrate_add_language()

    logger.info("=" * 50)
    logger.info("Миграция завершена")
    logger.info("=" * 50)
