import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

@pytest.mark.django_db
def test_registration(client):
    """Тест успешной регистрации пользователя"""
    response = client.post(reverse('register'), {
        'username': 'testuser',
        'email': 'test@example.com',
        'password1': 'Testpassword123',
        'password2': 'Testpassword123'
    })
    assert response.status_code == 302  # Проверяем редирект после регистрации
    assert User.objects.filter(username='testuser').exists()

@pytest.mark.django_db
def test_registration_invalid_data(client):
    """Тест неудачной регистрации (разные пароли)"""
    response = client.post(reverse('register'), {
        'username': 'testuser2',
        'email': 'test2@example.com',
        'password1': 'Testpassword123',
        'password2': 'WrongPassword456'
    })
    assert response.status_code == 200  # Форма должна вернуть страницу с ошибкой
    assert not User.objects.filter(username='testuser2').exists()

@pytest.mark.django_db
def test_login_success(client):
    """Тест успешного входа"""
    user = User.objects.create_user(username='testuser', email='test@example.com', password='Testpassword123')
    response = client.post(reverse('login'), {
        'username': 'testuser',
        'password': 'Testpassword123'
    })
    assert response.status_code == 302  # Проверяем редирект после входа

@pytest.mark.django_db
def test_login_failure(client):
    """Тест неудачного входа (неверный пароль)"""
    User.objects.create_user(username='testuser', email='test@example.com', password='Testpassword123')
    response = client.post(reverse('login'), {
        'username': 'testuser',
        'password': 'WrongPassword'
    })
    assert response.status_code == 200  # Остаемся на странице входа
    assert 'form' in response.context and response.context['form'].errors
