"""
Скрипт миграции данных из старого формата (JSON/Excel) в PostgreSQL

Использование:
    python migrations/migrate_to_postgresql.py

Мигрирует:
- Пользователей из all_users.json
- Города пользователей из user_cities.json
- Статистику из bot_activity_log.xlsx (если есть)
"""
import json
import os
import sys
from datetime import datetime

# Добавляем родительскую директорию в path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config import Config
from app.database.db_service import DatabaseService

# Опционально для миграции Excel
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    print("Warning: pandas not available, Excel migration will be skipped")


def migrate_users(db_service: DatabaseService, json_path: str):
    """Миграция пользователей из all_users.json"""
    if not os.path.exists(json_path):
        print(f"⚠️  File {json_path} not found, skipping users migration")
        return 0

    print(f"📋 Loading users from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        all_users = json.load(f)

    migrated = 0
    for user_id_str, user_info in all_users.items():
        try:
            user_id = int(user_id_str)
            source = user_info.get('source', 'additional_list')
            active = user_info.get('active', True)

            # Добавляем пользователя
            db_service.add_user(user_id, source=source)

            # Если неактивен, деактивируем
            if not active:
                db_service.deactivate_user(user_id)

            migrated += 1
        except Exception as e:
            print(f"⚠️  Error migrating user {user_id_str}: {e}")

    print(f"✅ Migrated {migrated} users")
    return migrated


def migrate_cities(db_service: DatabaseService, json_path: str):
    """Миграция городов из user_cities.json"""
    if not os.path.exists(json_path):
        print(f"⚠️  File {json_path} not found, skipping cities migration")
        return 0

    print(f"📋 Loading cities from {json_path}...")
    with open(json_path, 'r', encoding='utf-8') as f:
        user_cities = json.load(f)

    migrated = 0
    for user_id_str, cities in user_cities.items():
        try:
            user_id = int(user_id_str)
            for city in cities:
                db_service.add_user_city(user_id, city)
                migrated += 1
        except Exception as e:
            print(f"⚠️  Error migrating cities for user {user_id_str}: {e}")

    print(f"✅ Migrated {migrated} cities")
    return migrated


def migrate_activity_excel(db_service: DatabaseService, excel_path: str):
    """Миграция активности из bot_activity_log.xlsx"""
    if not PANDAS_AVAILABLE:
        print("⚠️  pandas not available, skipping Excel migration")
        return 0

    if not os.path.exists(excel_path):
        print(f"⚠️  File {excel_path} not found, skipping activity migration")
        return 0

    print(f"📋 Loading activity from {excel_path}...")

    migrated_actions = 0

    try:
        # Миграция кликов по кнопке "Обновить"
        try:
            df_refresh = pd.read_excel(excel_path, sheet_name='Refresh Button')
            for _, row in df_refresh.iterrows():
                user_id = int(row['User ID'])
                count = int(row['Count'])

                # Логируем count раз (приблизительно)
                for _ in range(count):
                    db_service.log_activity(user_id, 'refresh')
                migrated_actions += count

            print(f"  ✅ Migrated {len(df_refresh)} refresh users")
        except Exception as e:
            print(f"  ⚠️  Error migrating refresh data: {e}")

        # Миграция кликов по городам
        try:
            df_cities = pd.read_excel(excel_path, sheet_name='City Buttons')
            for _, row in df_cities.iterrows():
                user_id = int(row['User ID'])
                city = row['City']
                count = int(row['Count'])

                # Логируем count раз (приблизительно)
                for _ in range(count):
                    db_service.log_activity(user_id, 'city_click', city_name=city)
                migrated_actions += count

            print(f"  ✅ Migrated {len(df_cities)} city click records")
        except Exception as e:
            print(f"  ⚠️  Error migrating city data: {e}")

        # Миграция команды /start
        try:
            df_start = pd.read_excel(excel_path, sheet_name='Start Command')
            for _, row in df_start.iterrows():
                user_id = int(row['User ID'])
                count = int(row['Count'])

                # Логируем count раз (приблизительно)
                for _ in range(count):
                    db_service.log_activity(user_id, 'start_command')
                migrated_actions += count

            print(f"  ✅ Migrated {len(df_start)} start command records")
        except Exception as e:
            print(f"  ⚠️  Error migrating start data: {e}")

    except Exception as e:
        print(f"⚠️  Error reading Excel file: {e}")

    print(f"✅ Migrated {migrated_actions} activity records")
    return migrated_actions


def main():
    """Главная функция миграции"""
    print("=" * 60)
    print("🔄 GidMeteo Migration Script")
    print("=" * 60)
    print()

    # Проверяем конфигурацию
    try:
        print(f"📊 Database URL: {Config.DATABASE_URL[:50]}...")
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return

    # Инициализируем базу данных
    print("🔌 Connecting to database...")
    try:
        db_service = DatabaseService(Config.DATABASE_URL)
        print("✅ Connected to database")
    except Exception as e:
        print(f"❌ Error connecting to database: {e}")
        return

    print()
    print("Starting migration...")
    print()

    # Миграция пользователей
    users_migrated = migrate_users(db_service, 'all_users.json')
    print()

    # Миграция городов
    cities_migrated = migrate_cities(db_service, 'user_cities.json')
    print()

    # Миграция активности
    activity_migrated = migrate_activity_excel(db_service, 'bot_activity_log.xlsx')
    print()

    # Итоги
    print("=" * 60)
    print("✅ Migration completed!")
    print("=" * 60)
    print(f"📊 Summary:")
    print(f"  - Users:    {users_migrated}")
    print(f"  - Cities:   {cities_migrated}")
    print(f"  - Activity: {activity_migrated}")
    print()
    print("🎉 You can now run the bot with: python main.py")
    print()


if __name__ == '__main__':
    main()
