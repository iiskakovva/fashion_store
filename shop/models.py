from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.urls import reverse

class TimeStampedModel(models.Model):
    """Абстрактная базовая модель с полями created_at и updated_at"""
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        abstract = True


class User(AbstractUser, TimeStampedModel):
    """Модель пользователя с дополнительными полями"""
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")
    address = models.TextField(blank=True, verbose_name="Адрес")
    avatar = models.ImageField(upload_to='avatars/', null=True, blank=True, verbose_name="Аватар")
    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username


class Category(TimeStampedModel):
    """Модель категории товаров"""
    name = models.CharField(max_length=100, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL")
    description = models.TextField(blank=True, verbose_name="Описание")
    image = models.ImageField(upload_to='categories/', null=True, blank=True, verbose_name="Изображение")
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    """Модель товара"""
    STYLE_CHOICES = [
        ('casual', 'Casual'),
        ('formal', 'Formal'),
        ('sport', 'Sport'),
        ('vintage', 'Vintage'),
        ('bohemian', 'Bohemian'),
    ]
    
    name = models.CharField(max_length=200, verbose_name="Название")
    slug = models.SlugField(unique=True, verbose_name="URL")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', verbose_name="Категория")
    description = models.TextField(verbose_name="Описание")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    style = models.CharField(max_length=20, choices=STYLE_CHOICES, verbose_name="Стиль")
    image = models.ImageField(upload_to='products/', null=True, blank=True, verbose_name="Изображение")
    stock = models.PositiveIntegerField(default=0, verbose_name="Количество на складе")
    available = models.BooleanField(default=True, verbose_name="Доступен")
    
    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['id', 'slug']),
            models.Index(fields=['name']),
            models.Index(fields=['style']),
        ]

    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        """Возвращает URL детальной страницы товара"""
        return reverse('product_detail', args=[self.slug])


class Size(TimeStampedModel):
    """Модель размера товара"""
    SIZE_CHOICES = [
        ('xs', 'XS'),
        ('s', 'S'),
        ('m', 'M'),
        ('l', 'L'),
        ('xl', 'XL'),
        ('xxl', 'XXL'),
    ]
    
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sizes', verbose_name="Товар")
    size = models.CharField(max_length=3, choices=SIZE_CHOICES, verbose_name="Размер")
    quantity = models.PositiveIntegerField(default=0, verbose_name="Количество")
    
    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"
        unique_together = ['product', 'size']

    def __str__(self):
        return f"{self.product.name} - {self.get_size_display()}"


class Cart(TimeStampedModel):
    """Модель корзины покупок"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Пользователь")
    session_id = models.CharField(max_length=255, null=True, blank=True, verbose_name="ID сессии")
    
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"Cart {self.id} - {self.user or 'Guest'}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(TimeStampedModel):
    """Модель элемента корзины"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items', verbose_name="Корзина")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, verbose_name="Размер")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    
    class Meta:
        verbose_name = "Элемент корзины"
        verbose_name_plural = "Элементы корзины"
        unique_together = ['cart', 'product', 'size']

    def __str__(self):
        return f"{self.quantity} x {self.product.name} ({self.size.get_size_display()})"

    @property
    def total_price(self):
        return self.product.price * self.quantity


class Order(TimeStampedModel):
    """Модель заказа"""
    STATUS_CHOICES = [
        ('pending', 'Ожидает обработки'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
        ('cancelled', 'Отменён'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders', verbose_name="Пользователь")
    first_name = models.CharField(max_length=100, verbose_name="Имя")
    last_name = models.CharField(max_length=100, verbose_name="Фамилия")
    email = models.EmailField(verbose_name="Email")
    phone = models.CharField(max_length=20, verbose_name="Телефон")
    address = models.TextField(verbose_name="Адрес доставки")
    city = models.CharField(max_length=100, verbose_name="Город")
    postal_code = models.CharField(max_length=20, verbose_name="Почтовый индекс")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="Статус")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Общая сумма")
    notes = models.TextField(blank=True, verbose_name="Примечания")
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.id} by {self.user.username}"


class OrderItem(TimeStampedModel):
    """Модель элемента заказа"""
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', verbose_name="Заказ")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="Товар")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, verbose_name="Размер")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    quantity = models.PositiveIntegerField(default=1, verbose_name="Количество")
    
    class Meta:
        verbose_name = "Элемент заказа"
        verbose_name_plural = "Элементы заказов"

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.price * self.quantity


class Review(TimeStampedModel):
    """Модель отзыва о товаре"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews', verbose_name="Товар")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reviews', verbose_name="Пользователь")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)], verbose_name="Оценка")
    comment = models.TextField(verbose_name="Комментарий")
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"
        unique_together = ['product', 'user']
        ordering = ['-created_at']

    def __str__(self):
        return f"Review by {self.user.username} on {self.product.name}"