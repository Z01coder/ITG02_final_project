import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from flower_shop.models import Product, Review

User = get_user_model()

@pytest.mark.django_db
def test_authenticated_user_can_leave_review(client):
    """Тест: авторизованный пользователь может оставить отзыв"""
    user = User.objects.create_user(username="testuser", password="Testpassword123")
    client.login(username="testuser", password="Testpassword123")

    product = Product.objects.create(name="Роза", price=100)

    response = client.post(reverse('product_detail', args=[product.id]), {
        'rating': 5,
        'comment': 'Прекрасные цветы!'
    })

    assert response.status_code == 302  # Должен быть редирект
    assert Review.objects.filter(user=user, product=product).exists()  # Отзыв должен сохраниться

@pytest.mark.django_db
def test_unauthenticated_user_cannot_leave_review(client):
    """Тест: неавторизованный пользователь видит ссылку на вход вместо формы отзыва"""
    product = Product.objects.create(name="Лилия", price=150, image="test.jpg")

    response = client.get(reverse('product_detail', args=[product.id]))

    assert response.status_code == 200
    assert '<a href="' + reverse('login') + '">войдите</a>' in response.content.decode()

@pytest.mark.django_db
def test_reviews_displayed_on_product_page(client):
    """Тест: отзывы отображаются на странице товара"""
    user = User.objects.create_user(username="testuser", password="Testpassword123")
    product = Product.objects.create(name="Гвоздика", price=75, image="test.jpg")

    Review.objects.create(user=user, product=product, rating=3, comment="Обычные цветы.")

    response = client.get(reverse('product_detail', args=[product.id]))
    assert response.status_code == 200
    assert "Обычные цветы." in response.content.decode()  # Проверяем, что отзыв отображается
