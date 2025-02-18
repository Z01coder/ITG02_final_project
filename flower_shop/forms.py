from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import CustomUser, Order, Review

# ——————————— ФОРМА СОЗДАНИЯ НОВОГО ПОЛЬЗОВАТЕЛЯ ———————————
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

# ———————— ФОРМА РЕДАКТИРОВАНИЯ ПРОФИЛЯ ПОЛЬЗОВАТЕЛЯ ————————
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'address')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

# ——————————————————————— ФОРМА ЗАКАЗА ———————————————————————
class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_date', 'delivery_time', 'address', 'comment']
        labels = {
            'delivery_date': 'Дата доставки:',
            'delivery_time': 'Время доставки:',
            'address': 'Адрес:',
            'comment': 'Комментарий:',
        }
        widgets = {
            'delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'delivery_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# ———————————————————————— ФОРМА ОТЗЫВА ————————————————————————
class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        labels = {
            'rating': 'Оценка:',
            'comment': 'Ваш отзыв:',
        }