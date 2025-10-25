"""
Скрипт обновления timezone для существующих городов в базе данных
"""
import logging
from sqlalchemy import text
from bot.database import engine, get_db, init_db
from bot.models import City
from bot.services.timezone import TimezoneService

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def add_timezone_column_if_not_exists():
    """Добавляет столбец timezone в таблицу cities, если его еще нет"""
    logger.info("Проверка наличия столбца timezone в таблице cities...")

    try:
        with engine.connect() as conn:
            # Проверяем, существует ли столбец
            result = conn.execute(text("PRAGMA table_info(cities)"))
            columns = [row[1] for row in result]

            if 'timezone' not in columns:
                logger.info("Столбец timezone не найден, добавляем...")
                conn.execute(text("ALTER TABLE cities ADD COLUMN timezone VARCHAR(50)"))
                conn.commit()
                logger.info("Столбец timezone успешно добавлен")
            else:
                logger.info("Столбец timezone уже существует")

    except Exception as e:
        logger.error(f"Ошибка при добавлении столбца timezone: {e}")
        raise


def update_city_timezones():
    """Обновляет timezone для всех городов без timezone"""
    logger.info("Начало обновления timezone для городов...")

    try:
        db = get_db()

        # Получаем все города без timezone
        cities = db.query(City).filter(
            (City.timezone == None) | (City.timezone == '')
        ).all()

        logger.info(f"Найдено {len(cities)} городов без timezone")

        updated_count = 0
        failed_count = 0

        for city in cities:
            try:
                logger.info(f"Определение timezone для {city.name}...")

                timezone = TimezoneService.get_timezone_from_city(city.name)

                if timezone:
                    city.timezone = timezone
                    db.commit()
                    updated_count += 1
                    logger.info(f"✓ {city.name}: {timezone}")
                else:
                    logger.warning(f"✗ {city.name}: не удалось определить timezone")
                    failed_count += 1

            except Exception as e:
                logger.error(f"Ошибка при обновлении {city.name}: {e}")
                failed_count += 1
                db.rollback()

        logger.info("=" * 50)
        logger.info("ОБНОВЛЕНИЕ ЗАВЕРШЕНО")
        logger.info(f"Успешно обновлено: {updated_count}")
        logger.info(f"Ошибок: {failed_count}")
        logger.info("=" * 50)

        db.close()

    except Exception as e:
        logger.error(f"Критическая ошибка при обновлении timezone: {e}")
        raise


def main():
    """Основная функция миграции"""
    logger.info("=" * 50)
    logger.info("МИГРАЦИЯ: ДОБАВЛЕНИЕ TIMEZONE К ГОРОДАМ")
    logger.info("=" * 50)

    try:
        # Инициализируем базу данных
        logger.info("Инициализация базы данных...")
        init_db()

        # Добавляем столбец timezone, если его нет
        add_timezone_column_if_not_exists()

        # Обновляем timezone для городов
        update_city_timezones()

        logger.info("Миграция успешно завершена!")

    except Exception as e:
        logger.error(f"Критическая ошибка при миграции: {e}")
        raise


if __name__ == "__main__":
    main()
