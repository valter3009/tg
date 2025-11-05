"""
Система локализации для бота GidMeteo
Поддерживаемые языки: русский (ru), английский (en), испанский (es), немецкий (de)
"""

# Языки по умолчанию
DEFAULT_LANGUAGE = 'ru'
SUPPORTED_LANGUAGES = ['ru', 'en', 'es', 'de']

# Переводы интерфейса бота
BOT_TRANSLATIONS = {
    'ru': {
        'refresh_button': '🔄 Обновить',
        'add_city': 'Добавить город',
        'remove_city': 'Удалить город',
        'back_button': 'Назад',
        'welcome_text': 'Отправь мне название населенного пункта и я скажу какая там погода и температура, дам советы по одежде.\n\n💡 Отправляй прогнозы в любой чат: введи @MeteoblueBot + город в любом чате Телеграм',
        'welcome_text_with_cities': '{cities}\n\nОтправь мне название населенного пункта и я скажу какая там погода и температура, дам советы по одежде.\n\n💡 Отправляй прогнозы в любой чат: введи @MeteoblueBot + город в любом чате Телеграм',
        'city_not_found': 'Город не найден. Проверьте написание.',
        'weather_error': 'Произошла ошибка при получении данных о погоде. Попробуйте позже.',
        'unknown_command': 'Неизвестная команда. Попробуйте /start',
        'wind_speed': 'Скорость ветра',
        'update_time': 'Время обновления',
        'temperature': 't°',
        'feels_like': 't°ощущ.',
        'reminder_text': '🌤️ Привет! Пора узнать погоду на сегодня!\n\nОтправьте мне название города, чтобы получить актуальную информацию о погоде и рекомендации по одежде.\n\nПросто напишите название любого населенного пункта, и я расскажу:\n• Текущую температуру\n• Погодные условия\n• Что лучше надеть\n\nПопробуйте прямо сейчас! 😊',
        'language_selection': 'Выберите язык / Select language',
        'language_changed': 'Язык изменен на русский',
    },
    'en': {
        'refresh_button': '🔄 Refresh',
        'add_city': 'Add city',
        'remove_city': 'Remove city',
        'back_button': 'Back',
        'welcome_text': 'Send me the name of a city and I will tell you the weather and temperature there, and give you clothing advice.\n\n💡 Send forecasts to any chat: enter @MeteoblueBot + city in any Telegram chat',
        'welcome_text_with_cities': '{cities}\n\nSend me the name of a city and I will tell you the weather and temperature there, and give you clothing advice.\n\n💡 Send forecasts to any chat: enter @MeteoblueBot + city in any Telegram chat',
        'city_not_found': 'City not found. Check the spelling.',
        'weather_error': 'An error occurred while retrieving weather data. Try again later.',
        'unknown_command': 'Unknown command. Try /start',
        'wind_speed': 'Wind speed',
        'update_time': 'Update time',
        'temperature': 'Temp',
        'feels_like': 'Feels like',
        'reminder_text': '🌤️ Hello! Time to check today\'s weather!\n\nSend me the name of a city to get current weather information and clothing recommendations.\n\nJust write the name of any city, and I will tell you:\n• Current temperature\n• Weather conditions\n• What to wear\n\nTry it now! 😊',
        'language_selection': 'Select language / Выберите язык',
        'language_changed': 'Language changed to English',
    },
    'es': {
        'refresh_button': '🔄 Actualizar',
        'add_city': 'Añadir ciudad',
        'remove_city': 'Eliminar ciudad',
        'back_button': 'Atrás',
        'welcome_text': 'Envíame el nombre de una ciudad y te diré el tiempo y la temperatura, y te daré consejos sobre la ropa.\n\n💡 Envía pronósticos a cualquier chat: escribe @MeteoblueBot + ciudad en cualquier chat de Telegram',
        'welcome_text_with_cities': '{cities}\n\nEnvíame el nombre de una ciudad y te diré el tiempo y la temperatura, y te daré consejos sobre la ropa.\n\n💡 Envía pronósticos a cualquier chat: escribe @MeteoblueBot + ciudad en cualquier chat de Telegram',
        'city_not_found': 'Ciudad no encontrada. Verifique la ortografía.',
        'weather_error': 'Se produjo un error al recuperar los datos meteorológicos. Inténtalo más tarde.',
        'unknown_command': 'Comando desconocido. Prueba /start',
        'wind_speed': 'Velocidad del viento',
        'update_time': 'Hora de actualización',
        'temperature': 'Temp',
        'feels_like': 'Sensación',
        'reminder_text': '🌤️ ¡Hola! ¡Es hora de conocer el clima de hoy!\n\nEnvíame el nombre de una ciudad para obtener información meteorológica actual y recomendaciones de ropa.\n\nSolo escribe el nombre de cualquier ciudad y te diré:\n• Temperatura actual\n• Condiciones meteorológicas\n• Qué ponerte\n\n¡Pruébalo ahora! 😊',
        'language_selection': 'Seleccionar idioma / Select language',
        'language_changed': 'Idioma cambiado a español',
    },
    'de': {
        'refresh_button': '🔄 Aktualisieren',
        'add_city': 'Stadt hinzufügen',
        'remove_city': 'Stadt entfernen',
        'back_button': 'Zurück',
        'welcome_text': 'Senden Sie mir den Namen einer Stadt und ich sage Ihnen das Wetter und die Temperatur dort und gebe Ihnen Kleidungsempfehlungen.\n\n💡 Senden Sie Prognosen an jeden Chat: Geben Sie @MeteoblueBot + Stadt in jedem Telegram-Chat ein',
        'welcome_text_with_cities': '{cities}\n\nSenden Sie mir den Namen einer Stadt und ich sage Ihnen das Wetter und die Temperatur dort und gebe Ihnen Kleidungsempfehlungen.\n\n💡 Senden Sie Prognosen an jeden Chat: Geben Sie @MeteoblueBot + Stadt in jedem Telegram-Chat ein',
        'city_not_found': 'Stadt nicht gefunden. Überprüfen Sie die Schreibweise.',
        'weather_error': 'Beim Abrufen der Wetterdaten ist ein Fehler aufgetreten. Versuchen Sie es später erneut.',
        'unknown_command': 'Unbekannter Befehl. Versuchen Sie /start',
        'wind_speed': 'Windgeschwindigkeit',
        'update_time': 'Aktualisierungszeit',
        'temperature': 'Temp',
        'feels_like': 'Gefühlt',
        'reminder_text': '🌤️ Hallo! Zeit, das heutige Wetter zu überprüfen!\n\nSenden Sie mir den Namen einer Stadt, um aktuelle Wetterinformationen und Kleidungsempfehlungen zu erhalten.\n\nSchreiben Sie einfach den Namen einer beliebigen Stadt, und ich sage Ihnen:\n• Aktuelle Temperatur\n• Wetterbedingungen\n• Was Sie anziehen sollten\n\nProbieren Sie es jetzt aus! 😊',
        'language_selection': 'Sprache wählen / Select language',
        'language_changed': 'Sprache auf Deutsch geändert',
    },
}

