# 🌤️ GidMeteo - Professional Telegram Weather Bot

Профессиональный Telegram бот для получения актуальной информации о погоде с персонализированными советами по одежде.

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![PostgreSQL](https://img.shields.io/badge/database-PostgreSQL-blue.svg)](https://www.postgresql.org/)

## ✨ Возможности

- 🌤️ **Актуальная погода** - данные из OpenWeatherMap API
- 👕 **Умные советы по одежде** - с учетом температуры, погоды, сезона и времени суток
- 💨 **Юмористические описания ветра** - от "мертвого штиля" до "апокалиптического разрушителя"
- 📍 **Избранные города** - сохраняйте часто используемые локации
- 🔄 **Автообновления** - получайте прогноз каждые 4 часа
- 🌐 **Inline режим** - отправляйте погоду в любой чат (@BotName город)
- 📊 **Подробная статистика** - команда `/stats` показывает аналитику использования
- ⚡ **Быстрый кеш** - мгновенные ответы благодаря PostgreSQL
- 🔐 **Безопасность** - все токены в переменных окружения
- 🏗️ **Профессиональная архитектура** - модульный, масштабируемый код

## 🆕 Что нового в версии 2.0?

### ✅ Решена главная проблема - /stats теперь работает всегда!
- **Было:** Excel файлы не синхронизировались с GitHub, данные терялись
- **Стало:** PostgreSQL база данных - статистика сохраняется навсегда

### 🚀 Другие улучшения:
- Переход с JSON/Excel на PostgreSQL
- Модульная архитектура вместо монолитного файла
- Убраны все хардкодированные токены (безопасность++)
- Type hints и улучшенное логирование
- Оптимизированные SQL запросы с индексами

## 📁 Структура проекта

```
tg/
├── app/                           # Основной код приложения
│   ├── config.py                 # Конфигурация (без токенов!)
│   ├── database/                 # Слой базы данных
│   │   ├── models.py            # SQLAlchemy модели
│   │   └── db_service.py        # Сервис для работы с БД
│   ├── services/                # Бизнес-логика
│   │   ├── user_service.py      # Управление пользователями
│   │   ├── weather_service.py   # Получение погоды
│   │   ├── activity_service.py  # Аналитика
│   │   └── clothes_advice.py    # Советы по одежде
│   ├── handlers/                # Обработчики Telegram
│   │   └── bot_handlers.py      # Команды и сообщения
│   └── utils/                   # Вспомогательные функции
│       ├── helpers.py           # Утилиты
│       └── message_builder.py   # Форматирование сообщений
├── main.py                       # Точка входа
├── requirements.txt              # Зависимости Python
├── .env.example                  # Пример переменных окружения
├── Procfile                      # Конфигурация Railway
└── RAILWAY_DEPLOY.md            # Инструкция по деплою
```

## 🚀 Быстрый старт

### Вариант 1: Деплой на Railway (рекомендуется)

**За 10 минут бот будет работать в облаке 24/7!**

См. подробную инструкцию: [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md)

Кратко:
1. Создайте PostgreSQL в Railway
2. Разверните бота из GitHub
3. Добавьте `TELEGRAM_TOKEN` и `OPENWEATHER_API_KEY`
4. Подключите базу данных к боту
5. Готово!

### Вариант 2: Локальный запуск

#### 1. Клонируйте репозиторий

```bash
git clone https://github.com/valter3009/tg.git
cd tg
```

#### 2. Создайте виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

#### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

#### 4. Настройте переменные окружения

Скопируйте `.env.example` в `.env`:

```bash
cp .env.example .env
```

Отредактируйте `.env` и добавьте свои токены:

```env
TELEGRAM_TOKEN=your_bot_token_here
OPENWEATHER_API_KEY=your_weather_api_key_here
# DATABASE_URL не обязательно - будет использоваться SQLite
```

**Где получить токены:**

- **TELEGRAM_TOKEN**:
  1. Напишите [@BotFather](https://t.me/BotFather) в Telegram
  2. Отправьте `/newbot` и следуйте инструкциям
  3. Скопируйте полученный токен

- **OPENWEATHER_API_KEY**:
  1. Зарегистрируйтесь на [OpenWeatherMap](https://openweathermap.org/api)
  2. Перейдите в "API keys"
  3. Скопируйте ключ (может занять до 2 часов на активацию)

#### 5. Запустите бота

```bash
python main.py
```

Готово! Бот работает и логи выводятся в консоль.

## 📝 Доступные команды

- `/start` - Главное меню с вашими городами
- `/stats` - Подробная статистика использования бота
- `/check_users` - Проверка статуса пользователей

**Inline режим:**
```
@YourBotName Москва
```

## 🗄️ База данных

### Таблицы PostgreSQL:

- **users** - Пользователи бота
- **user_cities** - Города пользователей
- **activity_logs** - Логи действий (refresh, клики, /start)
- **auto_update_logs** - История автоматических рассылок
- **weather_cache** - Кеш погодных данных
- **last_messages** - ID последних сообщений для редактирования

### Миграция со старой версии

Если у вас есть старые данные в JSON/Excel файлах, создан скрипт миграции:

```bash
python migrations/migrate_to_postgresql.py
```

Скрипт автоматически перенесет:
- Пользователей из `all_users.json`
- Города из `user_cities.json`
- Статистику из `bot_activity_log.xlsx`

## 🛠️ Разработка

### Установка зависимостей для разработки

```bash
pip install -r requirements.txt
```

### Запуск тестов

```bash
pytest
```

### Структура кода

- `app/database/` - Модели SQLAlchemy и сервис БД
- `app/services/` - Бизнес-логика (погода, пользователи, активность)
- `app/handlers/` - Обработчики команд и сообщений Telegram
- `app/utils/` - Вспомогательные функции
- `main.py` - Точка входа, инициализация, фоновые задачи

### Логирование

Логи сохраняются в `bot.log`. Уровень логирования настраивается в `.env`:

```env
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
```

## 🔧 Конфигурация

Все настройки через переменные окружения в `.env`:

```env
# Обязательные
TELEGRAM_TOKEN=...
OPENWEATHER_API_KEY=...

# Опциональные
DATABASE_URL=postgresql://...      # По умолчанию SQLite
WEATHER_CACHE_TTL=3600             # Время жизни кеша (сек)
CACHE_UPDATE_INTERVAL=600          # Интервал обновления (сек)
LOG_LEVEL=INFO                     # Уровень логирования
```

## 📊 Автоматические обновления

Бот автоматически отправляет прогноз погоды всем активным пользователям каждые 4 часа:

- 00:01
- 04:01
- 08:01
- 12:01
- 16:01
- 20:01

Пользователи **с городами** получают актуальную погоду.
Пользователи **без городов** получают напоминание добавить город.

## 🐛 Решение проблем

### Бот не отвечает
- Проверьте корректность `TELEGRAM_TOKEN`
- Убедитесь, что бот запущен (`python main.py`)
- Проверьте логи в `bot.log`

### Погода не работает
- Проверьте `OPENWEATHER_API_KEY`
- Убедитесь что ключ активирован (до 2 часов)
- Проверьте лимиты API на openweathermap.org

### /stats показывает пустые данные
- Это нормально для нового бота
- Данные начнут накапливаться после использования
- Проверьте подключение к PostgreSQL

### База данных не подключается
- Проверьте `DATABASE_URL` в `.env`
- Для Railway убедитесь что PostgreSQL запущен
- Для локальной разработки можно использовать SQLite (удалите `DATABASE_URL` из .env)

## 📈 Производительность

- **Кеширование**: Погода кешируется на 1 час (настраивается)
- **Индексы БД**: Оптимизированные запросы к PostgreSQL
- **Пул соединений**: SQLAlchemy управляет подключениями
- **Фоновые задачи**: Обновление кеша не блокирует бота

## 🔐 Безопасность

✅ Все токены в переменных окружения
✅ `.env` добавлен в `.gitignore`
✅ Нет хардкода секретов в коде
✅ SQL injection защита через ORM
✅ Валидация входных данных

## 📦 Деплой

### Railway.app (рекомендуется)
См. [RAILWAY_DEPLOY.md](RAILWAY_DEPLOY.md)

### Heroku
```bash
heroku create
heroku addons:create heroku-postgresql:mini
heroku config:set TELEGRAM_TOKEN=... OPENWEATHER_API_KEY=...
git push heroku main
```

### Docker (скоро)
```bash
docker-compose up -d
```

## 🤝 Вклад в проект

Приветствуются Pull Requests! Для больших изменений сначала откройте Issue.

## 📄 Лицензия

MIT License - см. [LICENSE](LICENSE)

## 📞 Поддержка

- 🐛 Проблемы: [GitHub Issues](https://github.com/valter3009/tg/issues)
- 💬 Обсуждения: [GitHub Discussions](https://github.com/valter3009/tg/discussions)

## 🙏 Благодарности

- [OpenWeatherMap](https://openweathermap.org/) за API погоды
- [pyTelegramBotAPI](https://github.com/eternnoir/pyTelegramBotAPI) за Telegram библиотеку
- [Railway.app](https://railway.app/) за отличный хостинг

---

**Сделано с ❤️ для русскоязычного сообщества**
