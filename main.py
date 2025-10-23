"""
Главная точка входа для GidMeteo бота
"""
import logging
import time
import threading
from datetime import datetime
import telebot

from app.config import Config
from app.database.db_service import DatabaseService
from app.handlers.bot_handlers import BotHandlers
from app.services.user_service import UserService
from app.services.weather_service import WeatherService
from app.services.activity_service import ActivityService
from app.utils.helpers import is_auto_update_time

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class GidMeteoBot:
    """Основной класс бота GidMeteo"""

    def __init__(self):
        logger.info("Initializing GidMeteo bot...")

        # Инициализация бота
        self.bot = telebot.TeleBot(Config.TELEGRAM_TOKEN)

        # Инициализация базы данных
        logger.info(f"Connecting to database...")
        self.db_service = DatabaseService(Config.DATABASE_URL)

        # Инициализация сервисов
        self.user_service = UserService(self.db_service)
        self.weather_service = WeatherService(self.db_service)
        self.activity_service = ActivityService(self.db_service)

        # Инициализация обработчиков
        self.handlers = BotHandlers(self.bot, self.db_service)

        logger.info("Bot initialized successfully")

    def add_additional_users(self):
        """Добавляет пользователей из списка ADDITIONAL_USERS"""
        logger.info("Adding users from ADDITIONAL_USERS list...")
        added_count = self.user_service.add_additional_users()
        logger.info(f"Added {added_count} new users from ADDITIONAL_USERS")
        return added_count

    def cleanup_old_messages(self):
        """Фоновая задача: очистка старых записей о сообщениях"""
        while True:
            try:
                logger.debug("Cleaning up old last messages...")
                deleted = self.db_service.cleanup_old_last_messages(days=7)
                if deleted > 0:
                    logger.info(f"Cleaned up {deleted} old message records")
                time.sleep(86400)  # Раз в сутки
            except Exception as e:
                logger.error(f"Error in cleanup_old_messages: {e}")
                time.sleep(3600)

    def update_weather_cache(self):
        """Фоновая задача: обновление кеша погоды"""
        while True:
            try:
                logger.info(f"Updating weather cache... {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                self.weather_service.update_all_cities_cache()
                logger.info(f"Weather cache updated! {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                time.sleep(Config.CACHE_UPDATE_INTERVAL)
            except Exception as e:
                logger.error(f"Error updating weather cache: {e}")
                time.sleep(60)

    def auto_update_users(self):
        """
        Фоновая задача: автоматические обновления для пользователей
        Отправляет обновления каждые 4 часа (00:01, 04:01, 08:01, 12:01, 16:01, 20:01)
        """
        while True:
            try:
                if is_auto_update_time():
                    logger.info("Starting auto-update for all users...")

                    # Обновляем кеш погоды перед рассылкой
                    self.weather_service.update_all_cities_cache()

                    # Получаем всех активных пользователей
                    active_users = self.user_service.get_active_users()

                    # Счетчики статистики
                    total_attempts = 0
                    sent_with_cities = 0
                    sent_without_cities = 0
                    blocked_count = 0
                    error_count = 0
                    total_sent = 0

                    for user_id in active_users:
                        total_attempts += 1

                        try:
                            user_cities = self.user_service.get_user_cities(user_id)

                            if user_cities:
                                # Пользователь с городами - отправляем погоду
                                last_msg = self.db_service.get_last_message(user_id)
                                msg_id = last_msg['message_id'] if last_msg else None
                                self.handlers.send_welcome_message(
                                    user_id,
                                    message_id=msg_id,
                                    force_new=True
                                )
                                sent_with_cities += 1
                                total_sent += 1
                            else:
                                # Пользователь без городов - отправляем напоминание
                                if self.handlers.send_reminder_message(user_id):
                                    sent_without_cities += 1
                                    total_sent += 1

                            time.sleep(0.1)  # Задержка между отправками

                        except telebot.apihelper.ApiTelegramException as e:
                            if "bot was blocked by the user" in str(e).lower():
                                self.user_service.deactivate_user(user_id)
                                blocked_count += 1
                                logger.info(f"User {user_id} blocked the bot")
                            else:
                                error_count += 1
                                logger.error(f"Error sending auto-update to {user_id}: {e}")
                        except Exception as e:
                            error_count += 1
                            logger.error(f"Error sending auto-update to {user_id}: {e}")

                    # Логируем статистику
                    if total_attempts > 0:
                        self.activity_service.log_auto_update(
                            total_attempts=total_attempts,
                            messages_sent=total_sent,
                            users_with_cities=sent_with_cities,
                            users_without_cities=sent_without_cities,
                            blocked_users=blocked_count,
                            errors=error_count
                        )

                        success_rate = (total_sent / total_attempts) * 100
                        logger.info(f"Auto-update completed:")
                        logger.info(f"  - Total attempts: {total_attempts}")
                        logger.info(f"  - Successfully sent: {total_sent} ({success_rate:.1f}%)")
                        logger.info(f"  - With cities: {sent_with_cities}")
                        logger.info(f"  - Without cities: {sent_without_cities}")
                        logger.info(f"  - Blocked: {blocked_count}")
                        logger.info(f"  - Errors: {error_count}")

                    # Ждем минуту, чтобы избежать повторного срабатывания
                    time.sleep(60)

                # Проверяем каждые 30 секунд
                time.sleep(30)

            except Exception as e:
                logger.error(f"Error in auto_update_users: {e}")
                time.sleep(300)

    def start_background_tasks(self):
        """Запускает фоновые задачи"""
        logger.info("Starting background tasks...")

        # Очистка старых сообщений
        cleanup_thread = threading.Thread(
            target=self.cleanup_old_messages,
            daemon=True,
            name="CleanupThread"
        )
        cleanup_thread.start()

        # Обновление кеша погоды
        cache_thread = threading.Thread(
            target=self.update_weather_cache,
            daemon=True,
            name="CacheUpdateThread"
        )
        cache_thread.start()

        # Автоматические обновления пользователей
        auto_update_thread = threading.Thread(
            target=self.auto_update_users,
            daemon=True,
            name="AutoUpdateThread"
        )
        auto_update_thread.start()

        logger.info("Background tasks started")

    def run(self):
        """Запускает бота"""
        logger.info("=" * 50)
        logger.info("GidMeteo Weather Bot Starting")
        logger.info("=" * 50)

        # Добавляем пользователей из списка
        added_users = self.add_additional_users()

        # Запускаем фоновые задачи
        self.start_background_tasks()

        logger.info(f"Added {added_users} users from ADDITIONAL_USERS")
        logger.info("Auto-updates will be sent every 4 hours (00:01, 04:01, 08:01, 12:01, 16:01, 20:01)")
        logger.info("Available commands:")
        logger.info("  /start - Main menu")
        logger.info("  /stats - Activity report")
        logger.info("  /check_users - User status check")
        logger.info("=" * 50)
        logger.info("Bot is running. Press Ctrl+C to stop.")
        logger.info("=" * 50)

        # Запускаем polling
        try:
            while True:
                try:
                    self.bot.polling(none_stop=True, interval=0, timeout=60)
                except Exception as e:
                    logger.error(f"Polling error: {e}")
                    time.sleep(10)
        except KeyboardInterrupt:
            logger.info("Received Ctrl+C signal. Shutting down...")
            logger.info("Bot stopped.")


def main():
    """Главная функция"""
    try:
        bot = GidMeteoBot()
        bot.run()
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == '__main__':
    main()
