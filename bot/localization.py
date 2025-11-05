"""
Система локализации для GidMeteo бота
Поддержка русского (ru) и английского (en) языков

Примечание: Советы по одежде (clothes_advice) пока доступны только на русском языке.
"""

TRANSLATIONS = {
    'ru': {
        # Основные команды
        'error_occurred': "Произошла ошибка. Попробуйте позже.",
        'error_registration': "Ошибка при регистрации пользователя. Попробуйте позже.",
        'error_start': "Ошибка. Начните с /start",
        'error_getting_weather': "❌ Ошибка при получении погоды",
        'error_adding': "Ошибка при добавлении",
        'error_deleting': "Ошибка при удалении",
        'error_refresh': "Ошибка при обновлении",

        # Приветственное сообщение
        'welcome_text': "Отправь мне название населенного пункта и я скажу какая там погода и температура, дам советы по одежде.\n\n💡 Отправляй прогнозы в любой чат: введи @MeteoblueBot + город в любом чате Телеграм",
        'welcome_with_cities': "\n\nОтправь мне название населенного пункта и я скажу какая там погода и температура, дам советы по одежде.\n\n💡 Отправляй прогнозы в любой чат: введи @MeteoblueBot + город в любом чате Телеграм",

        # Кнопки
        'btn_refresh': "🔄 Обновить",
        'btn_back': "◀️ Назад",
        'btn_delete_city': "🗑️ Удалить город",
        'btn_add_favorite': "➕ Добавить в избранное",
        'btn_switch_to_en': "EN",
        'btn_switch_to_ru': "RU",

        # Сообщения о городах
        'city_not_found': "❌ Город '{city}' не найден. Проверьте правильность написания.",
        'local_time': "🕐 Местное время:",
        'temperature': "🌡️ Температура:",
        'wind': "💨 Ветер:",

        # Статистика
        'stats_title': "📊 Статистика бота\n\n",
        'stats_total_users': "👥 Всего пользователей:",
        'stats_active': "✅ Активных:",
        'stats_inactive': "❌ Неактивных:",
        'stats_with_cities': "🏙️ С городами:",
        'stats_without_cities': "🚫 Без городов:",
        'stats_activity_7days': "📈 Активность за 7 дней:",
        'stats_no_activity': "Нет активности за последние 7 дней",
        'stats_error': "⚠️ Не удалось получить статистику пользователей",
        'stats_error_msg': "Ошибка при получении статистики:",

        # Callback уведомления
        'updated': "✅ Обновлено",
        'weather_updated': "✅ Погода обновлена",
        'language_switched': "✅ Язык изменен на русский",

        # Inline запросы
        'inline_hint_title': "🌤️ Введите название города",
        'inline_hint_description': "Начните вводить название города для получения погоды",
        'inline_hint_message': "Используйте @gidmeteo_bot <название города> для получения погоды",
        'inline_city_not_found': "❌ Город \"{city}\" не найден",
        'inline_check_spelling': "Проверьте правильность написания",
        'inline_city_not_found_msg': "Город \"{city}\" не найден. Проверьте правильность написания.",
        'inline_error': "❌ Ошибка",
        'inline_error_description': "Произошла ошибка при получении погоды",
        'inline_error_msg': "Произошла ошибка при получении погоды. Попробуйте позже.",
    },

    'en': {
        # Basic commands
        'error_occurred': "An error occurred. Please try again later.",
        'error_registration': "Error registering user. Please try again later.",
        'error_start': "Error. Start with /start",
        'error_getting_weather': "❌ Error getting weather",
        'error_adding': "Error adding",
        'error_deleting': "Error deleting",
        'error_refresh': "Error refreshing",

        # Welcome message
        'welcome_text': "Send me a city name and I'll tell you the weather and temperature there, and give you clothing advice.\n\n💡 Share forecasts in any chat: type @MeteoblueBot + city in any Telegram chat",
        'welcome_with_cities': "\n\nSend me a city name and I'll tell you the weather and temperature there, and give you clothing advice.\n\n💡 Share forecasts in any chat: type @MeteoblueBot + city in any Telegram chat",

        # Buttons
        'btn_refresh': "🔄 Refresh",
        'btn_back': "◀️ Back",
        'btn_delete_city': "🗑️ Delete city",
        'btn_add_favorite': "➕ Add to favorites",
        'btn_switch_to_en': "EN",
        'btn_switch_to_ru': "RU",

        # City messages
        'city_not_found': "❌ City '{city}' not found. Please check the spelling.",
        'local_time': "🕐 Local time:",
        'temperature': "🌡️ Temperature:",
        'wind': "💨 Wind:",

        # Statistics
        'stats_title': "📊 Bot Statistics\n\n",
        'stats_total_users': "👥 Total users:",
        'stats_active': "✅ Active:",
        'stats_inactive': "❌ Inactive:",
        'stats_with_cities': "🏙️ With cities:",
        'stats_without_cities': "🚫 Without cities:",
        'stats_activity_7days': "📈 Activity in 7 days:",
        'stats_no_activity': "No activity in the last 7 days",
        'stats_error': "⚠️ Failed to get user statistics",
        'stats_error_msg': "Error getting statistics:",

        # Callback notifications
        'updated': "✅ Updated",
        'weather_updated': "✅ Weather updated",
        'language_switched': "✅ Language changed to English",

        # Inline queries
        'inline_hint_title': "🌤️ Enter city name",
        'inline_hint_description': "Start typing a city name to get weather",
        'inline_hint_message': "Use @gidmeteo_bot <city name> to get weather",
        'inline_city_not_found': "❌ City \"{city}\" not found",
        'inline_check_spelling': "Check the spelling",
        'inline_city_not_found_msg': "City \"{city}\" not found. Please check the spelling.",
        'inline_error': "❌ Error",
        'inline_error_description': "An error occurred while getting weather",
        'inline_error_msg': "An error occurred while getting weather. Please try again later.",
    }
}


def get_text(lang: str, key: str, **kwargs) -> str:
    """
    Получить переведенный текст

    Args:
        lang: Код языка ('ru' или 'en')
        key: Ключ перевода
        **kwargs: Параметры для форматирования (например, city='Moscow')

    Returns:
        Переведенный текст
    """
    # Если язык не поддерживается, используем русский по умолчанию
    if lang not in TRANSLATIONS:
        lang = 'ru'

    # Получаем текст из словаря переводов
    text = TRANSLATIONS[lang].get(key, TRANSLATIONS['ru'].get(key, key))

    # Форматируем текст с параметрами, если они есть
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass

    return text


def get_language_from_user(user) -> str:
    """
    Получить язык пользователя

    Args:
        user: Объект пользователя из базы данных

    Returns:
        Код языка ('ru' или 'en')
    """
    if hasattr(user, 'language') and user.language:
        return user.language
    return 'ru'  # По умолчанию русский
