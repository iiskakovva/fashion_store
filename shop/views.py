from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
from django.http import JsonResponse
from .models import Product, Category, Cart, CartItem, Order, OrderItem, Size, Review, User
from .forms import UserRegistrationForm, UserLoginForm, UserProfileForm, ReviewForm, CheckoutForm
import json

def home(request):
    """Главная страница с товарами"""
    products = Product.objects.filter(available=True)
    categories = Category.objects.all()
    
    # Поиск по названию
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) | 
            Q(description__icontains=query)
        )
    
    # Фильтр по категории (по slug, а не по id)
    category_slug = request.GET.get('category')
    if category_slug:
        products = products.filter(category__slug=category_slug)
    
    # Фильтр по стилю
    style = request.GET.get('style')
    if style:
        products = products.filter(style=style)
    
    # Фильтр по цене
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if min_price and min_price.strip():
        try:
            min_price = float(min_price)
            products = products.filter(price__gte=min_price)
        except ValueError:
            pass
    
    if max_price and max_price.strip():
        try:
            max_price = float(max_price)
            products = products.filter(price__lte=max_price)
        except ValueError:
            pass
    
    # Пагинация
    paginator = Paginator(products, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Получаем выбранные значения для отображения в фильтрах
    selected_category = category_slug if category_slug else ''
    selected_style = style if style else ''
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'styles': Product.STYLE_CHOICES,
        'selected_category': selected_category,
        'selected_style': selected_style,
        'search_query': query or '',
        'min_price': min_price if min_price else '',
        'max_price': max_price if max_price else '',
    }
    return render(request, 'shop/home.html', context)


def product_detail(request, slug):
    """Детальная страница товара"""
    product = get_object_or_404(Product, slug=slug, available=True)
    related_products = Product.objects.filter(
        category=product.category, 
        available=True
    ).exclude(id=product.id)[:4]
    
    # Получаем отзывы
    reviews = product.reviews.all().order_by('-created_at')
    avg_rating = reviews.aggregate(Avg('rating'))['rating__avg'] or 0
    
    # Обработка отзыва
    if request.method == 'POST' and request.user.is_authenticated and 'submit_review' in request.POST:
        rating = request.POST.get('rating')
        comment = request.POST.get('comment')
        if rating and comment:
            Review.objects.create(
                product=product,
                user=request.user,
                rating=int(rating),
                comment=comment
            )
            messages.success(request, 'Спасибо за ваш отзыв!')
            return redirect('product_detail', slug=product.slug)
    
    context = {
        'product': product,
        'related_products': related_products,
        'reviews': reviews,
        'avg_rating': avg_rating,
    }
    return render(request, 'shop/product_detail.html', context)


def register(request):
    """Регистрация пользователя"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'shop/register.html', {'form': form})


def user_login(request):
    """Вход пользователя"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'Добро пожаловать, {username}!')
                return redirect('home')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = UserLoginForm()
    return render(request, 'shop/login.html', {'form': form})


def user_logout(request):
    """Выход пользователя"""
    logout(request)
    messages.info(request, 'Вы вышли из системы')
    return redirect('home')


