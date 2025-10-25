"""
Основной файл Telegram бота GidMeteo
"""
import logging
import time
import threading
import os
import json
from datetime import datetime
import telebot
from telebot import types
from flask import Flask
from threading import Thread

# Импорты проекта
from bot.config import config
from bot.database import init_db, get_db, close_db
from bot.models import User, UserCity, City
from bot.services.weather import WeatherService
from bot.services.notifications import NotificationService
from bot.services.analytics import AnalyticsService
from bot.services.timezone import TimezoneService
from bot.utils.helpers import get_or_create_user, add_city_to_user, get_user_cities, format_temperature
from bot.utils.clothes_advice import get_clothing_advice

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(config.LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = telebot.TeleBot(config.TELEGRAM_TOKEN)
notification_service = NotificationService(bot)

# Хранилище последних сообщений
last_messages = {}


# Flask keepalive для Railway
app = Flask(__name__)


@app.route('/')
def home():
    return "GidMeteo Bot is running!"


def run_flask():
    """Запуск Flask сервера в отдельном потоке"""
    app.run(host='0.0.0.0', port=config.FLASK_PORT)


# =======================
# ОБРАБОТЧИКИ КОМАНД
# =======================

@bot.message_handler(commands=['start'])
def handle_start(message):
    """Обработчик команды /start"""
    try:
        db = get_db()

        # Получаем или создаем пользователя
        user = get_or_create_user(
            db,
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            message.from_user.last_name
        )

        if not user:
            bot.send_message(message.chat.id, "Ошибка при регистрации пользователя. Попробуйте позже.")
            return

        # Логируем активность
        AnalyticsService.log_activity(db, message.from_user.id, 'start')

        # Отправляем приветственное сообщение
        send_welcome_message(message.chat.id, db, user)

        db.close()

    except Exception as e:
        logger.error(f"Ошибка в handle_start: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте позже.")


@bot.message_handler(commands=['stats'])
def handle_stats(message):
    """Обработчик команды /stats (только для админов)"""
    try:
        db = get_db()

        # РЕАЛЬНЫЙ подсчет прямо из базы
        total_real = db.query(User).count()
        active_real = db.query(User).filter(User.is_active == True).count()

        # Получаем статистику через сервис
        user_stats = AnalyticsService.get_user_stats(db)
        activity_stats = AnalyticsService.get_activity_stats(db, days=7)

        # Проверяем, что статистика получена
        if not user_stats:
            bot.send_message(message.chat.id, "⚠️ Не удалось получить статистику пользователей")
            db.close()
            return

        stats_message = (
            "📊 Статистика бота\n\n"
            f"👥 Всего пользователей: {user_stats.get('total_users', 0)} (реально в БД: {total_real})\n"
            f"✅ Активных: {user_stats.get('active_users', 0)} (реально: {active_real})\n"
            f"❌ Неактивных: {user_stats.get('inactive_users', 0)}\n"
            f"🏙️ С городами: {user_stats.get('users_with_cities', 0)}\n"
            f"🚫 Без городов: {user_stats.get('users_without_cities', 0)}\n\n"
            f"📈 Активность за 7 дней:\n"
        )

        activity_by_type = activity_stats.get('activity_by_type', {})
        if activity_by_type:
            for activity_type, count in activity_by_type.items():
                stats_message += f"• {activity_type}: {count}\n"
        else:
            stats_message += "Нет активности за последние 7 дней\n"

        bot.send_message(message.chat.id, stats_message)

        db.close()

    except Exception as e:
        logger.error(f"Ошибка в handle_stats: {e}", exc_info=True)
        bot.send_message(message.chat.id, f"Ошибка при получении статистики: {str(e)}")


@bot.message_handler(commands=['migrate'])
def handle_migrate(message):
    """Обработчик команды /migrate - принудительная миграция данных"""
    try:
        db = get_db()

        if not os.path.exists('all_users.json'):
            bot.send_message(message.chat.id, "❌ Файл all_users.json не найден")
            db.close()
            return

        # Показываем информацию о файлах
        with open('all_users.json', 'r', encoding='utf-8') as f:
            all_users = json.load(f)

        with open('user_cities.json', 'r', encoding='utf-8') as f:
            user_cities = json.load(f)

        bot.send_message(
            message.chat.id,
            f"📦 Найдены файлы:\n"
            f"• all_users.json: {len(all_users)} пользователей\n"
            f"• user_cities.json: {len(user_cities)} записей\n\n"
            f"⏳ Запуск миграции..."
        )

        from migrate_data import migrate_users, migrate_cities_and_user_cities

        users_before = db.query(User).count()
        active_before = db.query(User).filter(User.is_active == True).count()

        migrate_users(db)
        migrate_cities_and_user_cities(db)

        users_after = db.query(User).count()
        active_after = db.query(User).filter(User.is_active == True).count()
        new_users = users_after - users_before

        # Детальная статистика
        all_users_list = db.query(User).all()
        sources = {}
        for u in all_users_list:
            sources[u.source] = sources.get(u.source, 0) + 1

        source_text = "\n".join([f"  • {k}: {v}" for k, v in sources.items()])

        # Подсчитываем изменения
        users_created = new_users
        users_updated = users_before  # Все существующие пользователи были обновлены
        active_change = active_after - active_before

        bot.send_message(
            message.chat.id,
            f"✅ Миграция завершена!\n\n"
            f"📊 Результаты:\n"
            f"• Всего пользователей: {users_after} (было: {users_before})\n"
            f"• Активных пользователей: {active_after} (было: {active_before}, изменение: {'+' if active_change >= 0 else ''}{active_change})\n"
            f"• Создано новых: {users_created}\n"
            f"• Обновлено существующих: {users_updated}\n\n"
            f"📋 Источники регистрации:\n{source_text}"
        )

        db.close()

    except Exception as e:
        logger.error(f"Ошибка при миграции: {e}", exc_info=True)
        bot.send_message(message.chat.id, f"❌ Ошибка при миграции: {str(e)}")


@bot.message_handler(func=lambda message: True, content_types=['text'])
def handle_text(message):
    """Обработчик текстовых сообщений (город)"""
    try:
        # Удаляем сообщение пользователя сразу
        delete_message_safe(message.chat.id, message.message_id)

        db = get_db()
        city_name = message.text.strip()

        # Получаем пользователя
        user = db.query(User).filter(User.telegram_id == message.from_user.id).first()

        if not user:
            user = get_or_create_user(
                db,
                message.from_user.id,
                message.from_user.username,
                message.from_user.first_name,
                message.from_user.last_name
            )

        # Получаем погоду
        weather = WeatherService.get_weather(db, city_name)

        if not weather:
            # Если город не найден, отправляем временное сообщение
            error_msg = bot.send_message(
                message.chat.id,
                f"❌ Город '{city_name}' не найден. Проверьте правильность написания."
            )
            # Удаляем сообщение об ошибке через 3 секунды
            threading.Timer(3.0, lambda: delete_message_safe(message.chat.id, error_msg.message_id)).start()
            db.close()
            return

        # Получаем местное время города
        local_time, timezone_name, formatted_time = TimezoneService.format_city_time(city_name)

        # Получаем совет по одежде с учетом местного времени ГОРОДА
        advice = get_clothing_advice(
            weather['temp'],
            weather['description'],
            wind_speed=weather['wind_speed'],
            local_datetime=local_time
        )

        # Форматируем ответ с местным временем города
        temp_str = format_temperature(weather['temp'])
        response = (
            f"{weather['emoji']} *{city_name}*\n"
            f"🕐 Местное время: {formatted_time}\n\n"
            f"🌡️ Температура: {temp_str}°C\n"
            f"☁️ {weather['description'].capitalize()}\n"
            f"💨 Ветер: {weather['wind_speed']} м/с\n\n"
            f"{advice}"
        )

        # Создаем кнопки "Назад" и "Добавить в избранное"
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("◀️ Назад", callback_data="back_to_start"),
            types.InlineKeyboardButton("➕ Добавить в избранное", callback_data=f"add_{city_name}")
        )

        # Пытаемся редактировать последнее стартовое сообщение
        if message.chat.id in last_messages:
            last_msg_id = last_messages[message.chat.id].get('message_id')
            if last_msg_id:
                try:
                    bot.edit_message_text(
                        response,
                        message.chat.id,
                        last_msg_id,
                        reply_markup=markup,
                        parse_mode='Markdown'
                    )
                except Exception as e:
                    logger.debug(f"Не удалось отредактировать сообщение {last_msg_id}: {e}")
                    # Если не удалось отредактировать, отправляем новое
                    sent_msg = bot.send_message(message.chat.id, response, reply_markup=markup, parse_mode='Markdown')
                    last_messages[message.chat.id] = {'message_id': sent_msg.message_id, 'timestamp': time.time()}
            else:
                # Если нет ID сообщения, отправляем новое
                sent_msg = bot.send_message(message.chat.id, response, reply_markup=markup, parse_mode='Markdown')
                last_messages[message.chat.id] = {'message_id': sent_msg.message_id, 'timestamp': time.time()}
        else:
            # Если нет записи о последнем сообщении, отправляем новое
            sent_msg = bot.send_message(message.chat.id, response, reply_markup=markup, parse_mode='Markdown')
            last_messages[message.chat.id] = {'message_id': sent_msg.message_id, 'timestamp': time.time()}

        # Если у пользователя нет timezone, пытаемся определить
        if user.timezone == 'UTC':
            timezone = TimezoneService.get_timezone_from_city(city_name)
            if timezone and timezone != 'UTC':
                user.timezone = timezone
                db.commit()
                logger.info(f"Установлен timezone {timezone} для пользователя {user.telegram_id}")

        db.close()

    except Exception as e:
        logger.error(f"Ошибка в handle_text: {e}")
        # Отправляем временное сообщение об ошибке
        error_msg = bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте еще раз.")
        threading.Timer(3.0, lambda: delete_message_safe(message.chat.id, error_msg.message_id)).start()


