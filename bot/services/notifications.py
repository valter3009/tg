"""
Сервис для отправки уведомлений
"""
import logging
from typing import List, Dict
from sqlalchemy.orm import Session
import telebot
from bot.models import User, UserCity, City
from bot.services.weather import WeatherService
from bot.services.timezone import TimezoneService
from bot.services.analytics import AnalyticsService
from bot.config import config

logger = logging.getLogger(__name__)


class NotificationService:
    """Сервис для отправки уведомлений пользователям"""

    def __init__(self, bot: telebot.TeleBot):
        self.bot = bot

    def send_weather_update(self, db: Session, user: User) -> bool:
        """
        Отправляет обновление погоды пользователю

        Args:
            db: Сессия базы данных
            user: Объект пользователя

        Returns:
            True если успешно, False иначе
        """
        try:
            # Получаем города пользователя
            user_cities = db.query(UserCity).filter(
                UserCity.user_id == user.id
            ).order_by(UserCity.order).all()

            if not user_cities:
                # Отправляем напоминание добавить город
                return self.send_reminder(user)

            # Формируем сообщение с погодой
            weather_messages = []

            for user_city in user_cities:
                city = db.query(City).filter(City.id == user_city.city_id).first()
                if not city:
                    continue

                weather = WeatherService.get_weather(db, city.name)

                if weather:
                    temp_str = f"+{weather['temp']}" if weather['temp'] > 0 else f"{weather['temp']}"
                    weather_messages.append(
                        f"{weather['emoji']} {city.name}: {temp_str}°C, {weather['description']}, "
                        f"ветер {weather['wind_speed']} м/с"
                    )

            if not weather_messages:
                return False

            message = "🌤️ Обновление погоды:\n\n" + "\n".join(weather_messages)

            # Пытаемся отредактировать предыдущее сообщение, если оно есть
            if user.last_weather_message_id:
                try:
                    self.bot.edit_message_text(
                        chat_id=user.telegram_id,
                        message_id=user.last_weather_message_id,
                        text=message
                    )
                    logger.debug(f"Отредактировано сообщение {user.last_weather_message_id} для пользователя {user.telegram_id}")
                except telebot.apihelper.ApiTelegramException as e:
                    # Если сообщение было удалено или недоступно, отправляем новое
                    if "message to edit not found" in str(e).lower() or "message can't be edited" in str(e).lower():
                        logger.info(f"Предыдущее сообщение не найдено, отправляем новое для {user.telegram_id}")
                        sent_message = self.bot.send_message(user.telegram_id, message)
                        user.last_weather_message_id = sent_message.message_id
                        db.commit()
                    else:
                        raise
            else:
                # Отправляем новое сообщение и сохраняем его ID
                sent_message = self.bot.send_message(user.telegram_id, message)
                user.last_weather_message_id = sent_message.message_id
                db.commit()
                logger.debug(f"Отправлено новое сообщение {sent_message.message_id} для пользователя {user.telegram_id}")

            # Логируем активность
            AnalyticsService.log_activity(db, user.telegram_id, 'auto_update')

            return True

        except telebot.apihelper.ApiTelegramException as e:
            if "bot was blocked by the user" in str(e).lower():
                # Деактивируем пользователя
                user.is_active = False
                db.commit()
                logger.info(f"Пользователь {user.telegram_id} заблокировал бота. Деактивирован.")
            else:
                logger.error(f"Ошибка Telegram API при отправке обновления: {e}")
            return False

        except Exception as e:
            logger.error(f"Ошибка при отправке обновления пользователю {user.telegram_id}: {e}")
            return False

    def send_reminder(self, user: User) -> bool:
        """
        Отправляет напоминание пользователю без городов

        Args:
            user: Объект пользователя

        Returns:
            True если успешно, False иначе
        """
        reminder_text = (
            "🌤️ Привет! Пора узнать погоду на сегодня!\n\n"
            "Отправьте мне название города, чтобы получить актуальную информацию о погоде "
            "и рекомендации по одежде.\n\n"
            "Просто напишите название любого населенного пункта, и я расскажу:\n"
            "• Текущую температуру\n"
            "• Погодные условия\n"
            "• Что лучше надеть\n\n"
            "Попробуйте прямо сейчас! 😊"
        )

        try:
            self.bot.send_message(user.telegram_id, reminder_text)
            return True

        except telebot.apihelper.ApiTelegramException as e:
            if "bot was blocked by the user" in str(e).lower():
                return False
            logger.error(f"Ошибка при отправке напоминания: {e}")
            return False

        except Exception as e:
            logger.error(f"Ошибка при отправке напоминания: {e}")
            return False

    def send_auto_updates(self, db: Session) -> Dict:
        """
        Отправляет автоматические обновления всем активным пользователям с учетом их часовых поясов

        Args:
            db: Сессия базы данных

        Returns:
            Словарь со статистикой отправки
        """
        stats = {
            'total_attempts': 0,
            'messages_sent': 0,
            'users_with_cities': 0,
            'users_without_cities': 0,
            'blocked_users': 0,
            'errors': 0
        }

        try:
            # Получаем всех активных пользователей
            users = db.query(User).filter(User.is_active == True).all()
            stats['total_attempts'] = len(users)

            logger.info(f"Начало отправки автообновлений для {len(users)} пользователей")

            for user in users:
                try:
                    # Проверяем, нужно ли отправлять уведомление этому пользователю
                    should_send = TimezoneService.should_send_notification(
                        user.timezone,
                        config.AUTO_UPDATE_HOURS,
                        config.AUTO_UPDATE_MINUTE
                    )

                    if not should_send:
                        continue

                    # Проверяем, есть ли у пользователя города
                    user_cities_count = db.query(UserCity).filter(
                        UserCity.user_id == user.id
                    ).count()

                    if user_cities_count > 0:
                        stats['users_with_cities'] += 1
                    else:
                        stats['users_without_cities'] += 1

                    # Отправляем обновление
                    success = self.send_weather_update(db, user)

                    if success:
                        stats['messages_sent'] += 1
                    elif not user.is_active:
                        # Пользователь заблокировал бота
                        stats['blocked_users'] += 1
                    else:
                        stats['errors'] += 1

                except Exception as e:
                    logger.error(f"Ошибка при обработке пользователя {user.telegram_id}: {e}")
                    stats['errors'] += 1

            # Логируем статистику
            AnalyticsService.log_auto_update(
                db,
                stats['total_attempts'],
                stats['messages_sent'],
                stats['users_with_cities'],
                stats['users_without_cities'],
                stats['blocked_users'],
                stats['errors']
            )

            logger.info(
                f"Автообновление завершено. Отправлено: {stats['messages_sent']}/{stats['total_attempts']}, "
                f"ошибок: {stats['errors']}, заблокировано: {stats['blocked_users']}"
            )

        except Exception as e:
            logger.error(f"Критическая ошибка при отправке автообновлений: {e}")

        return stats
