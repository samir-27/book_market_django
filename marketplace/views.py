from django.shortcuts import render, get_object_or_404
from .models import Book

def book_list(request):
    # Fetch all books that are NOT sold, ordered by newest first
    books = Book.objects.filter(is_sold=False).order_by('-created_at')
    return render(request, 'marketplace/index.html', {'books': books})

def book_detail(request, book_id):
    # Fetch the exact book using its ID, or throw a 404 error if it doesn't exist
    book = get_object_or_404(Book, id=book_id)
    
    return render(request, 'marketplace/book_detail.html', {'book': book})