# =======================
# ОБРАБОТЧИКИ CALLBACK
# =======================

@bot.callback_query_handler(func=lambda call: call.data == 'refresh')
def handle_refresh(call):
    """Обработчик кнопки обновления"""
    try:
        db = get_db()
        user = db.query(User).filter(User.telegram_id == call.from_user.id).first()

        if not user:
            bot.answer_callback_query(call.id, "Ошибка. Начните с /start")
            db.close()
            return

        # Логируем активность
        AnalyticsService.log_activity(db, call.from_user.id, 'refresh')

        # Обновляем сообщение
        send_welcome_message(call.message.chat.id, db, user, call.message.message_id)

        bot.answer_callback_query(call.id, "✅ Обновлено")
        db.close()

    except Exception as e:
        logger.error(f"Ошибка в handle_refresh: {e}")
        bot.answer_callback_query(call.id, "Ошибка при обновлении")


@bot.callback_query_handler(func=lambda call: call.data.startswith('city_'))
def handle_city_click(call):
    """Обработчик нажатия на город"""
    try:
        db = get_db()
        city_name = call.data.replace('city_', '')

        user = db.query(User).filter(User.telegram_id == call.from_user.id).first()

        if not user:
            bot.answer_callback_query(call.id, "Ошибка. Начните с /start")
            db.close()
            return

        # Логируем активность
        AnalyticsService.log_activity(db, call.from_user.id, 'city_click', city_name)

        # Получаем погоду
        weather = WeatherService.get_weather(db, city_name, use_cache=False)  # Принудительно обновляем

        if not weather:
            bot.answer_callback_query(call.id, "❌ Ошибка при получении погоды")
            db.close()
            return

        # Получаем местное время города
        local_time, timezone_name, formatted_time = TimezoneService.format_city_time(city_name)

        # Получаем совет по одежде с учетом местного времени ГОРОДА
        advice = get_clothing_advice(
            weather['temp'],
            weather['description'],
            wind_speed=weather['wind_speed'],
            local_datetime=local_time
        )

        # Форматируем ответ с местным временем города
        temp_str = format_temperature(weather['temp'])
        response = (
            f"{weather['emoji']} *{city_name}*\n"
            f"🕐 Местное время: {formatted_time}\n\n"
            f"🌡️ Температура: {temp_str}°C\n"
            f"☁️ {weather['description'].capitalize()}\n"
            f"💨 Ветер: {weather['wind_speed']} м/с\n\n"
            f"{advice}"
        )

        # Добавляем кнопки "Назад" и "Удалить город"
        markup = types.InlineKeyboardMarkup(row_width=2)
        markup.add(
            types.InlineKeyboardButton("◀️ Назад", callback_data="refresh"),
            types.InlineKeyboardButton("🗑️ Удалить город", callback_data=f"delete_{city_name}")
        )

        # Редактируем сообщение вместо отправки нового
        try:
            bot.edit_message_text(
                response,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup,
                parse_mode='Markdown'
            )
        except:
            # Если не удалось отредактировать, отправляем новое
            bot.send_message(call.message.chat.id, response, reply_markup=markup, parse_mode='Markdown')

        bot.answer_callback_query(call.id, "✅ Погода обновлена")

        db.close()

    except Exception as e:
        logger.error(f"Ошибка в handle_city_click: {e}")
        bot.answer_callback_query(call.id, "Ошибка")


