from django.contrib import admin
from .models import Book, Wishlist, SellerRating
# Register your models here.


# marketplace/admin.py

from django.contrib import admin
from .models import Book, Wishlist, SellerRating

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # This defines which columns are shown in the list view
    list_display = ('title', 'author', 'seller', 'price', 'condition', 'is_sold')
    # Adds a filter sidebar
    list_filter = ('condition', 'is_sold', 'created_at')
    # Adds a search bar that looks up these specific fields
    search_fields = ('title', 'author', 'isbn')

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'book', 'added_at')
    search_fields = ('user__username', 'book__title')

@admin.register(SellerRating)
class SellerRatingAdmin(admin.ModelAdmin):
    list_display = ('seller', 'buyer', 'rating', 'created_at')
    list_filter = ('rating',)
    search_fields = ('seller__username', 'buyer__username')