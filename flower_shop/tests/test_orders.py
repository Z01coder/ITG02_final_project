import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from flower_shop.models import Product, Order, OrderItem

User = get_user_model()

@pytest.mark.django_db
def test_create_order(client):
    """Тест успешного оформления заказа"""
    user = User.objects.create_user(username="testuser", password="Testpassword123")
    client.login(username="testuser", password="Testpassword123")

    product = Product.objects.create(name="Ромашка", price=50)

    session = client.session
    session['cart'] = {str(product.id): 2}  # Добавляем товар в корзину
    session.save()

    response = client.post(reverse('create_order'), {
        'delivery_date': '2025-02-15',
        'delivery_time': '14:00',
        'address': 'ул. Цветочная, 7',
        'comment': 'Быстрая доставка, пожалуйста!',
    })

    assert response.status_code == 302  # Редирект после оформления
    assert Order.objects.filter(user=user).exists()  # Проверяем, что заказ создался

    order = Order.objects.first()
    assert order.orderitem_set.count() == 1  # Проверяем, что товары добавлены
    assert order.address == "ул. Цветочная, 7"
    assert order.comment == "Быстрая доставка, пожалуйста!"

@pytest.mark.django_db
def test_create_order_empty_cart(client):
    """Тест попытки оформления заказа с пустой корзиной"""
    user = User.objects.create_user(username="testuser", password="Testpassword123")
    client.login(username="testuser", password="Testpassword123")

    response = client.post(reverse('create_order'), {
        'delivery_date': '2025-02-15',
        'delivery_time': '14:00',
        'address': 'ул. Цветочная, 7',
        'comment': 'Без комментариев',
    })

    assert response.status_code == 302  # Должен быть редирект (например, на каталог)
    assert not Order.objects.filter(user=user).exists()  # Заказ не должен создаться

from datetime import date, time

@pytest.mark.django_db
def test_order_history(client):
    """Тест просмотра истории заказов"""
    user = User.objects.create_user(username="testuser", password="Testpassword123")
    client.login(username="testuser", password="Testpassword123")

    order = Order.objects.create(
        user=user,
        order_date="2025-02-10",
        delivery_date=date(2025, 2, 15),
        delivery_time=time(14, 0),
        status="pending",
        address="ул. Цветочная, 7"
    )
    OrderItem.objects.create(order=order, product=Product.objects.create(name="Пион", price=80), quantity=1)

    response = client.get(reverse('order_history'))
    assert response.status_code == 200

    assert str(order.id) in response.content.decode()  # Проверяем ID заказа
    assert "Ожидает подтверждения" in response.content.decode()  # Проверяем статус заказа