@bot.callback_query_handler(func=lambda call: call.data.startswith('add_'))
def handle_add_city(call):
    """Обработчик добавления города в избранное"""
    try:
        db = get_db()
        city_name = call.data.replace('add_', '')

        user = db.query(User).filter(User.telegram_id == call.from_user.id).first()

        if not user:
            bot.answer_callback_query(call.id, "Ошибка. Начните с /start")
            db.close()
            return

        # Добавляем город
        success, message = add_city_to_user(db, user, city_name)

        if success:
            bot.answer_callback_query(call.id, f"✅ {message}")

            # Редактируем сообщение в обновленное стартовое сообщение
            send_welcome_message(call.message.chat.id, db, user, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, f"❌ {message}")

        db.close()

    except Exception as e:
        logger.error(f"Ошибка в handle_add_city: {e}")
        bot.answer_callback_query(call.id, "Ошибка при добавлении")


@bot.callback_query_handler(func=lambda call: call.data == 'back_to_start')
def handle_back_to_start(call):
    """Обработчик кнопки 'Назад' - возврат к стартовому сообщению"""
    try:
        db = get_db()
        user = db.query(User).filter(User.telegram_id == call.from_user.id).first()

        if not user:
            bot.answer_callback_query(call.id, "Ошибка. Начните с /start")
            db.close()
            return

        # Редактируем сообщение обратно в стартовое сообщение
        send_welcome_message(call.message.chat.id, db, user, call.message.message_id)

        bot.answer_callback_query(call.id, "")
        db.close()

    except Exception as e:
        logger.error(f"Ошибка в handle_back_to_start: {e}")
        bot.answer_callback_query(call.id, "Ошибка")


