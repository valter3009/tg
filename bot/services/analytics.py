"""
Сервис для аналитики и статистики
"""
import logging
from datetime import datetime
from typing import Dict, List
from sqlalchemy.orm import Session
from sqlalchemy import func
from bot.models import User, UserActivity, UserCity, AutoUpdateLog

logger = logging.getLogger(__name__)


class AnalyticsService:
    """Сервис для сбора и анализа статистики"""

    @staticmethod
    def log_activity(db: Session, user_id: int, activity_type: str, city_name: str = None) -> bool:
        """
        Логирует активность пользователя

        Args:
            db: Сессия базы данных
            user_id: ID пользователя в Telegram
            activity_type: Тип активности ('start', 'refresh', 'city_click', 'auto_update')
            city_name: Название города (опционально)

        Returns:
            True если успешно, False иначе
        """
        try:
            user = db.query(User).filter(User.telegram_id == user_id).first()
            if not user:
                logger.warning(f"Пользователь {user_id} не найден для логирования активности")
                return False

            activity = UserActivity(
                user_id=user.id,
                activity_type=activity_type,
                city_name=city_name
            )
            db.add(activity)
            db.commit()

            logger.debug(f"Активность '{activity_type}' логирована для пользователя {user_id}")
            return True

        except Exception as e:
            logger.error(f"Ошибка при логировании активности: {e}")
            db.rollback()
            return False

    @staticmethod
    def get_user_stats(db: Session) -> Dict:
        """
        Получает статистику по пользователям

        Returns:
            Словарь со статистикой
        """
        try:
            total_users = db.query(User).count()
            active_users = db.query(User).filter(User.is_active == True).count()
            inactive_users = total_users - active_users

            # Статистика по источникам
            source_stats = db.query(
                User.source,
                func.count(User.id)
            ).group_by(User.source).all()

            # Пользователи с городами - используем outer join чтобы не падать на пустой таблице
            try:
                users_with_cities = db.query(User.id).join(UserCity).distinct().count()
            except Exception as join_error:
                logger.warning(f"Ошибка при подсчете пользователей с городами: {join_error}")
                users_with_cities = 0

            users_without_cities = total_users - users_with_cities

            return {
                'total_users': total_users,
                'active_users': active_users,
                'inactive_users': inactive_users,
                'users_with_cities': users_with_cities,
                'users_without_cities': users_without_cities,
                'sources': dict(source_stats) if source_stats else {}
            }

        except Exception as e:
            logger.error(f"Ошибка при получении статистики пользователей: {e}", exc_info=True)
            return {
                'total_users': 0,
                'active_users': 0,
                'inactive_users': 0,
                'users_with_cities': 0,
                'users_without_cities': 0,
                'sources': {}
            }

    @staticmethod
    def get_activity_stats(db: Session, days: int = 7) -> Dict:
        """
        Получает статистику активности за последние дни

        Args:
            days: Количество дней для анализа

        Returns:
            Словарь со статистикой
        """
        try:
            from datetime import timedelta

            start_date = datetime.utcnow() - timedelta(days=days)

            # Статистика по типам активности
            activity_stats = db.query(
                UserActivity.activity_type,
                func.count(UserActivity.id)
            ).filter(
                UserActivity.created_at >= start_date
            ).group_by(UserActivity.activity_type).all()

            # Самые активные пользователи
            top_users = db.query(
                User.telegram_id,
                User.username,
                func.count(UserActivity.id).label('activity_count')
            ).join(UserActivity).filter(
                UserActivity.created_at >= start_date
            ).group_by(User.telegram_id, User.username).order_by(
                func.count(UserActivity.id).desc()
            ).limit(10).all()

            # Самые популярные города
            top_cities = db.query(
                UserActivity.city_name,
                func.count(UserActivity.id).label('click_count')
            ).filter(
                UserActivity.activity_type == 'city_click',
                UserActivity.created_at >= start_date,
                UserActivity.city_name.isnot(None)
            ).group_by(UserActivity.city_name).order_by(
                func.count(UserActivity.id).desc()
            ).limit(10).all()

            return {
                'period_days': days,
                'activity_by_type': dict(activity_stats),
                'top_users': [
                    {
                        'telegram_id': u[0],
                        'username': u[1],
                        'activity_count': u[2]
                    } for u in top_users
                ],
                'top_cities': [
                    {
                        'city': c[0],
                        'clicks': c[1]
                    } for c in top_cities
                ]
            }

        except Exception as e:
            logger.error(f"Ошибка при получении статистики активности: {e}")
            return {}

    @staticmethod
    def log_auto_update(
        db: Session,
        total_attempts: int,
        messages_sent: int,
        users_with_cities: int,
        users_without_cities: int,
        blocked_users: int,
        errors: int
    ) -> bool:
        """
        Логирует автоматическое обновление

        Returns:
            True если успешно, False иначе
        """
        try:
            log = AutoUpdateLog(
                total_attempts=total_attempts,
                messages_sent=messages_sent,
                users_with_cities=users_with_cities,
                users_without_cities=users_without_cities,
                blocked_users=blocked_users,
                errors=errors
            )
            db.add(log)
            db.commit()

            logger.info(
                f"Автообновление: попыток={total_attempts}, отправлено={messages_sent}, "
                f"ошибок={errors}, заблокировано={blocked_users}"
            )
            return True

        except Exception as e:
            logger.error(f"Ошибка при логировании автообновления: {e}")
            db.rollback()
            return False

    @staticmethod
    def get_auto_update_stats(db: Session, limit: int = 10) -> List[Dict]:
        """
        Получает статистику автообновлений

        Args:
            limit: Количество последних записей

        Returns:
            Список словарей со статистикой
        """
        try:
            logs = db.query(AutoUpdateLog).order_by(
                AutoUpdateLog.created_at.desc()
            ).limit(limit).all()

            return [
                {
                    'date': log.created_at,
                    'total_attempts': log.total_attempts,
                    'messages_sent': log.messages_sent,
                    'users_with_cities': log.users_with_cities,
                    'users_without_cities': log.users_without_cities,
                    'blocked_users': log.blocked_users,
                    'errors': log.errors
                } for log in logs
            ]

        except Exception as e:
            logger.error(f"Ошибка при получении статистики автообновлений: {e}")
            return []
