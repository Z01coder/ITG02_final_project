from django.contrib import admin
from .models import Product, Order, OrderItem

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'order_date', 'delivery_date', 'address')  # Отображаемые поля в списке
    list_filter = ('status', 'order_date')                                             # Фильтры для удобства
    search_fields = ('user__username', 'address')                                      # Поля для поиска
    list_editable = ('status',)                                      # Можно редактировать прямо в списке
    ordering = ('-order_date',)                                      # Сортировка по умолчанию (сначала новые заказы)
    date_hierarchy = 'order_date'                                    # Упрощённая навигация по датам

admin.site.register(Product)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)