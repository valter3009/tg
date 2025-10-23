"""
Модуль для создания сообщений бота
"""
from typing import Dict, List
from telebot import types

from .helpers import format_temperature, format_datetime, get_season, get_time_of_day
from ..services.clothes_advice import get_clothing_advice


class MessageBuilder:
    """Класс для создания сообщений и клавиатур"""

    @staticmethod
    def build_weather_message(city: str, weather_data: Dict) -> str:
        """
        Создает сообщение с информацией о погоде

        Args:
            city: название города
            weather_data: данные о погоде из weather_service

        Returns:
            str: отформатированное сообщение
        """
        temp_str = format_temperature(weather_data['temp'])
        description = weather_data['description']
        description_cap = description[0].upper() + description[1:]
        emoji = weather_data['emoji']
        wind_speed = weather_data['wind_speed']

        # Получаем время года и время суток
        season = get_season()
        time_of_day = get_time_of_day()

        # Получаем совет по одежде
        clothes_advice = get_clothing_advice(
            weather_data['temp'],
            description,
            season,
            time_of_day,
            wind_speed
        )

        # Температура ощущается (примерно на 2 градуса меньше)
        feels_like = weather_data['temp'] - 2
        temp_feels_str = format_temperature(feels_like)

        # Форматируем время обновления
        update_time = format_datetime(weather_data['updated_at'])

        message = (
            f"{emoji} {city} {description_cap}\n"
            f"🌡️ t° {temp_str}°C\n"
            f"🌡️ t°ощущ. {temp_feels_str}°C\n"
            f"💨 Скорость ветра | {wind_speed} м/с\n"
            f"{clothes_advice}\n"
            f"⏱️ Время обновления: {update_time}"
        )

        return message

    @staticmethod
    def build_welcome_message(user_cities: List[str], cities_weather: Dict[str, Dict]) -> str:
        """
        Создает приветственное сообщение

        Args:
            user_cities: список городов пользователя
            cities_weather: словарь {city: weather_data}

        Returns:
            str: приветственное сообщение
        """
        if not user_cities:
            return (
                "Отправь мне название населенного пункта и я скажу какая там погода "
                "и температура, дам советы по одежде.\n\n"
                "💡 Отправляй прогнозы в любой чат: введи @MeteoblueBot + город "
                "в любом чате Телеграм"
            )

        cities_text = []
        for city in user_cities:
            weather = cities_weather.get(city)
            if weather:
                temp_str = format_temperature(weather['temp'])
                city_text = f"{weather['emoji']} {city} {temp_str}°C"
            else:
                city_text = city
            cities_text.append(city_text)

        message = "\n".join(cities_text)
        message += (
            "\n\nОтправь мне название населенного пункта и я скажу какая там погода "
            "и температура, дам советы по одежде.\n\n"
            "💡 Отправляй прогнозы в любой чат: введи @MeteoblueBot + город "
            "в любом чате Телеграм"
        )

        return message

    @staticmethod
    def build_reminder_message() -> str:
        """Создает напоминание для пользователей без городов"""
        return (
            "🌤️ Привет! Пора узнать погоду на сегодня!\n\n"
            "Отправьте мне название города, чтобы получить актуальную информацию о погоде "
            "и рекомендации по одежде.\n\n"
            "Просто напишите название любого населенного пункта, и я расскажу:\n"
            "• Текущую температуру\n"
            "• Погодные условия\n"
            "• Что лучше надеть\n\n"
            "Попробуйте прямо сейчас! 😊"
        )

    @staticmethod
    def create_cities_keyboard(user_cities: List[str], cities_weather: Dict[str, Dict]) -> types.InlineKeyboardMarkup:
        """
        Создает клавиатуру с кнопками городов

        Args:
            user_cities: список городов пользователя
            cities_weather: словарь {city: weather_data}

        Returns:
            InlineKeyboardMarkup: клавиатура
        """
        markup = types.InlineKeyboardMarkup(row_width=1)

        for city in user_cities:
            weather = cities_weather.get(city)
            if weather:
                temp_str = format_temperature(weather['temp'])
                button_text = f"{weather['emoji']} {city} {temp_str}°C 💨{weather['wind_speed']}м/с"
            else:
                button_text = city

            markup.add(types.InlineKeyboardButton(
                text=button_text,
                callback_data=f"city_{city}"
            ))

        # Добавляем кнопку "Обновить" только если есть города
        if user_cities:
            markup.add(types.InlineKeyboardButton(
                text="🔄 Обновить",
                callback_data="refresh"
            ))

        return markup

    @staticmethod
    def create_weather_keyboard(city: str, is_saved: bool) -> types.InlineKeyboardMarkup:
        """
        Создает клавиатуру для страницы погоды города

        Args:
            city: название города
            is_saved: сохранен ли город у пользователя

        Returns:
            InlineKeyboardMarkup: клавиатура
        """
        markup = types.InlineKeyboardMarkup(row_width=2)

        if is_saved:
            markup.add(
                types.InlineKeyboardButton("Удалить город", callback_data=f"remove_{city}"),
                types.InlineKeyboardButton("Назад", callback_data="back")
            )
        else:
            markup.add(
                types.InlineKeyboardButton("Добавить город", callback_data=f"add_{city}"),
                types.InlineKeyboardButton("Назад", callback_data="back")
            )

        return markup
