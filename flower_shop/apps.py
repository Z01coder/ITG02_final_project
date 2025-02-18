from django.apps import AppConfig
from django.conf import settings
import threading
import logging

logger = logging.getLogger(__name__)

class OrdersConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "flower_shop"

    def ready(self):
        import flower_shop.signals # Импорт сигналов

        # Проверка запуска бота
        if not hasattr(settings, "BOT_STARTED"):
            logger.info("Бот ещё не запущен. Запуск!")
            settings.BOT_STARTED = True
            from .telegram_bot import start_bot
            threading.Thread(target=start_bot, daemon=True).start()
        else:
            logger.warning("Бот уже запущен. Пропуск.")