@bot.callback_query_handler(func=lambda call: call.data.startswith('delete_'))
def handle_delete_city(call):
    """Обработчик удаления города из избранного"""
    try:
        db = get_db()
        city_name = call.data.replace('delete_', '')

        user = db.query(User).filter(User.telegram_id == call.from_user.id).first()

        if not user:
            bot.answer_callback_query(call.id, "Ошибка. Начните с /start")
            db.close()
            return

        # Импортируем функцию удаления
        from bot.utils.helpers import remove_city_from_user

        # Удаляем город
        success, message = remove_city_from_user(db, user, city_name)

        if success:
            bot.answer_callback_query(call.id, f"✅ {message}")

            # Обновляем приветственное сообщение (редактируем)
            send_welcome_message(call.message.chat.id, db, user, call.message.message_id)
        else:
            bot.answer_callback_query(call.id, f"❌ {message}")

        db.close()

    except Exception as e:
        logger.error(f"Ошибка в handle_delete_city: {e}")
        bot.answer_callback_query(call.id, "Ошибка при удалении")


@bot.inline_handler(func=lambda query: True)
def handle_inline_query(query):
    """Обработчик inline-запросов"""
    try:
        city_name = query.query.strip()

        if not city_name:
            # Если город не указан, показываем подсказку
            results = []
            article = types.InlineQueryResultArticle(
                id='1',
                title='🌤️ Введите название города',
                description='Начните вводить название города для получения погоды',
                input_message_content=types.InputTextMessageContent(
                    message_text='Используйте @gidmeteo_bot <название города> для получения погоды'
                )
            )
            results.append(article)
            bot.answer_inline_query(query.id, results, cache_time=1)
            return

        db = get_db()

        # Получаем погоду
        weather = WeatherService.get_weather(db, city_name)

        if not weather:
            # Город не найден
            results = []
            article = types.InlineQueryResultArticle(
                id='1',
                title=f'❌ Город "{city_name}" не найден',
                description='Проверьте правильность написания',
                input_message_content=types.InputTextMessageContent(
                    message_text=f'Город "{city_name}" не найден. Проверьте правильность написания.'
                )
            )
            results.append(article)
            bot.answer_inline_query(query.id, results, cache_time=1)
            db.close()
            return

        # Получаем местное время города
        local_time, timezone_name, formatted_time = TimezoneService.format_city_time(city_name)

        # Получаем совет по одежде
        advice = get_clothing_advice(
            weather['temp'],
            weather['description'],
            wind_speed=weather['wind_speed'],
            local_datetime=local_time
        )

        # Форматируем сообщение
        temp_str = format_temperature(weather['temp'])
        message_text = (
            f"{weather['emoji']} *{city_name}*\n"
            f"🕐 Местное время: {formatted_time}\n\n"
            f"🌡️ Температура: {temp_str}°C\n"
            f"☁️ {weather['description'].capitalize()}\n"
            f"💨 Ветер: {weather['wind_speed']} м/с\n\n"
            f"{advice}"
        )

        # Создаем результат
        results = []
        article = types.InlineQueryResultArticle(
            id='1',
            title=f'{weather["emoji"]} {city_name}: {temp_str}°C',
            description=f'{weather["description"].capitalize()}, ветер {weather["wind_speed"]} м/с',
            input_message_content=types.InputTextMessageContent(
                message_text=message_text,
                parse_mode='Markdown'
            )
        )
        results.append(article)

        bot.answer_inline_query(query.id, results, cache_time=300)

        db.close()

    except Exception as e:
        logger.error(f"Ошибка в handle_inline_query: {e}")
        try:
            results = []
            article = types.InlineQueryResultArticle(
                id='1',
                title='❌ Ошибка',
                description='Произошла ошибка при получении погоды',
                input_message_content=types.InputTextMessageContent(
                    message_text='Произошла ошибка при получении погоды. Попробуйте позже.'
                )
            )
            results.append(article)
            bot.answer_inline_query(query.id, results, cache_time=1)
        except:
            pass


