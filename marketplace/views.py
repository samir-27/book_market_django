from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Book
from .forms import BookForm

def book_list(request):
    # Grab the search term from the URL (e.g., ?q=harry)
    query = request.GET.get('q')
    
    # Start with all unsold books
    books = Book.objects.filter(is_sold=False).order_by('-created_at')
    
    # If a search query exists, filter the books further
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query)
        )
    
    return render(request, 'marketplace/index.html', {'books': books})

def book_detail(request, book_id):
    # Fetch the exact book using its ID, or throw a 404 error if it doesn't exist
    book = get_object_or_404(Book, id=book_id)
    
    return render(request, 'marketplace/book_detail.html', {'book': book})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Automatically log the user in after registering
            return redirect('book_list')
    else:
        form = UserCreationForm()
    
    return render(request, 'marketplace/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('book_list')
    else:
        form = AuthenticationForm()
        
    return render(request, 'marketplace/login.html', {'form': form})

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        return redirect('book_list')

@login_required
def sell_book(request):
    if request.method == 'POST':
        # request.FILES is required whenever you are uploading images/files
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            # commit=False creates the book object but doesn't save it to the database yet
            book = form.save(commit=False)
            # Assign the currently logged-in user as the seller
            book.seller = request.user
            book.save()
            
            # Redirect them to the detail page of the book they just created
            return redirect('book_detail', book_id=book.id)
    else:
        form = BookForm()
        
    return render(request, 'marketplace/sell_book.html', {'form': form})