"""
Translations for the weather bot
"""

TRANSLATIONS = {
    'ru': {
        # Buttons
        'refresh': '🔄 Обновить',
        'add_city': 'Добавить город',
        'remove_city': 'Удалить город',
        'back': 'Назад',

        # Welcome messages
        'welcome_with_cities': 'Отправь мне название населенного пункта и я скажу какая там погода и температура, дам советы по одежде.\n\n💡 Отправляй прогнозы в любой чат: введи @MeteoblueBot + город в любом чате Телеграм',
        'welcome_without_cities': 'Отправь мне название населенного пункта и я скажу какая там погода и температура, дам советы по одежде.\n\n💡 Отправляй прогнозы в любой чат: введи @MeteoblueBot + город в любом чате Телеграм',

        # Reminder message
        'reminder_title': '🌤️ Привет! Пора узнать погоду на сегодня!',
        'reminder_text': 'Отправьте мне название города, чтобы получить актуальную информацию о погоде и рекомендации по одежде.',
        'reminder_features': 'Просто напишите название любого населенного пункта, и я расскажу:',
        'reminder_temp': '• Текущую температуру',
        'reminder_conditions': '• Погодные условия',
        'reminder_advice': '• Что лучше надеть',
        'reminder_cta': 'Попробуйте прямо сейчас! 😊',

        # Errors
        'city_not_found': 'Город не найден. Проверьте написание.',
        'weather_error': 'Произошла ошибка при получении данных о погоде. Попробуйте позже.',
        'unknown_command': 'Неизвестная команда. Попробуйте /start',
        'general_error': 'Произошла ошибка. Попробуйте позже.',

        # Weather info
        'temp': '🌡️ t°',
        'feels_like': '🌡️ t°ощущ.',
        'wind_speed': '💨 Скорость ветра |',
        'update_time': '⏱️ Время обновления:',
        'weather_in': 'Погода в',

        # Units
        'meters_per_second': 'м/с',
        'celsius': '°C',

        # Admin commands
        'no_access': 'У вас нет доступа к этой команде.',
        'stats_error': 'Произошла ошибка при генерации отчета.',
        'check_users_error': 'Произошла ошибка при проверке пользователей.',
        'activity_report': 'Отчет об активности пользователей:',
        'user_status_check': 'Проверка статуса пользователей',

        # Stats labels
        'total_users': '📊 Общая статистика:\n• Всего пользователей:',
        'active_users': '• Активных:',
        'inactive_users': '• Неактивных (заблокировали бота):',
        'users_with_cities': '🏙️ По наличию городов:\n• С добавленными городами:',
        'users_without_cities': '• Без городов:',
        'from_additional_list': '📝 По источникам:\n• Из дополнительного списка:',
        'from_start_command': '• Через команду /start:',
        'active_percentage': '✅ Процент активных пользователей:',
    },
    'en': {
        # Buttons
        'refresh': '🔄 Refresh',
        'add_city': 'Add city',
        'remove_city': 'Remove city',
        'back': 'Back',

        # Welcome messages
        'welcome_with_cities': 'Send me the name of a city and I will tell you the weather and temperature there, and give you clothing advice.\n\n💡 Share forecasts in any chat: type @MeteoblueBot + city name in any Telegram chat',
        'welcome_without_cities': 'Send me the name of a city and I will tell you the weather and temperature there, and give you clothing advice.\n\n💡 Share forecasts in any chat: type @MeteoblueBot + city name in any Telegram chat',

        # Reminder message
        'reminder_title': '🌤️ Hello! Time to check today\'s weather!',
        'reminder_text': 'Send me a city name to get current weather information and clothing recommendations.',
        'reminder_features': 'Just write the name of any city, and I will tell you:',
        'reminder_temp': '• Current temperature',
        'reminder_conditions': '• Weather conditions',
        'reminder_advice': '• What to wear',
        'reminder_cta': 'Try it now! 😊',

        # Errors
        'city_not_found': 'City not found. Please check spelling.',
        'weather_error': 'An error occurred while fetching weather data. Please try later.',
        'unknown_command': 'Unknown command. Try /start',
        'general_error': 'An error occurred. Please try later.',

        # Weather info
        'temp': '🌡️ Temp',
        'feels_like': '🌡️ Feels like',
        'wind_speed': '💨 Wind speed |',
        'update_time': '⏱️ Updated at:',
        'weather_in': 'Weather in',

        # Units
        'meters_per_second': 'm/s',
        'celsius': '°C',

        # Admin commands
        'no_access': 'You do not have access to this command.',
        'stats_error': 'An error occurred while generating the report.',
        'check_users_error': 'An error occurred while checking users.',
        'activity_report': 'User activity report:',
        'user_status_check': 'User status check',

        # Stats labels
        'total_users': '📊 Overall statistics:\n• Total users:',
        'active_users': '• Active:',
        'inactive_users': '• Inactive (blocked bot):',
        'users_with_cities': '🏙️ By cities:\n• With added cities:',
        'users_without_cities': '• Without cities:',
        'from_additional_list': '📝 By source:\n• From additional list:',
        'from_start_command': '• Via /start command:',
        'active_percentage': '✅ Active users percentage:',
    }
}

def get_text(key, lang='ru'):
    """
    Get translated text by key

    Args:
        key (str): Translation key
        lang (str): Language code ('ru' or 'en')

    Returns:
        str: Translated text
    """
    return TRANSLATIONS.get(lang, TRANSLATIONS['ru']).get(key, key)

def get_weather_api_lang(lang='ru'):
    """
    Get OpenWeather API language code

    Args:
        lang (str): Bot language code ('ru' or 'en')

    Returns:
        str: OpenWeather API language code
    """
    return 'en' if lang == 'en' else 'ru'
