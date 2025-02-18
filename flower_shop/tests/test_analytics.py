import pytest
from django.urls import reverse
from django.contrib.auth import get_user_model
from flower_shop.models import Order, Report
from datetime import date

User = get_user_model()

@pytest.mark.django_db
def test_only_admin_can_access_analytics(client):
    """Тест: обычный пользователь не имеет доступа к аналитике"""
    user = User.objects.create_user(username="testuser", password="Testpassword123")
    client.login(username="testuser", password="Testpassword123")

    response = client.get(reverse("analytics"))  # URL аналитики
    assert response.status_code == 302  # Должен быть редирект на главную (не пускаем)

@pytest.mark.django_db
def test_admin_can_access_analytics(admin_client):
    """Тест: администратор может просматривать аналитику"""
    response = admin_client.get(reverse("analytics"))
    assert response.status_code == 200  # Админ должен получить доступ

@pytest.mark.django_db
def test_report_generation(admin_client):
    """Тест: проверка генерации отчёта"""
    today = date.today()
    Report.objects.create(
        date=today,
        total_orders=10,
        completed_orders=8,
        revenue=5000.00,
        expenses=2000.00
    )

    response = admin_client.get(reverse("analytics"))
    assert response.status_code == 200
    assert "5000,00 руб." in response.content.decode()  # Проверяем выручку
    assert "2000,00 руб." in response.content.decode()  # Проверяем расходы
    assert "10" in response.content.decode()  # Проверяем количество заказов
    assert "8" in response.content.decode()  # Проверяем выполненные заказы