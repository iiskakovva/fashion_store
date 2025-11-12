from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import UserPreferencesForm
import json
from datetime import datetime, timedelta

# Данные о товарах
CLOTHING_ITEMS = [
    {
        'id': 1,
        'name': 'Classic White T-Shirt',
        'description': 'Comfortable cotton t-shirt for everyday wear',
        'price': 29.99,
        'style': 'casual',
        'sizes': ['xs', 's', 'm', 'l', 'xl'],
        'image': '/static/images/tshirt.jpg'
    },
    {
        'id': 2,
        'name': 'Elegant Black Dress',
        'description': 'Perfect for formal occasions and evening events',
        'price': 89.99,
        'style': 'formal',
        'sizes': ['xs', 's', 'm', 'l'],
        'image': '/static/images/dress.jpg'
    },
    {
        'id': 3,
        'name': 'Sport Running Shorts',
        'description': 'Lightweight and breathable for sports activities',
        'price': 34.99,
        'style': 'sport',
        'sizes': ['s', 'm', 'l', 'xl'],
        'image': '/static/images/shorts.jpg'
    },
    {
        'id': 4,
        'name': 'Vintage Denim Jacket',
        'description': 'Retro-style jacket with authentic worn look',
        'price': 65.99,
        'style': 'vintage',
        'sizes': ['m', 'l', 'xl', 'xxl'],
        'image': '/static/images/jacket.jpg'
    },
    {
        'id': 5,
        'name': 'Bohemian Flowy Blouse',
        'description': 'Colorful and artistic blouse with unique patterns',
        'price': 45.99,
        'style': 'bohemian',
        'sizes': ['xs', 's', 'm', 'l'],
        'image': '/static/images/blouse.jpg'
    },
]

def get_user_preferences(request):
    """Получение пользовательских настроек из cookies"""
    preferences = {
        'favorite_styles': [],
        'preferred_sizes': [],
        'theme': 'light',
        'language': 'en',
        'recent_views': []
    }
    
    if 'user_preferences' in request.COOKIES:
        try:
            preferences = json.loads(request.COOKIES['user_preferences'])
        except:
            pass
    
    return preferences

def save_user_preferences(response, preferences):
    """Сохранение пользовательских настроек в cookies"""
    response.set_cookie(
        'user_preferences',
        json.dumps(preferences),
        expires=datetime.now() + timedelta(days=30),
        httponly=True
    )
    return response

def home(request):
    preferences = get_user_preferences(request)
    
    # Фильтрация товаров по предпочтениям
    filtered_items = CLOTHING_ITEMS
    if preferences['favorite_styles']:
        filtered_items = [item for item in CLOTHING_ITEMS if item['style'] in preferences['favorite_styles']]
    
    # Обновление истории просмотров
    recent_views = preferences.get('recent_views', [])
    if len(recent_views) >= 5:
        recent_views = recent_views[:4]
    
    context = {
        'clothing_items': filtered_items,
        'preferences': preferences,
        'recent_views': recent_views,
    }
    
    response = render(request, 'shop/home.html', context)
    
    # Сохраняем обновленные настройки
    preferences['recent_views'] = recent_views
    response = save_user_preferences(response, preferences)
    
    return response

def preferences(request):
    preferences = get_user_preferences(request)
    
    if request.method == 'POST':
        form = UserPreferencesForm(request.POST)
        if form.is_valid():
            # Обновляем настройки
            preferences['favorite_styles'] = form.cleaned_data['favorite_styles']
            preferences['preferred_sizes'] = form.cleaned_data['preferred_sizes']
            preferences['theme'] = form.cleaned_data['theme']
            preferences['language'] = form.cleaned_data['language']
            
            response = redirect('home')
            response = save_user_preferences(response, preferences)
            return response
    else:
        # Заполняем форму текущими настройками
        initial_data = {
            'favorite_styles': preferences['favorite_styles'],
            'preferred_sizes': preferences['preferred_sizes'],
            'theme': preferences['theme'],
            'language': preferences['language'],
        }
        form = UserPreferencesForm(initial=initial_data)
    
    context = {
        'form': form,
        'preferences': preferences,
    }
    
    response = render(request, 'shop/preferences.html', context)
    return response

def item_detail(request, item_id):
    preferences = get_user_preferences(request)
    
    item = next((item for item in CLOTHING_ITEMS if item['id'] == item_id), None)
    if not item:
        return redirect('home')
    
    # Добавляем в историю просмотров
    recent_views = preferences.get('recent_views', [])
    if item_id not in recent_views:
        recent_views.insert(0, item_id)
        if len(recent_views) > 5:
            recent_views = recent_views[:5]
    
    context = {
        'item': item,
        'preferences': preferences,
    }
    
    response = render(request, 'shop/item_detail.html', context)
    
    # Сохраняем обновленную историю
    preferences['recent_views'] = recent_views
    response = save_user_preferences(response, preferences)
    
    return response
    