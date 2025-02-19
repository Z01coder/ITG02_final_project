from django.apps import AppConfig
from django.conf import settings
import threading
import logging
import os

logger = logging.getLogger(__name__)

class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "flower_shop"

    def ready(self):
        import flower_shop.signals  # Импорт сигналов

        # Проверяем, является ли текущий процесс рабочим процессом
        if os.environ.get("RUN_MAIN", False):
            logger.info("Бот ещё не запущен. Запуск!")
            from .telegram_bot import start_bot
            threading.Thread(target=start_bot, daemon=True).start()
        else:
            logger.warning("Бот уже запущен или процесс не является рабочим. Пропуск.")
