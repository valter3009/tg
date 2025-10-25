"""
Модели базы данных для GidMeteo бота
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, ForeignKey, Text
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class User(Base):
    """Модель пользователя"""
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    telegram_id = Column(Integer, unique=True, nullable=False, index=True)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    timezone = Column(String(50), default='UTC', nullable=False)  # Часовой пояс пользователя
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    source = Column(String(50), nullable=True)  # 'start_command' или 'additional_list'

    # Связи
    cities = relationship('UserCity', back_populates='user', cascade='all, delete-orphan')
    activities = relationship('UserActivity', back_populates='user', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<User(telegram_id={self.telegram_id}, username={self.username})>"


class City(Base):
    """Модель города"""
    __tablename__ = 'cities'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), unique=True, nullable=False, index=True)
    name_lower = Column(String(255), unique=True, nullable=False, index=True)  # Для быстрого поиска
    timezone = Column(String(50), nullable=True)  # Часовой пояс города (Europe/Moscow, America/New_York, etc.)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Связи
    user_cities = relationship('UserCity', back_populates='city', cascade='all, delete-orphan')
    weather_cache = relationship('WeatherCache', back_populates='city', uselist=False)

    def __repr__(self):
        return f"<City(name={self.name})>"


class UserCity(Base):
    """Связь многие-ко-многим между пользователями и городами"""
    __tablename__ = 'user_cities'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='CASCADE'), nullable=False)
    order = Column(Integer, default=0, nullable=False)  # Порядок отображения
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Связи
    user = relationship('User', back_populates='cities')
    city = relationship('City', back_populates='user_cities')

    def __repr__(self):
        return f"<UserCity(user_id={self.user_id}, city_id={self.city_id})>"


class WeatherCache(Base):
    """Кэш погодных данных"""
    __tablename__ = 'weather_cache'

    id = Column(Integer, primary_key=True)
    city_id = Column(Integer, ForeignKey('cities.id', ondelete='CASCADE'), unique=True, nullable=False)
    temperature = Column(Float, nullable=False)
    description = Column(String(255), nullable=False)
    emoji = Column(String(10), nullable=False)
    wind_speed = Column(Float, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Связи
    city = relationship('City', back_populates='weather_cache')

    def __repr__(self):
        return f"<WeatherCache(city_id={self.city_id}, temp={self.temperature})>"


class UserActivity(Base):
    """Активность пользователя"""
    __tablename__ = 'user_activities'

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    activity_type = Column(String(50), nullable=False)  # 'start', 'refresh', 'city_click', 'auto_update'
    city_name = Column(String(255), nullable=True)  # Для city_click
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    # Связи
    user = relationship('User', back_populates='activities')

    def __repr__(self):
        return f"<UserActivity(user_id={self.user_id}, type={self.activity_type})>"


class AutoUpdateLog(Base):
    """Лог автоматических обновлений"""
    __tablename__ = 'auto_update_logs'

    id = Column(Integer, primary_key=True)
    total_attempts = Column(Integer, default=0, nullable=False)
    messages_sent = Column(Integer, default=0, nullable=False)
    users_with_cities = Column(Integer, default=0, nullable=False)
    users_without_cities = Column(Integer, default=0, nullable=False)
    blocked_users = Column(Integer, default=0, nullable=False)
    errors = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    def __repr__(self):
        return f"<AutoUpdateLog(sent={self.messages_sent}, errors={self.errors})>"
