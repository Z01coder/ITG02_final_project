from django.contrib.auth.models import AbstractUser
from django.db import models

    # ———————— МОДЕЛЬ КАСТОМНОГО ПОЛЬЗОВАТЕЛЯ —————————
class CustomUser(AbstractUser):
    phone = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)

    # ————————————————— МОДЕЛЬ ТОВАРА —————————————————
class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='media/products/', blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

    # ———————————————— МОДЕЛИ ЗАКАЗОВ —————————————————
class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('processing', 'В работе'),
        ('shipped', 'Отправлен'),
        ('completed', 'Выполнен'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    products = models.ManyToManyField(Product, through='OrderItem')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    order_date = models.DateTimeField(auto_now_add=True)
    delivery_date = models.DateField()
    delivery_time = models.TimeField()
    address = models.CharField(max_length=255)
    comment = models.TextField(blank=True, null=True)
    is_finalized = models.BooleanField(default=False)
    is_repeated = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} by {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.quantity} x {self.product.name} in Order #{self.order.id}"

    # ———————————————— МОДЕЛЬ ОТЗЫВОВ —————————————————
class Review(models.Model):
    RATING_CHOICES = [
        (1, '⭐'),
        (2, '⭐⭐'),
        (3, '⭐⭐⭐'),
        (4, '⭐⭐⭐⭐'),
        (5, '⭐⭐⭐⭐⭐'),
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=RATING_CHOICES)
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.user.username} for {self.product.name}"

    # ———————————————— МОДЕЛЬ ОТЧЁТОВ —————————————————
class Report(models.Model):
    date = models.DateField()
    total_orders = models.IntegerField()
    completed_orders = models.IntegerField()
    revenue = models.DecimalField(max_digits=10, decimal_places=2)
    expenses = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Report for {self.date}"