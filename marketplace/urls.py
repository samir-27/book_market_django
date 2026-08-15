from django.urls import path
from . import views

urlpatterns = [
    # The empty string '' means this is the root URL of the app
    path('', views.book_list, name='book_list'),
    path('book/<int:book_id>/', views.book_detail, name='book_detail'),
]