"""
Сервис для работы с пользователями и их городами
"""
import logging
from typing import List, Dict, Optional

from ..database.db_service import DatabaseService
from ..config import Config

logger = logging.getLogger(__name__)


class UserService:
    """Сервис для управления пользователями"""

    def __init__(self, db_service: DatabaseService):
        self.db_service = db_service

    def register_user(self, user_id: int, source: str = 'start_command') -> bool:
        """
        Регистрирует нового пользователя

        Returns:
            True если пользователь новый, False если уже существовал
        """
        is_new = self.db_service.add_user(user_id, source)
        if is_new:
            logger.info(f"New user registered: {user_id} (source: {source})")
        else:
            logger.debug(f"Existing user reactivated: {user_id}")
        return is_new

    def add_additional_users(self) -> int:
        """
        Добавляет пользователей из списка ADDITIONAL_USERS

        Returns:
            Количество добавленных новых пользователей
        """
        added_count = 0
        for user_id in Config.ADDITIONAL_USERS:
            try:
                is_new = self.db_service.add_user(user_id, source='additional_list')
                if is_new:
                    added_count += 1
            except Exception as e:
                logger.error(f"Error adding additional user {user_id}: {e}")

        if added_count > 0:
            logger.info(f"Added {added_count} users from ADDITIONAL_USERS list")
        return added_count

    def deactivate_user(self, user_id: int):
        """Деактивирует пользователя (заблокировал бота)"""
        self.db_service.deactivate_user(user_id)
        logger.info(f"User {user_id} deactivated")

    def get_user_cities(self, user_id: int) -> List[str]:
        """Получает список городов пользователя"""
        return self.db_service.get_user_cities(user_id)

    def add_city(self, user_id: int, city_name: str) -> bool:
        """
        Добавляет город пользователю

        Returns:
            True если город добавлен, False если уже был
        """
        success = self.db_service.add_user_city(user_id, city_name)
        if success:
            logger.info(f"City '{city_name}' added for user {user_id}")
        return success

    def remove_city(self, user_id: int, city_name: str) -> bool:
        """
        Удаляет город у пользователя

        Returns:
            True если город удален, False если его не было
        """
        success = self.db_service.remove_user_city(user_id, city_name)
        if success:
            logger.info(f"City '{city_name}' removed for user {user_id}")
        return success

    def get_all_users(self) -> List[Dict]:
        """Получает всех пользователей"""
        return self.db_service.get_all_users()

    def get_active_users(self) -> List[int]:
        """Получает список ID активных пользователей"""
        return self.db_service.get_active_users()

    def get_user_stats(self) -> Dict:
        """Получает статистику по пользователям"""
        all_users = self.get_all_users()
        active_users = [u for u in all_users if u['active']]
        inactive_users = [u for u in all_users if not u['active']]

        users_with_cities = 0
        users_without_cities = 0

        for user in active_users:
            cities = self.get_user_cities(user['id'])
            if cities:
                users_with_cities += 1
            else:
                users_without_cities += 1

        # Подсчет по источникам
        from_start_command = len([u for u in all_users if u['source'] == 'start_command'])
        from_additional_list = len([u for u in all_users if u['source'] == 'additional_list'])

        return {
            'total_users': len(all_users),
            'active_users': len(active_users),
            'inactive_users': len(inactive_users),
            'users_with_cities': users_with_cities,
            'users_without_cities': users_without_cities,
            'from_start_command': from_start_command,
            'from_additional_list': from_additional_list,
            'activity_rate': (len(active_users) / len(all_users) * 100) if all_users else 0
        }