# Переводы интерфейса веб-приложения
WEBAPP_TRANSLATIONS = {
    'ru': {
        'search_placeholder': 'Введите название города...',
        'four_days': '4 дня',
        'seven_days': '7 дней',
        'satellite': 'Спутник',
        'precipitation': 'Осадки',
        'wind': 'Ветер',
        'loading': 'Загрузка метеосервиса...',
    },
    'en': {
        'search_placeholder': 'Enter city name...',
        'four_days': '4 days',
        'seven_days': '7 days',
        'satellite': 'Satellite',
        'precipitation': 'Precipitation',
        'wind': 'Wind',
        'loading': 'Loading weather service...',
    },
    'es': {
        'search_placeholder': 'Introduce el nombre de la ciudad...',
        'four_days': '4 días',
        'seven_days': '7 días',
        'satellite': 'Satélite',
        'precipitation': 'Precipitación',
        'wind': 'Viento',
        'loading': 'Cargando servicio meteorológico...',
    },
    'de': {
        'search_placeholder': 'Geben Sie den Stadtnamen ein...',
        'four_days': '4 Tage',
        'seven_days': '7 Tage',
        'satellite': 'Satellit',
        'precipitation': 'Niederschlag',
        'wind': 'Wind',
        'loading': 'Wetterdienst wird geladen...',
    },
}

def get_user_language(user_id, user_languages=None):
    """
    Получает язык пользователя из базы данных

    Args:
        user_id: ID пользователя
        user_languages: Словарь с языками пользователей

    Returns:
        str: Код языка ('ru', 'en', 'es', 'de')
    """
    if user_languages is None:
        return DEFAULT_LANGUAGE

    return user_languages.get(str(user_id), DEFAULT_LANGUAGE)

def set_user_language(user_id, language, user_languages):
    """
    Устанавливает язык пользователя

    Args:
        user_id: ID пользователя
        language: Код языка ('ru', 'en', 'es', 'de')
        user_languages: Словарь с языками пользователей

    Returns:
        dict: Обновленный словарь языков
    """
    if language not in SUPPORTED_LANGUAGES:
        language = DEFAULT_LANGUAGE

    user_languages[str(user_id)] = language
    return user_languages

def t(key, language='ru', context='bot', **kwargs):
    """
    Получает перевод по ключу

    Args:
        key: Ключ перевода
        language: Код языка
        context: Контекст ('bot' или 'webapp')
        **kwargs: Параметры для форматирования строки

    Returns:
        str: Переведенная строка
    """
    if context == 'bot':
        translations = BOT_TRANSLATIONS
    else:
        translations = WEBAPP_TRANSLATIONS

    if language not in translations:
        language = DEFAULT_LANGUAGE

    if key not in translations[language]:
        # Возвращаем русский вариант, если перевод не найден
        return translations[DEFAULT_LANGUAGE].get(key, key)

    text = translations[language][key]

    # Форматируем строку, если переданы параметры
    if kwargs:
        try:
            return text.format(**kwargs)
        except KeyError:
            return text

    return text
