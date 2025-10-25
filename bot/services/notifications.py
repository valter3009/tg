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
        Отправляет обновление погоды пользователю в виде стартового сообщения с кнопками

        Args:
            db: Сессия базы данных
            user: Объект пользователя

        Returns:
            True если успешно, False иначе
        """
        try:
            from telebot import types
            from bot.utils.helpers import get_user_cities, format_temperature

            # Получаем города пользователя
            cities = get_user_cities(db, user)

            if not cities:
                # Отправляем напоминание добавить город
                return self.send_reminder(user)

            # Создаем клавиатуру с городами
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
                    cities_weather_text.append(button_text)
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
            welcome_text = (
                "\n".join(cities_weather_text) +
                "\n\nОтправь мне название населенного пункта и я скажу какая там погода и температура, "
                "дам советы по одежде.\n\n"
                "💡 Отправляй прогнозы в любой чат: введи @MeteoblueBot + город в любом чате Телеграм"
            )

            # Отправляем сообщение с кнопками
            self.bot.send_message(user.telegram_id, welcome_text, reply_markup=markup)

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
