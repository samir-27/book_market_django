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


    # Transactions and History
    path('book/<int:book_id>/buy/', views.buy_book, name='buy_book'),
    path('orders/', views.order_history, name='order_history'),
    path('sales/', views.sales_history, name='sales_history'),

    path('cart/', views.view_cart, name='view_cart'),
    path('cart/add/<int:book_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/checkout/', views.checkout_cart, name='checkout_cart'),
]