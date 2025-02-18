import asyncio
from asgiref.sync import sync_to_async
from django.db.models import Sum
from django.utils.timezone import localtime, now
from telegram.ext import CommandHandler, CallbackContext, Application
from telegram import Update
from .models import Order
import requests
import logging
from django.conf import settings
import json

logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self, token):
        self.token = token
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.session = requests.Session()

    def send_message(self, chat_id, text):
        """ Отправка текстового сообщения в Telegram """
        url = f"{self.base_url}/sendMessage"
        data = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
        try:
            response = self.session.post(url, json=data, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка отправки сообщения в Telegram: {e}")

    def send_photos(self, chat_id, photo_paths, caption=""):
        """ Отправка альбома из нескольких фото в Telegram """
        if not photo_paths:
            self.send_message(chat_id, caption)
            return

        url = f"{self.base_url}/sendMediaGroup"
        media = []
        files = {}

        try:
            # Открываем файлы перед отправкой
            for i, photo_path in enumerate(photo_paths):
                file_key = f"photo{i}"
                files[file_key] = open(photo_path, "rb")  # Открываем файл перед отправкой
                media.append({
                    "type": "photo",
                    "media": f"attach://{file_key}",
                    "caption": caption if i == 0 else ""  # Подпись только к первому фото
                })

            # Логируем структуру запроса перед отправкой
            logger.info(f"Отправка фото в Telegram: {json.dumps(media, ensure_ascii=False)}")

            response = self.session.post(
                url,
                data={"chat_id": chat_id, "media": json.dumps(media)},  # <-- Передаём `media` как JSON-строку
                files=files,
                timeout=10
            )

            # Логируем ответ Telegram
            logger.info(f"Ответ Telegram: {response.status_code} - {response.text}")

            response.raise_for_status()

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка отправки фото в Telegram: {e}")
        finally:
            # Закрываем файлы после отправки
            for file in files.values():
                file.close()

# Создаём объект Telegram-бота
telegram_bot = TelegramBot(settings.TELEGRAM_BOT_TOKEN)

@sync_to_async
def get_daily_analytics():
    """ Получение аналитики по заказам за день """
    today = localtime(now()).date()
    orders_today = Order.objects.filter(order_date__date=today)

    total_orders = orders_today.count()
    total_income = orders_today.aggregate(total_income=Sum('orderitem__product__price'))['total_income'] or 0

    return total_orders, total_income

# Обработчик команды /analytics
async def analytics_command(update: Update, context: CallbackContext):
    if str(update.message.chat_id) != str(settings.TELEGRAM_ADMIN_CHAT_ID):
        await update.message.reply_text("У вас нет прав для просмотра аналитики.")
        return

    total_orders, total_income = await get_daily_analytics()

    message = (
        f"📊 *Аналитика за сегодня:*\n"
        f"🛒 Количество заказов: {total_orders}\n"
        f"💰 Общий доход: {total_income:.2f} руб."
    )

    await update.message.reply_text(message, parse_mode="Markdown")

# Настройка обработчиков команд
def add_handlers(application):
    application.add_handler(CommandHandler("analytics", analytics_command))

# Запуск Telegram-бота
application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()
add_handlers(application)

def start_bot():
    """ Запуск бота с обработкой событий """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(application.run_polling(drop_pending_updates=True, timeout=10))
