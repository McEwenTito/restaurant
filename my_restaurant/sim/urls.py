from django.urls import path
from sim import views

app_name = 'sim'

urlpatterns = [
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('restaurants/new/', views.restaurant_create, name='restaurant_create'),
    path('restaurants/<int:pk>/edit/', views.restaurant_update, name='restaurant_edit'),
    path('restaurants/<int:pk>/delete/', views.restaurant_delete, name='restaurant_delete'),
]