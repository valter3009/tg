"""
Вспомогательные функции для бота
"""
from datetime import datetime
from typing import Dict, Optional


def format_datetime(timestamp: int) -> str:
    """Форматирует timestamp в читаемый формат"""
    return datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M:%S')


def get_season() -> str:
    """
    Определяет текущее время года

    Returns:
        str: 'зима', 'весна', 'лето' или 'осень'
    """
    month = datetime.now().month

    if month in [12, 1, 2]:
        return 'зима'
    elif month in [3, 4, 5]:
        return 'весна'
    elif month in [6, 7, 8]:
        return 'лето'
    else:  # 9, 10, 11
        return 'осень'


def get_time_of_day() -> str:
    """
    Определяет текущее время суток

    Returns:
        str: 'утро', 'день', 'вечер' или 'ночь'
    """
    hour = datetime.now().hour

    if 6 <= hour < 12:
        return 'утро'
    elif 12 <= hour < 18:
        return 'день'
    elif 18 <= hour < 24:
        return 'вечер'
    else:  # 0 <= hour < 6
        return 'ночь'


def format_temperature(temp: float) -> str:
    """
    Форматирует температуру с знаком +/-

    Args:
        temp: температура в градусах Цельсия

    Returns:
        str: отформатированная строка вида "+15" или "-5"
    """
    if temp > 0:
        return f"+{temp}"
    return str(temp)


def is_auto_update_time() -> bool:
    """
    Проверяет, наступило ли время автоматического обновления
    (каждые 4 часа: 00:01, 04:01, 08:01, 12:01, 16:01, 20:01)

    Returns:
        bool: True если сейчас время автообновления
    """
    now = datetime.now()
    return now.minute == 1 and now.hour % 4 == 0
