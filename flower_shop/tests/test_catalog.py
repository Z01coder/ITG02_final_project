import pytest
from django.urls import reverse
from flower_shop.models import Product


@pytest.mark.django_db
def test_product_list_view(client):
    """Тест отображения списка товаров"""
    Product.objects.create(name="Роза", price=100, image="rose.jpg")
    Product.objects.create(name="Тюльпан", price=50, image="tulip.jpg")

    response = client.get(reverse('product_list'))  # Замените на ваш URL, если он отличается
    assert response.status_code == 200
    assert "Роза" in response.content.decode()
    assert "Тюльпан" in response.content.decode()


@pytest.mark.django_db
def test_product_detail_view(client):
    """Тест страницы товара"""
    product = Product.objects.create(name="Лилия", price=150, description="Ароматный цветок", image="test.jpg")

    response = client.get(reverse('product_detail', args=[product.id]))
    assert response.status_code == 200
    assert "Лилия" in response.content.decode()
    assert "Ароматный цветок" in response.content.decode()


@pytest.mark.django_db
def test_add_to_cart(client):
    """Тест добавления товара в корзину"""
    product = Product.objects.create(name="Орхидея", price=200)

    response = client.get(reverse('add_to_cart', args=[product.id]))
    assert response.status_code == 302  # Проверяем, что происходит редирект

    session = client.session
    assert str(product.id) in session['cart']
    assert session['cart'][str(product.id)] == 1


@pytest.mark.django_db
def test_view_cart(client):
    """Тест просмотра корзины"""
    product = Product.objects.create(name="Гвоздика", price=75)

    session = client.session
    session['cart'] = {str(product.id): 2}
    session.save()

    response = client.get(reverse('view_cart'))
    assert response.status_code == 200
    assert "Гвоздика" in response.content.decode()
    assert "2" in response.content.decode()  # Проверяем, что отображается количество
