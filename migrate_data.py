"""
Скрипт миграции данных из JSON/Excel в базу данных
"""
import json
import os
from datetime import datetime
import logging
from bot.database import engine, get_db, init_db
from bot.models import Base, User, City, UserCity, WeatherCache
from bot.services.timezone import TimezoneService

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def migrate_users(db):
    """Миграция пользователей из all_users.json"""
    logger.info("Начало миграции пользователей...")

    try:
        with open('all_users.json', 'r', encoding='utf-8') as f:
            all_users = json.load(f)

        migrated = 0
        skipped = 0

        for telegram_id_str, user_data in all_users.items():
            try:
                telegram_id = int(telegram_id_str)

                # Проверяем, не существует ли уже пользователь
                existing_user = db.query(User).filter(User.telegram_id == telegram_id).first()

                if existing_user:
                    logger.debug(f"Пользователь {telegram_id} уже существует, пропускаем")
                    skipped += 1
                    continue

                # Парсим дату первого старта
                first_start_str = user_data.get('first_start')
                if first_start_str:
                    try:
                        created_at = datetime.strptime(first_start_str, '%Y-%m-%d %H:%M:%S')
                    except ValueError:
                        created_at = datetime.utcnow()
                else:
                    created_at = datetime.utcnow()

                # Создаем пользователя
                user = User(
                    telegram_id=telegram_id,
                    is_active=user_data.get('active', True),
                    created_at=created_at,
                    updated_at=created_at,
                    source=user_data.get('source', 'migration'),
                    timezone='UTC'  # По умолчанию UTC, будет обновлено при добавлении городов
                )

                db.add(user)
                migrated += 1

                if migrated % 10 == 0:
                    db.commit()
                    logger.info(f"Мигрировано пользователей: {migrated}")

            except Exception as e:
                logger.error(f"Ошибка при миграции пользователя {telegram_id_str}: {e}")
                continue

        db.commit()
        logger.info(f"Миграция пользователей завершена. Мигрировано: {migrated}, пропущено: {skipped}")

    except FileNotFoundError:
        logger.warning("Файл all_users.json не найден, пропускаем миграцию пользователей")
    except Exception as e:
        logger.error(f"Ошибка при миграции пользователей: {e}")
        db.rollback()


def migrate_cities_and_user_cities(db):
    """Миграция городов и связей пользователь-город из user_cities.json"""
    logger.info("Начало миграции городов...")

    try:
        with open('user_cities.json', 'r', encoding='utf-8') as f:
            user_cities_data = json.load(f)

        migrated_cities = 0
        migrated_relations = 0
        skipped_relations = 0

        for telegram_id_str, cities_list in user_cities_data.items():
            try:
                telegram_id = int(telegram_id_str)

                # Находим пользователя
                user = db.query(User).filter(User.telegram_id == telegram_id).first()

                if not user:
                    logger.warning(f"Пользователь {telegram_id} не найден, создаем...")
                    user = User(
                        telegram_id=telegram_id,
                        is_active=True,
                        source='migration',
                        timezone='UTC'
                    )
                    db.add(user)
                    db.commit()
                    db.refresh(user)

                # Обрабатываем города пользователя
                for order, city_name in enumerate(cities_list):
                    if not city_name:
                        continue

                    # Получаем или создаем город
                    city_name_lower = city_name.lower()
                    city = db.query(City).filter(City.name_lower == city_name_lower).first()

                    if not city:
                        city = City(name=city_name, name_lower=city_name_lower)
                        db.add(city)
                        db.commit()
                        db.refresh(city)
                        migrated_cities += 1
                        logger.debug(f"Создан город: {city_name}")

                    # Создаем связь пользователь-город
                    existing_relation = db.query(UserCity).filter(
                        UserCity.user_id == user.id,
                        UserCity.city_id == city.id
                    ).first()

                    if existing_relation:
                        skipped_relations += 1
                        continue

                    user_city = UserCity(
                        user_id=user.id,
                        city_id=city.id,
                        order=order
                    )
                    db.add(user_city)
                    migrated_relations += 1

                # Если это первый город пользователя, пытаемся определить timezone
                if cities_list and user.timezone == 'UTC':
                    first_city = cities_list[0]
                    timezone = TimezoneService.get_timezone_from_city(first_city)
                    if timezone:
                        user.timezone = timezone
                        logger.info(f"Установлен timezone {timezone} для пользователя {telegram_id} (город: {first_city})")

                if migrated_relations % 20 == 0:
                    db.commit()
                    logger.info(f"Мигрировано связей: {migrated_relations}")

            except Exception as e:
                logger.error(f"Ошибка при миграции городов для пользователя {telegram_id_str}: {e}")
                db.rollback()
                continue

        db.commit()
        logger.info(
            f"Миграция городов завершена. Новых городов: {migrated_cities}, "
            f"связей: {migrated_relations}, пропущено: {skipped_relations}"
        )

    except FileNotFoundError:
        logger.warning("Файл user_cities.json не найден, пропускаем миграцию городов")
    except Exception as e:
        logger.error(f"Ошибка при миграции городов: {e}")
        db.rollback()


