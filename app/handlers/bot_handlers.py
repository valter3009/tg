"""
Обработчики команд и сообщений бота
"""
import logging
import time
import telebot
from telebot import types

from ..database.db_service import DatabaseService
from ..services.user_service import UserService
from ..services.weather_service import WeatherService
from ..services.activity_service import ActivityService
from ..utils.message_builder import MessageBuilder
from ..utils.helpers import get_season, get_time_of_day

logger = logging.getLogger(__name__)


class BotHandlers:
    """Класс с обработчиками команд и сообщений бота"""

    def __init__(self, bot: telebot.TeleBot, db_service: DatabaseService):
        self.bot = bot
        self.db_service = db_service
        self.user_service = UserService(db_service)
        self.weather_service = WeatherService(db_service)
        self.activity_service = ActivityService(db_service)
        self.message_builder = MessageBuilder()

        # Регистрируем обработчики
        self._register_handlers()

    def _register_handlers(self):
        """Регистрирует все обработчики бота"""
        self.bot.message_handler(commands=['start'])(self.start_command)
        self.bot.message_handler(commands=['stats'])(self.stats_command)
        self.bot.message_handler(commands=['check_users'])(self.check_users_command)
        self.bot.callback_query_handler(func=lambda call: True)(self.callback_handler)
        self.bot.message_handler(func=lambda message: True)(self.handle_all_messages)
        self.bot.inline_handler(func=lambda query: True)(self.handle_inline_query)

    # ============ ВСПОМОГАТЕЛЬНЫЕ МЕТОДЫ ============

    def send_new_message(self, chat_id: int, text: str, markup=None) -> telebot.types.Message:
        """Отправляет новое сообщение"""
        try:
            sent_msg = self.bot.send_message(
                chat_id,
                text,
                reply_markup=markup,
                parse_mode='Markdown'
            )
            self.db_service.save_last_message(chat_id, sent_msg.message_id)
            return sent_msg
        except Exception as e:
            logger.error(f"Error sending message to {chat_id}: {e}")
            return None

    def update_message(self, chat_id: int, message_id: int, text: str, markup=None) -> telebot.types.Message:
        """Обновляет существующее сообщение или отправляет новое"""
        try:
            if message_id:
                try:
                    return self.bot.edit_message_text(
                        text=text,
                        chat_id=chat_id,
                        message_id=message_id,
                        reply_markup=markup,
                        parse_mode='Markdown'
                    )
                except telebot.apihelper.ApiTelegramException as e:
                    if "message to edit not found" in str(e).lower():
                        logger.info(f"Message {message_id} not found, sending new")
                        self.db_service.delete_last_message(chat_id)
                        return self.send_new_message(chat_id, text, markup)
                    raise
            return self.send_new_message(chat_id, text, markup)

        except Exception as e:
            logger.error(f"Error updating message: {e}")
            return self.send_new_message(chat_id, text, markup)

    def delete_message_safe(self, chat_id: int, message_id: int):
        """Безопасно удаляет сообщение"""
        try:
            self.bot.delete_message(chat_id, message_id)
        except Exception as e:
            logger.warning(f"Failed to delete message: {e}")

    def send_welcome_message(self, chat_id: int, message_id=None, force_new=False):
        """Отправляет приветственное сообщение с городами"""
        user_cities = self.user_service.get_user_cities(chat_id)

        # Получаем погоду для всех городов
        cities_weather = {}
        for city in user_cities:
            weather = self.weather_service.get_weather(city)
            if weather:
                cities_weather[city] = weather

        # Создаем сообщение и клавиатуру
        text = self.message_builder.build_welcome_message(user_cities, cities_weather)
        markup = self.message_builder.create_cities_keyboard(user_cities, cities_weather)

        if force_new:
            # Удаляем старое сообщение и отправляем новое
            if message_id:
                self.delete_message_safe(chat_id, message_id)
            sent = self.send_new_message(chat_id, text, markup)
        else:
            # Обновляем существующее сообщение
            last_msg = self.db_service.get_last_message(chat_id)
            msg_id = message_id if message_id else (last_msg['message_id'] if last_msg else None)
            sent = self.update_message(chat_id, msg_id, text, markup)

        if sent:
            self.db_service.save_last_message(chat_id, sent.message_id)

    def send_weather_info(self, chat_id: int, city: str, message_id=None, force_new=False):
        """Отправляет информацию о погоде для города"""
        weather_data = self.weather_service.get_weather(city)

        if not weather_data:
            error_text = 'Город не найден. Проверьте написание.'
            if force_new and message_id:
                self.delete_message_safe(chat_id, message_id)
                sent = self.send_new_message(chat_id, error_text)
            else:
                last_msg = self.db_service.get_last_message(chat_id)
                msg_id = message_id if message_id else (last_msg['message_id'] if last_msg else None)
                sent = self.update_message(chat_id, msg_id, error_text)

            if sent:
                self.db_service.save_last_message(chat_id, sent.message_id)
            return False

        # Создаем сообщение и клавиатуру
        text = self.message_builder.build_weather_message(city, weather_data)
        user_cities = self.user_service.get_user_cities(chat_id)
        is_saved = city in user_cities
        markup = self.message_builder.create_weather_keyboard(city, is_saved)

        if force_new:
            if message_id:
                self.delete_message_safe(chat_id, message_id)
            sent = self.send_new_message(chat_id, text, markup)
        else:
            last_msg = self.db_service.get_last_message(chat_id)
            msg_id = message_id if message_id else (last_msg['message_id'] if last_msg else None)
            sent = self.update_message(chat_id, msg_id, text, markup)

        if sent:
            self.db_service.save_last_message(chat_id, sent.message_id)
        return True

    def send_reminder_message(self, chat_id: int) -> bool:
        """Отправляет напоминание пользователю без городов"""
        try:
            text = self.message_builder.build_reminder_message()
            sent = self.bot.send_message(chat_id, text)
            if sent:
                self.db_service.save_last_message(chat_id, sent.message_id)
            return True
        except telebot.apihelper.ApiTelegramException as e:
            if "bot was blocked by the user" in str(e).lower():
                self.user_service.deactivate_user(chat_id)
                logger.info(f"User {chat_id} blocked the bot")
                return False
        except Exception as e:
            logger.error(f"Error sending reminder to {chat_id}: {e}")
            return False

    # ============ ОБРАБОТЧИКИ КОМАНД ============

    def start_command(self, message: types.Message):
        """Обработчик команды /start"""
        try:
            chat_id = message.chat.id

            # Регистрируем пользователя
            self.user_service.register_user(chat_id, source='start_command')

            # Логируем активность
            self.activity_service.log_start_command(chat_id)

            # Удаляем запись о последнем сообщении
            self.db_service.delete_last_message(chat_id)

            # Отправляем приветственное сообщение
            self.send_welcome_message(chat_id)

        except Exception as e:
            logger.error(f"Error in /start handler: {e}")
            self.bot.send_message(
                message.chat.id,
                "Давайте начнем заново! Вот меню:"
            )
            self.send_welcome_message(message.chat.id)

    def stats_command(self, message: types.Message):
        """Обработчик команды /stats"""
        try:
            # Проверка прав (любой может посмотреть статистику своего использования)
            report = self.activity_service.generate_activity_report()
            self.bot.send_message(message.chat.id, report)
        except Exception as e:
            logger.error(f"Error in /stats handler: {e}")
            self.bot.send_message(
                message.chat.id,
                "Произошла ошибка при генерации отчета."
            )

    def check_users_command(self, message: types.Message):
        """Обработчик команды /check_users"""
        try:
            report = self.activity_service.get_user_check_report()
            self.bot.send_message(message.chat.id, report)
        except Exception as e:
            logger.error(f"Error in /check_users handler: {e}")
            self.bot.send_message(
                message.chat.id,
                "Произошла ошибка при проверке пользователей."
            )

    # ============ ОБРАБОТЧИК CALLBACK-ОВ ============

    def callback_handler(self, call: types.CallbackQuery):
        """Обработчик нажатий на inline кнопки"""
        try:
            chat_id = call.message.chat.id
            message_id = call.message.message_id

            if call.data == "back":
                self.send_welcome_message(chat_id, message_id)

            elif call.data == "refresh":
                # Логируем обновление
                self.activity_service.log_refresh(chat_id)

                # Обновляем погоду для всех городов пользователя
                user_cities = self.user_service.get_user_cities(chat_id)
                for city in user_cities:
                    self.weather_service.get_weather_from_api(city)
                    time.sleep(0.5)  # Задержка между запросами

                # Отправляем обновленное сообщение
                self.send_welcome_message(chat_id, message_id, force_new=True)

            elif call.data.startswith("add_"):
                city = call.data[4:]
                self.user_service.add_city(chat_id, city)
                self.send_welcome_message(chat_id, message_id)

            elif call.data.startswith("remove_"):
                city = call.data[7:]
                self.user_service.remove_city(chat_id, city)
                self.send_welcome_message(chat_id, message_id)

            elif call.data.startswith("city_"):
                city = call.data[5:]
                # Логируем клик по городу
                self.activity_service.log_city_click(chat_id, city)
                self.send_weather_info(chat_id, city, message_id, force_new=False)

            self.bot.answer_callback_query(call.id)

        except Exception as e:
            logger.error(f"Error in callback handler: {e}")
            try:
                self.bot.answer_callback_query(call.id)
            except:
                pass

    # ============ ОБРАБОТЧИК СООБЩЕНИЙ ============

    def handle_all_messages(self, message: types.Message):
        """Обработчик всех текстовых сообщений"""
        try:
            if message.text.startswith('/'):
                self.bot.send_message(
                    message.chat.id,
                    "Неизвестная команда. Попробуйте /start"
                )
            else:
                # Пользователь отправил название города
                city = message.text.strip()
                last_msg = self.db_service.get_last_message(message.chat.id)
                msg_id = last_msg['message_id'] if last_msg else None
                self.send_weather_info(message.chat.id, city, msg_id, force_new=False)

            # Удаляем сообщение пользователя
            self.delete_message_safe(message.chat.id, message.message_id)

        except Exception as e:
            logger.error(f"Error handling message: {e}")
            self.bot.send_message(
                message.chat.id,
                "Произошла ошибка. Попробуйте позже."
            )

    # ============ ОБРАБОТЧИК INLINE РЕЖИМА ============

    def handle_inline_query(self, query: types.InlineQuery):
        """Обработчик inline запросов"""
        try:
            city = query.query.strip()

            if not city:
                # Предлагаем варианты по умолчанию
                results = self._get_default_inline_results()
                self.bot.answer_inline_query(query.id, results)
                return

            # Получаем погоду для запрошенного города
            weather_data = self.weather_service.get_weather(city)

            if not weather_data:
                self.bot.answer_inline_query(query.id, [])
                return

            # Создаем сообщение
            message_text = self.message_builder.build_weather_message(city, weather_data)

            # Форматируем описание для результата
            temp_str = f"+{weather_data['temp']}" if weather_data['temp'] > 0 else str(weather_data['temp'])

            result = types.InlineQueryResultArticle(
                id="1",
                title=f"Погода в {city}",
                description=f"{temp_str}°C, {weather_data['description']}",
                input_message_content=types.InputTextMessageContent(
                    message_text=message_text
                )
            )

            self.bot.answer_inline_query(query.id, [result])

        except Exception as e:
            logger.error(f"Inline query error: {e}")
            self.bot.answer_inline_query(query.id, [])

    def _get_default_inline_results(self) -> list:
        """Возвращает результаты inline по умолчанию (Москва и СПб)"""
        results = []

        for city in ["Москва", "Санкт-Петербург"]:
            weather_data = self.weather_service.get_weather(city)
            if weather_data:
                message_text = self.message_builder.build_weather_message(city, weather_data)
                temp_str = f"+{weather_data['temp']}" if weather_data['temp'] > 0 else str(weather_data['temp'])

                results.append(types.InlineQueryResultArticle(
                    id=str(len(results) + 1),
                    title=city,
                    description=f"{temp_str}°C, {weather_data['description']}",
                    input_message_content=types.InputTextMessageContent(
                        message_text=message_text
                    )
                ))

        return results
