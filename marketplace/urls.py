# marketplace/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.book_list, name='book_list'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
    path('sell/', views.sell_book, name='sell_book'),

    path('wishlist/', views.my_wishlist, name='my_wishlist'),
    path('book/<int:book_id>/wishlist/', views.toggle_wishlist, name='toggle_wishlist'),
    
    #Authentication URLs
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
]