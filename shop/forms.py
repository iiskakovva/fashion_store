from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Review, Order

class UserRegistrationForm(UserCreationForm):
    """
    Форма регистрации пользователя
    """
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(max_length=20, required=False, label='Телефон')
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'phone', 'password1', 'password2', 'avatar']
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('Пользователь с таким email уже существует')
        return email


class UserLoginForm(forms.Form):
    """
    Форма входа пользователя
    """
    username = forms.CharField(max_length=150, label='Имя пользователя')
    password = forms.CharField(widget=forms.PasswordInput, label='Пароль')


class UserProfileForm(forms.ModelForm):
    """
    Форма редактирования профиля
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'avatar']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class ReviewForm(forms.ModelForm):
    """
    Форма отзыва о товаре
    """
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(choices=[(i, i) for i in range(1, 6)]),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Ваш отзыв...'}),
        }
        labels = {
            'rating': 'Оценка',
            'comment': 'Комментарий',
        }


class CheckoutForm(forms.ModelForm):
    """
    Форма оформления заказа
    """
    class Meta:
        model = Order
        fields = ['first_name', 'last_name', 'email', 'phone', 'address', 'city', 'postal_code', 'notes']
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Дополнительные пожелания...'}),
        }