def migrate_weather_cache(db):
    """Миграция кэша погоды из weather_cache.json"""
    logger.info("Начало миграции кэша погоды...")

    try:
        with open('weather_cache.json', 'r', encoding='utf-8') as f:
            weather_cache_data = json.load(f)

        migrated = 0
        skipped = 0

        for city_name_lower, weather_data in weather_cache_data.items():
            try:
                # Находим город
                city = db.query(City).filter(City.name_lower == city_name_lower).first()

                if not city:
                    logger.debug(f"Город {city_name_lower} не найден в БД, пропускаем кэш")
                    skipped += 1
                    continue

                # Проверяем, не существует ли уже кэш
                existing_cache = db.query(WeatherCache).filter(WeatherCache.city_id == city.id).first()

                if existing_cache:
                    # Обновляем существующий кэш
                    existing_cache.temperature = weather_data.get('temp', 0)
                    existing_cache.description = weather_data.get('description', '')
                    existing_cache.emoji = weather_data.get('emoji', '🌦️')
                    existing_cache.wind_speed = weather_data.get('wind_speed', 0)

                    # Парсим timestamp
                    updated_at_ts = weather_data.get('updated_at')
                    if updated_at_ts:
                        existing_cache.updated_at = datetime.fromtimestamp(updated_at_ts)
                else:
                    # Создаем новый кэш
                    updated_at_ts = weather_data.get('updated_at')
                    updated_at = datetime.fromtimestamp(updated_at_ts) if updated_at_ts else datetime.utcnow()

                    cache = WeatherCache(
                        city_id=city.id,
                        temperature=weather_data.get('temp', 0),
                        description=weather_data.get('description', ''),
                        emoji=weather_data.get('emoji', '🌦️'),
                        wind_speed=weather_data.get('wind_speed', 0),
                        updated_at=updated_at
                    )
                    db.add(cache)

                migrated += 1

                if migrated % 20 == 0:
                    db.commit()
                    logger.info(f"Мигрировано кэшей: {migrated}")

            except Exception as e:
                logger.error(f"Ошибка при миграции кэша для {city_name_lower}: {e}")
                continue

        db.commit()
        logger.info(f"Миграция кэша завершена. Мигрировано: {migrated}, пропущено: {skipped}")

    except FileNotFoundError:
        logger.warning("Файл weather_cache.json не найден, пропускаем миграцию кэша")
    except Exception as e:
        logger.error(f"Ошибка при миграции кэша погоды: {e}")
        db.rollback()


def main():
    """Основная функция миграции"""
    logger.info("=" * 50)
    logger.info("НАЧАЛО МИГРАЦИИ ДАННЫХ")
    logger.info("=" * 50)

    try:
        # Инициализируем базу данных
        logger.info("Инициализация базы данных...")
        init_db()

        # Получаем сессию БД
        db = get_db()

        # Мигрируем данные
        migrate_users(db)
        migrate_cities_and_user_cities(db)
        migrate_weather_cache(db)

        # Статистика
        total_users = db.query(User).count()
        total_cities = db.query(City).count()
        total_relations = db.query(UserCity).count()
        total_cache = db.query(WeatherCache).count()

        logger.info("=" * 50)
        logger.info("МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        logger.info(f"Всего пользователей: {total_users}")
        logger.info(f"Всего городов: {total_cities}")
        logger.info(f"Связей пользователь-город: {total_relations}")
        logger.info(f"Записей кэша: {total_cache}")
        logger.info("=" * 50)

        db.close()

    except Exception as e:
        logger.error(f"Критическая ошибка при миграции: {e}")
        raise


if __name__ == "__main__":
    main()
