import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from flower_shop.models import Product, Order, OrderItem
from datetime import date, time

User = get_user_model()


@pytest.mark.django_db
def test_admin_can_view_orders(admin_client):
    """Тест: администратор может просматривать список заказов"""
    user = User.objects.create_user(username="testuser", password="Testpassword123")
    order = Order.objects.create(
        user=user,
        delivery_date=date(2025, 2, 15),
        delivery_time=time(14, 0),
        status="pending",
        address="ул. Цветочная, 7"
    )

    response = admin_client.get(reverse("admin:flower_shop_order_changelist"))  # Админка заказов
    assert response.status_code == 200
    assert str(order.id) in response.content.decode()  # Проверяем, что заказ отображается


@pytest.mark.django_db
def test_admin_can_change_order_status(admin_client):
    """Тест: администратор может изменить статус заказа"""
    user = User.objects.create_user(username="testuser", password="Testpassword123")
    order = Order.objects.create(
        user=user,
        delivery_date=date(2025, 2, 15),
        delivery_time=time(14, 0),
        status="pending",
        address="ул. Цветочная, 7"
    )

    response = admin_client.post(
        reverse("admin:flower_shop_order_change", args=[order.id]),
        {
            "user": order.user.id,
            "delivery_date": order.delivery_date,
            "delivery_time": order.delivery_time,
            "status": "shipped",
            "address": order.address,
        }
    )

    order.refresh_from_db()
    assert response.status_code == 302  # Должен быть редирект
    assert order.status == "shipped"  # Проверяем, что статус изменился


@pytest.mark.django_db
def test_admin_can_delete_order(admin_client):
    """Тест: администратор может удалить заказ"""
    user = User.objects.create_user(username="testuser", password="Testpassword123")
    order = Order.objects.create(
        user=user,
        delivery_date=date(2025, 2, 15),
        delivery_time=time(14, 0),
        status="pending",
        address="ул. Цветочная, 7"
    )

    response = admin_client.post(
        reverse("admin:flower_shop_order_delete", args=[order.id]),
        {"post": "yes"}  # Подтверждение удаления
    )

    assert response.status_code == 302  # Должен быть редирект
    assert not Order.objects.filter(id=order.id).exists()  # Проверяем, что заказа больше нет
