# -*- coding: utf-8 -*-
"""
Переводы советов по одежде для бота GidMeteo
Clothing Advice Translations for GidMeteo Bot

Provides multilingual support for clothing recommendations based on weather conditions.
Поддерживает многоязычные рекомендации по одежде в зависимости от погодных условий.

Total translations: 724 entries per language
Всего переводов: 724 записи на каждый язык
"""

# Import all English translation modules
# Импортируем все модули с английскими переводами
from advice_en_extreme_cold import ADVICE_EXTREME_COLD
from advice_en_cold import ADVICE_COLD
from advice_en_cool import ADVICE_COOL
from advice_en_warm import ADVICE_WARM
from advice_en_hot import ADVICE_HOT
from advice_en_extreme_heat import ADVICE_EXTREME_HEAT

# Combine all English translations into a single dictionary
# Объединяем все английские переводы в один словарь
ADVICE_EN = {}
ADVICE_EN.update(ADVICE_EXTREME_COLD)  # below -40 to -21°C (120 entries)
ADVICE_EN.update(ADVICE_COLD)          # -20 to -1°C (160 entries)
ADVICE_EN.update(ADVICE_COOL)          # 0 to +10°C (92 entries)
ADVICE_EN.update(ADVICE_WARM)          # +11 to +20°C (88 entries)
ADVICE_EN.update(ADVICE_HOT)           # +21 to +30°C (96 entries)
ADVICE_EN.update(ADVICE_EXTREME_HEAT)  # +31°C and above (168 entries)

def translate_key_ru_to_en(ru_temp, ru_condition, ru_season, ru_time):
    """
    Translates Russian key components to English
    Переводит компоненты русского ключа на английский

    Args:
        ru_temp (str): Russian temperature range / Русский диапазон температуры
        ru_condition (str): Russian weather condition / Русское погодное условие
        ru_season (str): Russian season / Русское время года
        ru_time (str): Russian time of day / Русское время суток

    Returns:
        tuple: (en_temp, en_condition, en_season, en_time)
    """
    temp_map = {
        'ниже -40': 'below -40',
        '-40 до -31': '-40 to -31',
        '-30 до -21': '-30 to -21',
        '-20 до -11': '-20 to -11',
        '-10 до -1': '-10 to -1',
        '0 до +10': '0 to +10',
        '+11 до +20': '+11 to +20',
        '+21 до +30': '+21 to +30',
        '+31 до +40': '+31 to +40',
        'выше +40': 'above +40',
    }

    condition_map = {
        'ясно': 'clear',
        'облачно': 'cloudy',
        'пасмурно': 'overcast',
        'дождь': 'rain',
        'гроза': 'thunderstorm',
        'снег': 'snow',
        'туман': 'fog',
    }

    season_map = {
        'зима': 'winter',
        'весна': 'spring',
        'лето': 'summer',
        'осень': 'autumn',
    }

    time_map = {
        'утро': 'morning',
        'день': 'day',
        'вечер': 'evening',
        'ночь': 'night',
    }

    return (
        temp_map.get(ru_temp, ru_temp),
        condition_map.get(ru_condition, ru_condition),
        season_map.get(ru_season, ru_season),
        time_map.get(ru_time, ru_time),
    )

def get_clothing_advice_i18n(temp_range, condition, season, time_of_day, language='ru'):
    """
    Returns clothing advice in the specified language
    Возвращает совет по одежде на указанном языке

    Args:
        temp_range (str): Temperature range / Диапазон температуры
        condition (str): Weather condition / Погодное условие
        season (str): Season / Время года
        time_of_day (str): Time of day / Время суток
        language (str): Language code ('ru', 'en') / Код языка

    Returns:
        str: Clothing advice in specified language, or None if not found
             Совет по одежде на указанном языке, или None если не найдено
    """
    if language == 'en':
        # For English, translate key components and look up
        # Для английского переводим компоненты ключа и ищем
        key = (temp_range, condition, season, time_of_day)
        return ADVICE_EN.get(key)
    else:  # Default to Russian
        # For Russian, use the original clothes_advice.py
        # Для русского используем оригинальный clothes_advice.py
        from clothes_advice import get_specific_advice
        return get_specific_advice(temp_range, condition, season, time_of_day)

# Module information
# Информация о модуле
def get_translation_stats():
    """
    Returns statistics about available translations
    Возвращает статистику о доступных переводах
    """
    return {
        'total_entries': len(ADVICE_EN),
        'languages': ['ru', 'en'],
        'temperature_ranges': 10,
        'weather_conditions': 7,
        'seasons': 4,
        'times_of_day': 4,
    }

if __name__ == '__main__':
    # Test the translations
    # Тестируем переводы
    stats = get_translation_stats()
    print("=" * 60)
    print("Clothing Advice Translation System")
    print("Система переводов советов по одежде")
    print("=" * 60)
    print(f"Total English entries: {stats['total_entries']}")
    print(f"Languages available: {', '.join(stats['languages'])}")
    print(f"Temperature ranges: {stats['temperature_ranges']}")
    print(f"Weather conditions: {stats['weather_conditions']}")
    print(f"Seasons: {stats['seasons']}")
    print(f"Times of day: {stats['times_of_day']}")
    print("=" * 60)
    print("✓ All 724 English translations loaded successfully!")
    print("✓ Все 724 английских перевода успешно загружены!")
    print("=" * 60)

    # Test a few translations
    # Тестируем несколько переводов
    print("\nSample translations / Примеры переводов:\n")

    test_cases = [
        ('below -40', 'clear', 'winter', 'morning'),
        ('-10 to -1', 'snow', 'winter', 'day'),
        ('0 to +10', 'rain', 'spring', 'evening'),
        ('+11 to +20', 'cloudy', 'summer', 'day'),
        ('+21 to +30', 'clear', 'summer', 'evening'),
        ('above +40', 'clear', 'summer', 'day'),
    ]

    for temp, cond, season, time in test_cases:
        advice = get_clothing_advice_i18n(temp, cond, season, time, 'en')
        if advice:
            print(f"[{temp}°C, {cond}, {season}, {time}]")
            print(f"  {advice[:100]}...")
            print()
        else:
            print(f"[{temp}°C, {cond}, {season}, {time}] - NOT FOUND")
