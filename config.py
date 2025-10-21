import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла (для локальной разработки)
load_dotenv()

# Токены из переменных окружения
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "7519888794:AAG7b-VSCcAC-4DE6M-e8W1rd0WQawqpMjQ")
OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY", "79d1ca96933b0328e1c7e3e7a26cb347")
PROJECTEOL_TOKEN = os.getenv("PROJECTEOL_TOKEN", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ2MDQ1NzkyLCJpYXQiOjE3NDYwNDU0OTIsImp0aSI6ImMxZGE4OTZmNDI0ZjRlMzc4MmRjZTkzNmJlODY0MWEzIiwidXNlcl9pZCI6NzQxfQ.rKRdUln0IlqLVI9HGQ-XLJnA3XpCuBHsTJq5Wc0itHc")
