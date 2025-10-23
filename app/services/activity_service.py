"""
Сервис для отслеживания активности пользователей
"""
import logging
from typing import Dict, Optional
from datetime import datetime

from ..database.db_service import DatabaseService

logger = logging.getLogger(__name__)


class ActivityService:
    """Сервис для логирования и анализа активности"""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def log_start_command(self, user_id: int):
        """Логирует использование команды /start"""
        self.db_service.log_activity(user_id, 'start_command')
        logger.debug(f"Logged /start command for user {user_id}")

    def log_refresh(self, user_id: int):
        """Логирует нажатие кнопки 'Обновить'"""
        self.db_service.log_activity(user_id, 'refresh')
        logger.debug(f"Logged refresh for user {user_id}")

    def log_city_click(self, user_id: int, city_name: str):
        """Логирует нажатие на кнопку города"""
        self.db_service.log_activity(user_id, 'city_click', city_name)
        logger.debug(f"Logged city click '{city_name}' for user {user_id}")

    def log_auto_update(self, total_attempts: int, messages_sent: int,
                       users_with_cities: int, users_without_cities: int,
                       blocked_users: int, errors: int):
        """Логирует автоматическое обновление"""
        self.db_service.log_auto_update(
            total_attempts=total_attempts,
            messages_sent=messages_sent,
            users_with_cities=users_with_cities,
            users_without_cities=users_without_cities,
            blocked_users=blocked_users,
            errors=errors
        )
        logger.info(f"Auto update logged: {messages_sent}/{total_attempts} messages sent")

    def generate_activity_report(self) -> str:
        """Генерирует текстовый отчет об активности пользователей"""
        stats = self.db_service.get_activity_stats()
        auto_update_stats = self.db_service.get_auto_update_stats()
        recent_updates = self.db_service.get_recent_auto_updates(limit=5)

        # Получаем статистику пользователей
        from .user_service import UserService
        user_service = UserService(self.db_service)
        user_stats = user_service.get_user_stats()

        report = f"📊 Отчет о активности бота GidMeteo\n"
        report += f"🕐 Дата: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        # Статистика пользователей
        report += "👥 ПОЛЬЗОВАТЕЛИ:\n"
        report += f"• Всего зарегистрировано: {user_stats['total_users']}\n"
        report += f"• Активных: {user_stats['active_users']}\n"
        report += f"• Неактивных (заблокировали бота): {user_stats['inactive_users']}\n"
        report += f"• С добавленными городами: {user_stats['users_with_cities']}\n"
        report += f"• Без городов: {user_stats['users_without_cities']}\n"
        report += f"• Процент активности: {user_stats['activity_rate']:.1f}%\n\n"

        # Статистика действий
        report += "🎯 ДЕЙСТВИЯ ПОЛЬЗОВАТЕЛЕЙ:\n"
        report += f"• Всего нажатий 'Обновить': {stats['total_refresh']}\n"
        report += f"• Всего кликов по городам: {stats['total_city_clicks']}\n"
        report += f"• Всего использований /start: {stats['total_start']}\n\n"

        # Топ пользователей по обновлениям
        if stats['top_refresh_users']:
            report += "🔄 ТОП-5 ПО ОБНОВЛЕНИЯМ:\n"
            for i, user in enumerate(stats['top_refresh_users'], 1):
                report += f"{i}. Пользователь {user['user_id']}: {user['count']} раз\n"
            report += "\n"

        # Топ пользователей по /start
        if stats['top_start_users']:
            report += "🚀 ТОП-5 ПО ИСПОЛЬЗОВАНИЮ /START:\n"
            for i, user in enumerate(stats['top_start_users'], 1):
                report += f"{i}. Пользователь {user['user_id']}: {user['count']} раз\n"
            report += "\n"

        # Топ городов
        if stats['top_cities']:
            report += "🏙️ ТОП-5 ПОПУЛЯРНЫХ ГОРОДОВ:\n"
            for i, city in enumerate(stats['top_cities'], 1):
                report += f"{i}. {city['city']}: {city['count']} кликов\n"
            report += "\n"

        # Статистика автообновлений
        report += "🔁 АВТОМАТИЧЕСКИЕ ОБНОВЛЕНИЯ:\n"
        report += f"• Всего рассылок: {auto_update_stats['total_updates']}\n"
        report += f"• Всего отправлено сообщений: {auto_update_stats['total_sent']}\n"
        if auto_update_stats['last_update']:
            report += f"• Последнее обновление: {auto_update_stats['last_update'].strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += "\n"

        # Последние 5 автообновлений
        if recent_updates:
            report += "📅 ПОСЛЕДНИЕ 5 АВТООБНОВЛЕНИЙ:\n"
            for update in recent_updates:
                report += (
                    f"• {update['timestamp'].strftime('%Y-%m-%d %H:%M:%S')} - "
                    f"Попыток: {update['total_attempts']}, "
                    f"Отправлено: {update['messages_sent']}, "
                    f"С городами: {update['users_with_cities']}, "
                    f"Без городов: {update['users_without_cities']}, "
                    f"Заблокировано: {update['blocked_users']}, "
                    f"Ошибок: {update['errors']}\n"
                )

        return report

    def get_user_check_report(self) -> str:
        """Генерирует отчет о проверке пользователей"""
        from .user_service import UserService
        user_service = UserService(self.db_service)
        user_stats = user_service.get_user_stats()

        report = f"🔍 Проверка статуса пользователей\n"
        report += f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        report += "📊 ОБЩАЯ СТАТИСТИКА:\n"
        report += f"• Всего пользователей: {user_stats['total_users']}\n"
        report += f"• Активных: {user_stats['active_users']}\n"
        report += f"• Неактивных (заблокировали бота): {user_stats['inactive_users']}\n\n"

        report += "🏙️ ПО НАЛИЧИЮ ГОРОДОВ:\n"
        report += f"• С добавленными городами: {user_stats['users_with_cities']}\n"
        report += f"• Без городов: {user_stats['users_without_cities']}\n\n"

        report += "📝 ПО ИСТОЧНИКАМ:\n"
        report += f"• Из дополнительного списка: {user_stats['from_additional_list']}\n"
        report += f"• Через команду /start: {user_stats['from_start_command']}\n\n"

        report += f"✅ Процент активных пользователей: {user_stats['activity_rate']:.1f}%\n"

        return report
