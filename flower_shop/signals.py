from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.conf import settings
from .models import Order, OrderItem
from .telegram_bot import telegram_bot
import logging
import os
import time

logger = logging.getLogger(__name__)

# —————————————————————————————— Уведомления о новом заказе ——————————————————————————————
@receiver(post_save, sender=Order)
def send_order_notification(sender, instance, created, **kwargs):
    """
    Отправляет уведомление о новом заказе только если он был финализирован.
    """
    # Проверяем, что заказ финализирован и содержит товары
    if not instance.is_finalized or not instance.orderitem_set.exists():
        logger.info(f"Уведомление о заказе #{instance.pk} отклонено: заказ не готов.")
        return

    chat_id = settings.TELEGRAM_ADMIN_CHAT_ID
    order_items = instance.orderitem_set.all()

    caption = (
        f"🆕 *Новый заказ #{instance.pk}*\n"
        f"📅 Дата доставки: {instance.delivery_date.strftime('%d.%m.%Y')}\n"
        f"⏰ Время доставки: {instance.delivery_time.strftime('%H:%M')}\n"
        f"📍 Адрес: {instance.address}\n"
        f"{f'💬 Комментарий: {instance.comment}' if instance.comment else ''}\n"
        f"🛍 *Товары:*"
    )

    product_photos = []
    for item in order_items:
        product = item.product
        caption += f"\n- {product.name} ({item.quantity} шт.) — {product.price} руб."
        if product.image:
            image_path = f"{settings.MEDIA_ROOT}/{product.image}"
            product_photos.append(image_path)

    if product_photos:
        telegram_bot.send_photos(chat_id, product_photos, caption)
    else:
        telegram_bot.send_message(chat_id, caption)

    logger.info(f"Уведомление о заказе #{instance.pk} отправлено.")

# ————————————————————————— Уведомления при смене статуса заказа —————————————————————————
@receiver(pre_save, sender=Order)
def notify_order_status_change(sender, instance, **kwargs):
    if instance.pk:  # Проверяем, что заказ уже существует
        old_status = Order.objects.filter(pk=instance.pk).values_list("status", flat=True).first()
        if old_status and old_status != instance.status:
            print(f"✅ Отправляем уведомление о смене статуса заказа {instance.pk}")
            telegram_bot.send_message(settings.TELEGRAM_ADMIN_CHAT_ID, "Смена статуса заказа ⚠")
            message = (
                f"🔔 Статус заказа #{instance.pk} изменён!\n"
                f"📦 Новый статус: {dict(Order.STATUS_CHOICES).get(instance.status)}\n"
                f"📅 Дата изменения: {instance.order_date.strftime('%d.%m.%Y %H:%M')}"
            )
            telegram_bot.send_message(settings.TELEGRAM_ADMIN_CHAT_ID, message)