@login_required
def profile(request):
    """Профиль пользователя"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    orders = request.user.orders.all().order_by('-created_at')
    return render(request, 'shop/profile.html', {'form': form, 'orders': orders})


def add_to_cart(request, product_id):
    """Добавление товара в корзину"""
    product = get_object_or_404(Product, id=product_id, available=True)
    
    if request.method == 'POST':
        size_id = request.POST.get('size')
        quantity = int(request.POST.get('quantity', 1))
        
        if not size_id:
            messages.error(request, 'Пожалуйста, выберите размер')
            return redirect('product_detail', slug=product.slug)
        
        size = get_object_or_404(Size, id=size_id, product=product)
        
        # Проверяем наличие
        if size.quantity < quantity:
            messages.error(request, f'Извините, доступно только {size.quantity} единиц')
            return redirect('product_detail', slug=product.slug)
        
        # Получаем или создаем корзину
        if request.user.is_authenticated:
            cart, _ = Cart.objects.get_or_create(user=request.user)
        else:
            session_id = request.session.session_key
            if not session_id:
                request.session.create()
                session_id = request.session.session_key
            cart, _ = Cart.objects.get_or_create(session_id=session_id)
        
        # Добавляем товар
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            size=size,
            defaults={'quantity': quantity}
        )
        
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        
        messages.success(request, f'{product.name} добавлен в корзину')
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'cart_count': cart.items.count()
            })
        
        return redirect('cart_detail')
    
    return redirect('product_detail', slug=product.slug)


def cart_detail(request):
    """Детальная страница корзины"""
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
    else:
        session_id = request.session.session_key
        cart = Cart.objects.filter(session_id=session_id).first() if session_id else None
    
    return render(request, 'shop/cart.html', {'cart': cart})


def update_cart(request, item_id):
    """Обновление количества товара в корзине"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        
        if quantity <= 0:
            cart_item.delete()
            messages.success(request, 'Товар удален из корзины')
        else:
            if quantity > cart_item.size.quantity:
                messages.error(request, f'Доступно только {cart_item.size.quantity} единиц')
            else:
                cart_item.quantity = quantity
                cart_item.save()
                messages.success(request, 'Корзина обновлена')
    
    return redirect('cart_detail')


def remove_from_cart(request, item_id):
    """Удаление товара из корзины"""
    cart_item = get_object_or_404(CartItem, id=item_id)
    product_name = cart_item.product.name
    cart_item.delete()
    messages.success(request, f'{product_name} удален из корзины')
    return redirect('cart_detail')


@login_required
def checkout(request):
    """Оформление заказа"""
    cart = Cart.objects.filter(user=request.user).first()
    
    if not cart or not cart.items.exists():
        messages.warning(request, 'Ваша корзина пуста')
        return redirect('cart_detail')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Создаем заказ
            order = Order.objects.create(
                user=request.user,
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                email=form.cleaned_data['email'],
                phone=form.cleaned_data['phone'],
                address=form.cleaned_data['address'],
                city=form.cleaned_data['city'],
                postal_code=form.cleaned_data['postal_code'],
                total_price=cart.total_price,
                notes=form.cleaned_data['notes']
            )
            
            # Создаем элементы заказа
            for item in cart.items.all():
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    size=item.size,
                    price=item.product.price,
                    quantity=item.quantity
                )
                # Уменьшаем количество на складе
                item.size.quantity -= item.quantity
                item.size.save()
            
            # Очищаем корзину
            cart.items.all().delete()
            
            messages.success(request, f'Заказ №{order.id} успешно оформлен!')
            return redirect('order_detail', order_id=order.id)
    else:
        initial_data = {
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'email': request.user.email,
            'phone': request.user.phone,
            'address': request.user.address,
        }
        form = CheckoutForm(initial=initial_data)
    
    return render(request, 'shop/checkout.html', {'form': form, 'cart': cart})


@login_required
def order_detail(request, order_id):
    """Детальная страница заказа"""
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'shop/order_detail.html', {'order': order})


def search_products(request):
    """Поиск товаров (AJAX)"""
    query = request.GET.get('q', '')
    if query:
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query),
            available=True
        )[:10]
        
        results = [{
            'id': p.id,
            'name': p.name,
            'price': str(p.price),
            'image': p.image.url if p.image else '',
            'url': p.get_absolute_url(),
        } for p in products]
        
        return JsonResponse({'results': results})
    
    return JsonResponse({'results': []})


def preferences(request):
    """Настройки пользователя (cookies)"""
    preferences = {}
    if 'user_preferences' in request.COOKIES:
        try:
            preferences = json.loads(request.COOKIES['user_preferences'])
        except:
            preferences = {}
    
    if request.method == 'POST':
        preferences = {
            'theme': request.POST.get('theme', 'light'),
            'language': request.POST.get('language', 'ru'),
            'items_per_page': int(request.POST.get('items_per_page', 12)),
        }
        
        response = redirect('home')
        response.set_cookie(
            'user_preferences',
            json.dumps(preferences),
            max_age=30*24*60*60,
            httponly=True
        )
        messages.success(request, 'Настройки сохранены!')
        return response
    
    return render(request, 'shop/preferences.html', {'preferences': preferences})