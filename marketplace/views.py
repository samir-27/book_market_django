from django.shortcuts import render
from .models import Book

def book_list(request):
    # Fetch all books that are NOT sold, ordered by newest first
    books = Book.objects.filter(is_sold=False).order_by('-created_at')
    return render(request, 'marketplace/index.html', {'books': books})

