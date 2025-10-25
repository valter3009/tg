"""
Утилиты для повторных попыток при ошибках
"""
import time
import logging
from functools import wraps
from typing import Callable, Any, Tuple, Type

logger = logging.getLogger(__name__)


def retry_on_exception(
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
) -> Callable:
    """
    Декоратор для повторных попыток выполнения функции при ошибках

    Args:
        max_retries: Максимальное количество попыток
        delay: Начальная задержка между попытками (в секундах)
        backoff: Множитель для увеличения задержки
        exceptions: Кортеж исключений, при которых нужно повторить попытку
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            current_delay = delay
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_retries:
                        logger.warning(
                            f"Попытка {attempt + 1}/{max_retries} провалилась для {func.__name__}: {e}. "
                            f"Повторная попытка через {current_delay:.1f}с..."
                        )
                        time.sleep(current_delay)
                        current_delay *= backoff
                    else:
                        logger.error(
                            f"Все {max_retries + 1} попыток провалились для {func.__name__}: {e}"
                        )

            raise last_exception

        return wrapper
    return decorator


def safe_execute(func: Callable, *args, default=None, log_errors: bool = True, **kwargs) -> Any:
    """
    Безопасное выполнение функции с возвратом значения по умолчанию при ошибке

    Args:
        func: Функция для выполнения
        *args: Позиционные аргументы функции
        default: Значение по умолчанию при ошибке
        log_errors: Логировать ли ошибки
        **kwargs: Именованные аргументы функции

    Returns:
        Результат функции или значение по умолчанию
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        if log_errors:
            logger.error(f"Ошибка при выполнении {func.__name__}: {e}")
        return default
