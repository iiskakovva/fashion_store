from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('preferences/', views.preferences, name='preferences'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
]