# =======================
# ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ
# =======================

def delete_message_safe(chat_id, message_id):
    """Безопасно удаляет сообщение, игнорируя ошибки"""
    try:
        bot.delete_message(chat_id, message_id)
    except Exception as e:
        logger.debug(f"Не удалось удалить сообщение {message_id}: {e}")


def send_welcome_message(chat_id, db, user, message_id=None):
    """Отправляет приветственное сообщение с городами пользователя"""
    try:
        # Получаем города пользователя
        cities = get_user_cities(db, user)

        # Создаем клавиатуру
        markup = types.InlineKeyboardMarkup(row_width=1)

        cities_weather_text = []

        for city in cities:
            # Получаем погоду из кэша
            weather = WeatherService.get_weather(db, city.name)

            if weather:
                # Получаем местное время города
                local_time, _, formatted_time = TimezoneService.format_city_time(city.name)
                time_emoji = TimezoneService.get_time_of_day_emoji(local_time.hour)

                temp_str = format_temperature(weather['temp'])
                wind_speed = weather['wind_speed']
                button_text = f"{weather['emoji']} {city.name} {temp_str}°C 💨 {wind_speed} м/с {time_emoji}"
                cities_weather_text.append(f"{weather['emoji']} {city.name} {temp_str}°C 💨 {wind_speed} м/с {time_emoji}")
            else:
                button_text = city.name
                cities_weather_text.append(city.name)

            markup.add(types.InlineKeyboardButton(
                text=button_text,
                callback_data=f"city_{city.name}"
            ))

        # Добавляем кнопку обновления
        if cities:
            markup.add(types.InlineKeyboardButton(text="🔄 Обновить", callback_data="refresh"))

        # Формируем текст сообщения
        if cities_weather_text:
            welcome_text = (
                "\n".join(cities_weather_text) +
                "\n\nОтправь мне название населенного пункта и я скажу какая там погода и температура, "
                "дам советы по одежде.\n\n"
                "💡 Отправляй прогнозы в любой чат: введи @MeteoblueBot + город в любом чате Телеграм"
            )
        else:
            welcome_text = (
                "Отправь мне название населенного пункта и я скажу какая там погода и температура, "
                "дам советы по одежде.\n\n"
                "💡 Отправляй прогнозы в любой чат: введи @MeteoblueBot + город в любом чате Телеграм"
            )

        # Отправляем или обновляем сообщение
        if message_id:
            try:
                bot.edit_message_text(
                    text=welcome_text,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=markup
                )
            except telebot.apihelper.ApiTelegramException:
                # Сообщение не найдено, отправляем новое
                sent_msg = bot.send_message(chat_id, welcome_text, reply_markup=markup)
                last_messages[chat_id] = {'message_id': sent_msg.message_id, 'timestamp': time.time()}
        else:
            sent_msg = bot.send_message(chat_id, welcome_text, reply_markup=markup)
            last_messages[chat_id] = {'message_id': sent_msg.message_id, 'timestamp': time.time()}

    except Exception as e:
        logger.error(f"Ошибка в send_welcome_message: {e}")


