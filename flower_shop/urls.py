"""
Конфигурация URL-адресов для проекта flower_shop.

Список `urlpatterns` сопоставляет URL-адреса с представлениями. Дополнительную информацию см. по адресу:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Примеры:
Функциональные представления
    1. Добавьте импорт:  from my_app import views
    2. Добавьте URL-адрес в urlpatterns:  path('', views.home, name='home')
Представления на основе классов
    1. Добавьте импорт: from other_app.views import Home
    2. Добавьте URL в urlpatterns: path('', Home.as_view(), name='home')
Включение другого URL-конф
    1. Импортируйте функцию include(): from django.urls import include, path
    2. Добавьте URL в urlpatterns: path('blog/', include('blog.urls'))
"""
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.conf import settings
from django.urls import path
from .views import repeat_order
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('catalog/', views.product_list, name='product_list'),
    path('catalog/<int:product_id>/', views.product_detail, name='product_detail'),
    path('cart/', views.view_cart, name='view_cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('create_order/', views.create_order, name='create_order'),
    path('order_history/', views.order_history, name='order_history'),
    path('profile/', views.profile, name='profile'),
    path('analytics/', views.analytics, name='analytics'),
    path('clear_cart/', views.clear_cart, name='clear_cart'),
    path('repeat_order/<int:order_id>/', repeat_order, name='repeat_order'),
]

if settings.DEBUG:  # Только для режима разработки
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)