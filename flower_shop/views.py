from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from .forms import CustomUserCreationForm, ProfileEditForm
from .forms import ReviewForm
from .models import Product, Review, Order, OrderItem, Report
from .forms import OrderForm
from datetime import date
import logging

logger = logging.getLogger(__name__)
def home(request):
    return render(request, 'home.html')

# ——————————————————————————————————————————— ПРЕДСТАВЛЕНИЕ ДЛЯ РЕГИСТРАЦИИ ———————————————————————————————————————————
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('home')
    else:
        form = CustomUserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

# —————————————————————————————————————————————— РЕДАКТИРОВАНИЕ ПРОФИЛЯ ———————————————————————————————————————————————
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('home')
    else:
        form = ProfileEditForm(instance=request.user)
    return render(request, 'registration/edit_profile.html', {'form': form})

# ———————————————————————————————————————————— ПРЕДСТАВЛЕНИЯ ДЛЯ КАТАЛОГА —————————————————————————————————————————————
def product_list(request):
    products = Product.objects.all()
    return render(request, 'catalog/product_list.html', {'products': products})

def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    reviews = Review.objects.filter(product=product)

    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.product = product
            review.save()
            return redirect('product_detail', product_id=product.id)
    else:
        form = ReviewForm()

    return render(request, 'catalog/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'form': form,
    })

# —————————————————————————————————————————————— ПРЕДСТАВЛЕНИЯ ДЛЯ КОРЗИНЫ ————————————————————————————————————————————
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = request.session.get('cart', {})
    cart[str(product_id)] = cart.get(str(product_id), 0) + 1
    request.session['cart'] = cart
    return redirect('product_list')

def view_cart(request):
    cart = request.session.get('cart', {})
    products = []
    total_price = 0
    for product_id, quantity in cart.items():
        product = Product.objects.get(id=product_id)
        products.append({
            'product': product,
            'quantity': quantity,
            'total': product.price * quantity
        })
        total_price += product.price * quantity
    return render(request, 'catalog/cart.html', {'products': products, 'total_price': total_price})

def clear_cart(request):
    # Удаляем корзину из сессии
    if 'cart' in request.session:
        del request.session['cart']
    return redirect('product_list')

# ———————————————————————————————————————— ПРЕДСТАВЛЕНИЕ ДЛЯ ОФОРМЛЕНИЯ ЗАКАЗА ————————————————————————————————————————
@login_required
def create_order(request):
    cart = request.session.get('cart', {})

    if not cart:
        messages.error(request, "Корзина пуста. Добавьте товары перед оформлением заказа.")
        return redirect('product_list')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()

            for product_id, quantity in cart.items():
                try:
                    product = Product.objects.get(id=product_id)
                    OrderItem.objects.create(order=order, product=product, quantity=quantity)
                except Product.DoesNotExist:
                    continue

            # Финализация заказа
            order.is_finalized = True
            order.save()

            request.session['cart'] = {}
            return redirect('order_history')
    else:
        form = OrderForm()

    return render(request, 'orders/create_order.html', {'form': form})


# ———————————————————————————————————————— ПРЕДСТАВЛЕНИЕ ИСТОРИИ ЗАКАЗОВ ——————————————————————————————————————————————
@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'orders/order_history.html', {'orders': orders})

# ——————————————————————————————————————— ПРЕДСТАВЛЕНИЕ ДЛЯ ПОВТОРА ЗАКАЗА ————————————————————————————————————————————
def repeat_order(request, order_id):
    old_order = get_object_or_404(Order, id=order_id, user=request.user)
    new_order = Order.objects.create(
        user=request.user,
        delivery_date=old_order.delivery_date,
        delivery_time=old_order.delivery_time,
        address=old_order.address,
        comment=old_order.comment,
        status='pending',
        is_finalized=False  # Заказ еще не финализирован
    )

    # Создаем OrderItem для каждого товара из старого заказа
    for item in old_order.orderitem_set.all():
        OrderItem.objects.create(
            order=new_order,
            product=item.product,
            quantity=item.quantity
        )

    # Финализируем новый заказ
    new_order.is_finalized = True
    new_order.save()

    messages.success(request, "Заказ успешно повторен!")
    return redirect('order_history')

# ———————————————————————————————————————————————— ЛИЧНЫЙ КАБИНЕТ —————————————————————————————————————————————————————
@login_required
def profile(request):
    return render(request, 'registration/profile.html')

# ———————————————————————————————————————— ПРЕДСТАВЛЕНИЯ ДЛЯ ОТЧЁТОВ / АНАЛИТИКИ ——————————————————————————————————————
@login_required
def analytics(request):
    if not request.user.is_superuser:
        return redirect('home')

    # Генерация данных для отчётов
    today = date.today()

    # Получение выполненных заказов
    total_orders = Order.objects.count()  # Всего заказов
    completed_orders = Order.objects.filter(status='completed').count()  # Выполненные заказы

    # Расчёт выручки
    revenue = Order.objects.filter(status='completed').aggregate(
        total_revenue=Sum('orderitem__product__price')
    )['total_revenue'] or 0

    # Расходы (фиксированные)
    expenses = 5000  # Пример: фиксированные расходы

    # Создание или обновление отчёта
    report, created = Report.objects.get_or_create(date=today, defaults={
        'total_orders': total_orders,
        'completed_orders': completed_orders,
        'revenue': revenue,
        'expenses': expenses,
    })

    # Передача всех отчётов в шаблон
    reports = Report.objects.all()
    return render(request, 'analytics/analytics.html', {'reports': reports})