def auto_update_task():
    """Задача автоматического обновления (выполняется в отдельном потоке)"""
    logger.info("Запущена задача автоматического обновления")

    while True:
        try:
            db = get_db()

            # Отправляем обновления
            stats = notification_service.send_auto_updates(db)

            logger.info(f"Автообновление: отправлено {stats['messages_sent']} из {stats['total_attempts']}")

            db.close()

            # Ждем 1 минуту перед следующей проверкой
            time.sleep(60)

        except Exception as e:
            logger.error(f"Ошибка в auto_update_task: {e}")
            time.sleep(300)  # 5 минут при ошибке


# =======================
# ГЛАВНАЯ ФУНКЦИЯ
# =======================

def main():
    """Главная функция запуска бота"""
    logger.info("=" * 50)
    logger.info("Запуск GidMeteo бота v2.0")
    logger.info("=" * 50)

    try:
        # Инициализация базы данных
        logger.info("Инициализация базы данных...")
        init_db()

        # Автоматическая миграция данных при первом запуске
        try:
            db = get_db()
            user_count = db.query(User).count()

            if user_count == 0 and os.path.exists('all_users.json'):
                logger.info("База данных пустая. Запуск миграции данных...")
                from migrate_data import migrate_users, migrate_cities_and_user_cities

                migrate_users(db)
                migrate_cities_and_user_cities(db)

                new_user_count = db.query(User).count()
                logger.info(f"Миграция завершена! Восстановлено пользователей: {new_user_count}")
            elif user_count > 0:
                logger.info(f"В базе данных уже есть {user_count} пользователей")

            db.close()
        except Exception as e:
            logger.warning(f"Не удалось выполнить миграцию: {e}")

        # Запуск Flask keepalive в отдельном потоке
        logger.info(f"Запуск Flask сервера на порту {config.FLASK_PORT}...")
        flask_thread = Thread(target=run_flask, daemon=True)
        flask_thread.start()

        # Запуск задачи автообновления
        logger.info("Запуск задачи автоматического обновления...")
        auto_update_thread = threading.Thread(target=auto_update_task, daemon=True)
        auto_update_thread.start()

        # Запуск бота
        logger.info("Бот GidMeteo запущен. Нажмите Ctrl+C для остановки.")
        logger.info("Автоматические обновления с учетом часовых поясов пользователей")

        bot.infinity_polling(timeout=60, long_polling_timeout=60)

    except KeyboardInterrupt:
        logger.info("Получен сигнал остановки. Завершение работы...")
        close_db()
    except Exception as e:
        logger.critical(f"Критическая ошибка: {e}")
        raise
    finally:
        logger.info("Бот остановлен")


if __name__ == "__main__":
    main()
