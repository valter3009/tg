"""
Модели базы данных для GidMeteo бота
"""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    Column, Integer, String, Boolean, Float, DateTime,
    ForeignKey, Text, create_engine, Index
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()


class User(Base):
    """Модель пользователя бота"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)  # Telegram user ID
    first_start = Column(DateTime, default=datetime.utcnow, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    source = Column(String(50), nullable=False)  # 'start_command' или 'additional_list'
    last_interaction = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    cities = relationship('UserCity', back_populates='user', cascade='all, delete-orphan')
    activities = relationship('ActivityLog', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User(id={self.id}, active={self.active}, source='{self.source}')>"


class UserCity(Base):
    """Модель города пользователя"""
    __tablename__ = 'user_cities'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    city_name = Column(String(100), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship('User', back_populates='cities')

    # Indexes
    __table_args__ = (
        Index('idx_user_city', 'user_id', 'city_name', unique=True),
    )

    def __repr__(self):
        return f"<UserCity(user_id={self.user_id}, city='{self.city_name}')>"


class ActivityLog(Base):
    """Модель логов активности пользователей"""
    __tablename__ = 'activity_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    action_type = Column(String(50), nullable=False)  # 'refresh', 'city_click', 'start_command'
    city_name = Column(String(100), nullable=True)  # Для action_type='city_click'
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    user = relationship('User', back_populates='activities')

    # Indexes
    __table_args__ = (
        Index('idx_activity_user_action', 'user_id', 'action_type'),
        Index('idx_activity_timestamp', 'timestamp'),
    )

    def __repr__(self):
        return f"<ActivityLog(user_id={self.user_id}, action='{self.action_type}', time={self.timestamp})>"


class AutoUpdateLog(Base):
    """Модель логов автоматических обновлений"""
    __tablename__ = 'auto_update_logs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    total_attempts = Column(Integer, default=0, nullable=False)
    messages_sent = Column(Integer, default=0, nullable=False)
    users_with_cities = Column(Integer, default=0, nullable=False)
    users_without_cities = Column(Integer, default=0, nullable=False)
    blocked_users = Column(Integer, default=0, nullable=False)
    errors = Column(Integer, default=0, nullable=False)

    # Indexes
    __table_args__ = (
        Index('idx_auto_update_timestamp', 'timestamp'),
    )

    def __repr__(self):
        return f"<AutoUpdateLog(time={self.timestamp}, sent={self.messages_sent})>"


class WeatherCache(Base):
    """Модель кеша погоды"""
    __tablename__ = 'weather_cache'

    id = Column(Integer, primary_key=True, autoincrement=True)
    city_name = Column(String(100), unique=True, nullable=False)
    temperature = Column(Float, nullable=False)
    description = Column(String(200), nullable=False)
    emoji = Column(String(10), nullable=False)
    wind_speed = Column(Integer, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Indexes
    __table_args__ = (
        Index('idx_weather_city', 'city_name'),
        Index('idx_weather_updated', 'updated_at'),
    )

    def __repr__(self):
        return f"<WeatherCache(city='{self.city_name}', temp={self.temperature}°C)>"


class LastMessage(Base):
    """Модель последних сообщений для каждого пользователя"""
    __tablename__ = 'last_messages'

    user_id = Column(Integer, primary_key=True)  # Telegram user ID
    message_id = Column(Integer, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<LastMessage(user_id={self.user_id}, message_id={self.message_id})>"


# Функции для создания и управления базой данных
def get_engine(database_url: str):
    """Создает engine для подключения к базе данных"""
    return create_engine(database_url, echo=False, pool_pre_ping=True)


def get_session_maker(engine):
    """Создает SessionMaker для работы с базой данных"""
    return sessionmaker(bind=engine)


def init_database(database_url: str):
    """Инициализирует базу данных, создает все таблицы"""
    engine = get_engine(database_url)
    Base.metadata.create_all(engine)
    return engine
