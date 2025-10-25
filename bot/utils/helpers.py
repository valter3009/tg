"""
Вспомогательные функции
"""
from typing import Optional
from sqlalchemy.orm import Session
from bot.models import User, City, UserCity
import logging

logger = logging.getLogger(__name__)


def get_or_create_user(
    db: Session,
    telegram_id: int,
    username: str = None,
    first_name: str = None,
    last_name: str = None,
    source: str = 'start_command'
) -> Optional[User]:
    """
    Получает пользователя из БД или создает нового

    Args:
        db: Сессия базы данных
        telegram_id: ID пользователя в Telegram
        username: Имя пользователя
        first_name: Имя
        last_name: Фамилия
        source: Источник регистрации

    Returns:
        Объект User или None
    """
    try:
        user = db.query(User).filter(User.telegram_id == telegram_id).first()

        if not user:
            user = User(
                telegram_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                source=source
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            logger.info(f"Создан новый пользователь: {telegram_id} (@{username})")
        else:
            # Обновляем информацию пользователя
            updated = False
            if username and user.username != username:
                user.username = username
                updated = True
            if first_name and user.first_name != first_name:
                user.first_name = first_name
                updated = True
            if last_name and user.last_name != last_name:
                user.last_name = last_name
                updated = True
            if not user.is_active:
                user.is_active = True
                updated = True

            if updated:
                db.commit()
                logger.debug(f"Обновлена информация пользователя: {telegram_id}")

        return user

    except Exception as e:
        logger.error(f"Ошибка при получении/создании пользователя {telegram_id}: {e}")
        db.rollback()
        return None


def add_city_to_user(db: Session, user: User, city_name: str) -> tuple[bool, str]:
    """
    Добавляет город пользователю

    Args:
        db: Сессия базы данных
        user: Объект пользователя
        city_name: Название города

    Returns:
        Кортеж (успешно, сообщение)
    """
    try:
        # Получаем или создаем город
        from bot.services.weather import WeatherService

        city = WeatherService.get_or_create_city(db, city_name)
        if not city:
            return False, "Ошибка при создании города"

        # Проверяем, не добавлен ли уже этот город
        existing = db.query(UserCity).filter(
            UserCity.user_id == user.id,
            UserCity.city_id == city.id
        ).first()

        if existing:
            return False, f"Город {city_name} уже добавлен в ваш список"

        # Получаем текущее количество городов пользователя
        cities_count = db.query(UserCity).filter(UserCity.user_id == user.id).count()

        # Добавляем город
        user_city = UserCity(
            user_id=user.id,
            city_id=city.id,
            order=cities_count
        )
        db.add(user_city)
        db.commit()

        logger.info(f"Добавлен город {city_name} для пользователя {user.telegram_id}")
        return True, f"Город {city_name} успешно добавлен"

    except Exception as e:
        logger.error(f"Ошибка при добавлении города {city_name}: {e}")
        db.rollback()
        return False, "Ошибка при добавлении города"


def remove_city_from_user(db: Session, user: User, city_name: str) -> tuple[bool, str]:
    """
    Удаляет город у пользователя

    Args:
        db: Сессия базы данных
        user: Объект пользователя
        city_name: Название города

    Returns:
        Кортеж (успешно, сообщение)
    """
    try:
        city = db.query(City).filter(City.name_lower == city_name.lower()).first()

        if not city:
            return False, f"Город {city_name} не найден"

        user_city = db.query(UserCity).filter(
            UserCity.user_id == user.id,
            UserCity.city_id == city.id
        ).first()

        if not user_city:
            return False, f"Город {city_name} не найден в вашем списке"

        db.delete(user_city)
        db.commit()

        logger.info(f"Удален город {city_name} у пользователя {user.telegram_id}")
        return True, f"Город {city_name} удален из вашего списка"

    except Exception as e:
        logger.error(f"Ошибка при удалении города {city_name}: {e}")
        db.rollback()
        return False, "Ошибка при удалении города"


def get_user_cities(db: Session, user: User) -> list:
    """
    Получает список городов пользователя

    Args:
        db: Сессия базы данных
        user: Объект пользователя

    Returns:
        Список объектов City
    """
    try:
        user_cities = db.query(City).join(UserCity).filter(
            UserCity.user_id == user.id
        ).order_by(UserCity.order).all()

        return user_cities

    except Exception as e:
        logger.error(f"Ошибка при получении городов пользователя {user.telegram_id}: {e}")
        return []


def format_temperature(temp: float) -> str:
    """
    Форматирует температуру с знаком +/-

    Args:
        temp: Температура

    Returns:
        Отформатированная строка температуры
    """
    if temp > 0:
        return f"+{temp:.1f}"
    else:
        return f"{temp:.1f}"
