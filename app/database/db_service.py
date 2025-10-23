"""
Сервис для работы с базой данных
Все операции с БД должны проходить через этот модуль
"""
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, desc
from contextlib import contextmanager
import logging

from .models import (
    User, UserCity, ActivityLog, AutoUpdateLog,
    WeatherCache, LastMessage, get_session_maker, init_database
)

logger = logging.getLogger(__name__)


class DatabaseService:
    """Сервис для работы с базой данных"""

    def __init__(self, database_url: str):
        """Инициализация сервиса БД"""
        self.engine = init_database(database_url)
        self.SessionMaker = get_session_maker(self.engine)
        logger.info("Database service initialized")

    @contextmanager
    def get_session(self):
        """Context manager для работы с сессией БД"""
        session = self.SessionMaker()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()

    # ============ USER OPERATIONS ============

    def add_user(self, user_id: int, source: str = 'start_command') -> bool:
        """Добавляет нового пользователя или обновляет существующего"""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()

            if user:
                # Обновляем существующего пользователя
                user.active = True
                user.last_interaction = datetime.utcnow()
                logger.info(f"User {user_id} reactivated")
                return False
            else:
                # Создаем нового пользователя
                new_user = User(
                    id=user_id,
                    source=source,
                    active=True,
                    first_start=datetime.utcnow(),
                    last_interaction=datetime.utcnow()
                )
                session.add(new_user)
                logger.info(f"New user {user_id} added with source '{source}'")
                return True

    def deactivate_user(self, user_id: int):
        """Деактивирует пользователя (заблокировал бота)"""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.active = False
                logger.info(f"User {user_id} deactivated")

    def get_user(self, user_id: int) -> Optional[User]:
        """Получает информацию о пользователе"""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                # Detach from session
                session.expunge(user)
            return user

    def get_all_users(self) -> List[Dict]:
        """Получает список всех пользователей"""
        with self.get_session() as session:
            users = session.query(User).all()
            return [
                {
                    'id': user.id,
                    'first_start': user.first_start,
                    'active': user.active,
                    'source': user.source,
                    'last_interaction': user.last_interaction
                }
                for user in users
            ]

    def get_active_users(self) -> List[int]:
        """Получает список ID всех активных пользователей"""
        with self.get_session() as session:
            user_ids = session.query(User.id).filter(User.active == True).all()
            return [user_id[0] for user_id in user_ids]

    def update_user_interaction(self, user_id: int):
        """Обновляет время последнего взаимодействия пользователя"""
        with self.get_session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                user.last_interaction = datetime.utcnow()

    # ============ USER CITY OPERATIONS ============

    def add_user_city(self, user_id: int, city_name: str) -> bool:
        """Добавляет город пользователю"""
        with self.get_session() as session:
            # Проверяем, существует ли уже такая запись
            existing = session.query(UserCity).filter(
                and_(UserCity.user_id == user_id, UserCity.city_name == city_name)
            ).first()

            if existing:
                return False

            # Добавляем новый город
            new_city = UserCity(user_id=user_id, city_name=city_name)
            session.add(new_city)
            logger.info(f"City '{city_name}' added for user {user_id}")
            return True

    def remove_user_city(self, user_id: int, city_name: str) -> bool:
        """Удаляет город у пользователя"""
        with self.get_session() as session:
            city = session.query(UserCity).filter(
                and_(UserCity.user_id == user_id, UserCity.city_name == city_name)
            ).first()

            if city:
                session.delete(city)
                logger.info(f"City '{city_name}' removed for user {user_id}")
                return True
            return False

    def get_user_cities(self, user_id: int) -> List[str]:
        """Получает список городов пользователя"""
        with self.get_session() as session:
            cities = session.query(UserCity.city_name).filter(
                UserCity.user_id == user_id
            ).order_by(UserCity.added_at).all()
            return [city[0] for city in cities]

    def get_all_cities(self) -> List[str]:
        """Получает список всех уникальных городов"""
        with self.get_session() as session:
            cities = session.query(UserCity.city_name).distinct().all()
            return [city[0] for city in cities]

    # ============ ACTIVITY LOG OPERATIONS ============

    def log_activity(self, user_id: int, action_type: str, city_name: Optional[str] = None):
        """Логирует активность пользователя"""
        with self.get_session() as session:
            activity = ActivityLog(
                user_id=user_id,
                action_type=action_type,
                city_name=city_name,
                timestamp=datetime.utcnow()
            )
            session.add(activity)
            # Также обновляем время последнего взаимодействия
            self.update_user_interaction(user_id)

    def get_activity_stats(self) -> Dict:
        """Получает статистику активности"""
        with self.get_session() as session:
            # Общее количество действий по типам
            total_refresh = session.query(func.count(ActivityLog.id)).filter(
                ActivityLog.action_type == 'refresh'
            ).scalar() or 0

            total_city_clicks = session.query(func.count(ActivityLog.id)).filter(
                ActivityLog.action_type == 'city_click'
            ).scalar() or 0

            total_start = session.query(func.count(ActivityLog.id)).filter(
                ActivityLog.action_type == 'start_command'
            ).scalar() or 0

            # Топ-5 пользователей по refresh
            top_refresh_users = session.query(
                ActivityLog.user_id,
                func.count(ActivityLog.id).label('count')
            ).filter(
                ActivityLog.action_type == 'refresh'
            ).group_by(ActivityLog.user_id).order_by(desc('count')).limit(5).all()

            # Топ-5 пользователей по start command
            top_start_users = session.query(
                ActivityLog.user_id,
                func.count(ActivityLog.id).label('count')
            ).filter(
                ActivityLog.action_type == 'start_command'
            ).group_by(ActivityLog.user_id).order_by(desc('count')).limit(5).all()

            # Топ-5 городов
            top_cities = session.query(
                ActivityLog.city_name,
                func.count(ActivityLog.id).label('count')
            ).filter(
                and_(
                    ActivityLog.action_type == 'city_click',
                    ActivityLog.city_name.isnot(None)
                )
            ).group_by(ActivityLog.city_name).order_by(desc('count')).limit(5).all()

            return {
                'total_refresh': total_refresh,
                'total_city_clicks': total_city_clicks,
                'total_start': total_start,
                'top_refresh_users': [{'user_id': u[0], 'count': u[1]} for u in top_refresh_users],
                'top_start_users': [{'user_id': u[0], 'count': u[1]} for u in top_start_users],
                'top_cities': [{'city': c[0], 'count': c[1]} for c in top_cities]
            }

    # ============ AUTO UPDATE LOG OPERATIONS ============

    def log_auto_update(self, total_attempts: int, messages_sent: int,
                       users_with_cities: int, users_without_cities: int,
                       blocked_users: int, errors: int):
        """Логирует автоматическое обновление"""
        with self.get_session() as session:
            log_entry = AutoUpdateLog(
                timestamp=datetime.utcnow(),
                total_attempts=total_attempts,
                messages_sent=messages_sent,
                users_with_cities=users_with_cities,
                users_without_cities=users_without_cities,
                blocked_users=blocked_users,
                errors=errors
            )
            session.add(log_entry)
            logger.info(f"Auto update logged: {messages_sent} messages sent")

    def get_recent_auto_updates(self, limit: int = 5) -> List[Dict]:
        """Получает последние автообновления"""
        with self.get_session() as session:
            updates = session.query(AutoUpdateLog).order_by(
                desc(AutoUpdateLog.timestamp)
            ).limit(limit).all()

            return [
                {
                    'timestamp': update.timestamp,
                    'total_attempts': update.total_attempts,
                    'messages_sent': update.messages_sent,
                    'users_with_cities': update.users_with_cities,
                    'users_without_cities': update.users_without_cities,
                    'blocked_users': update.blocked_users,
                    'errors': update.errors
                }
                for update in updates
            ]

    def get_auto_update_stats(self) -> Dict:
        """Получает общую статистику автообновлений"""
        with self.get_session() as session:
            total_updates = session.query(func.count(AutoUpdateLog.id)).scalar() or 0
            total_sent = session.query(func.sum(AutoUpdateLog.messages_sent)).scalar() or 0

            last_update = session.query(AutoUpdateLog).order_by(
                desc(AutoUpdateLog.timestamp)
            ).first()

            return {
                'total_updates': total_updates,
                'total_sent': total_sent,
                'last_update': last_update.timestamp if last_update else None
            }

    # ============ WEATHER CACHE OPERATIONS ============

    def update_weather_cache(self, city_name: str, temperature: float,
                           description: str, emoji: str, wind_speed: int):
        """Обновляет кеш погоды для города"""
        with self.get_session() as session:
            cache = session.query(WeatherCache).filter(
                WeatherCache.city_name == city_name
            ).first()

            if cache:
                # Обновляем существующую запись
                cache.temperature = temperature
                cache.description = description
                cache.emoji = emoji
                cache.wind_speed = wind_speed
                cache.updated_at = datetime.utcnow()
            else:
                # Создаем новую запись
                cache = WeatherCache(
                    city_name=city_name,
                    temperature=temperature,
                    description=description,
                    emoji=emoji,
                    wind_speed=wind_speed,
                    updated_at=datetime.utcnow()
                )
                session.add(cache)

    def get_weather_cache(self, city_name: str, max_age_seconds: int = 3600) -> Optional[Dict]:
        """Получает кешированную погоду для города"""
        with self.get_session() as session:
            cache = session.query(WeatherCache).filter(
                WeatherCache.city_name == city_name
            ).first()

            if not cache:
                return None

            # Проверяем возраст кеша
            age = (datetime.utcnow() - cache.updated_at).total_seconds()
            if age > max_age_seconds:
                return None

            return {
                'temp': cache.temperature,
                'description': cache.description,
                'emoji': cache.emoji,
                'wind_speed': cache.wind_speed,
                'updated_at': int(cache.updated_at.timestamp())
            }

    # ============ LAST MESSAGE OPERATIONS ============

    def save_last_message(self, user_id: int, message_id: int):
        """Сохраняет ID последнего сообщения пользователю"""
        with self.get_session() as session:
            last_msg = session.query(LastMessage).filter(
                LastMessage.user_id == user_id
            ).first()

            if last_msg:
                last_msg.message_id = message_id
                last_msg.timestamp = datetime.utcnow()
            else:
                last_msg = LastMessage(
                    user_id=user_id,
                    message_id=message_id,
                    timestamp=datetime.utcnow()
                )
                session.add(last_msg)

    def get_last_message(self, user_id: int) -> Optional[Dict]:
        """Получает ID последнего сообщения пользователю"""
        with self.get_session() as session:
            last_msg = session.query(LastMessage).filter(
                LastMessage.user_id == user_id
            ).first()

            if not last_msg:
                return None

            return {
                'message_id': last_msg.message_id,
                'timestamp': int(last_msg.timestamp.timestamp())
            }

    def delete_last_message(self, user_id: int):
        """Удаляет запись о последнем сообщении"""
        with self.get_session() as session:
            last_msg = session.query(LastMessage).filter(
                LastMessage.user_id == user_id
            ).first()
            if last_msg:
                session.delete(last_msg)

    # ============ CLEANUP OPERATIONS ============

    def cleanup_old_last_messages(self, days: int = 7):
        """Удаляет старые записи о последних сообщениях"""
        with self.get_session() as session:
            threshold = datetime.utcnow() - timedelta(days=days)
            deleted = session.query(LastMessage).filter(
                LastMessage.timestamp < threshold
            ).delete()
            logger.info(f"Cleaned up {deleted} old last messages")
            return deleted
