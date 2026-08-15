from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from .models import Book, Wishlist, Order
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
    book = get_object_or_404(Book, id=book_id)
    
    # Check if the currently logged-in user has this book in their wishlist
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, book=book).exists()
        
    return render(request, 'marketplace/book_detail.html', {
        'book': book, 
        'in_wishlist': in_wishlist
    })

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

@login_required
def toggle_wishlist(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    
    # Look for an existing wishlist entry for this user and book
    wishlist_item = Wishlist.objects.filter(user=request.user, book=book).first()
    
    if wishlist_item:
        # If it exists, remove it (toggle off)
        wishlist_item.delete()
    else:
        # If it doesn't exist, create it (toggle on)
        Wishlist.objects.create(user=request.user, book=book)
        
    return redirect('book_detail', book_id=book.id)

@login_required
def my_wishlist(request):
    # Fetch all wishlist items for this user
    # select_related('book') makes the database query much faster by grabbing book data at the same time
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('book').order_by('-added_at')
    return render(request, 'marketplace/wishlist.html', {'wishlist_items': wishlist_items})



@login_required
def buy_book(request, book_id):
    # Only allow POST requests for purchasing
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)
        
        # Security checks: prevent buying sold books or buying your own book
        if book.is_sold or book.seller == request.user:
            return redirect('book_detail', book_id=book.id)
            
        # 1. Create the Order record
        Order.objects.create(
            book=book,
            buyer=request.user,
            seller=book.seller,
            purchase_price=book.price
        )
        
        # 2. Update the Book status
        book.is_sold = True
        book.save()
        
        return redirect('order_history')
        
    return redirect('book_list')

@login_required
def order_history(request):
    # Fetch orders where the current user is the buyer
    orders = Order.objects.filter(buyer=request.user).select_related('book', 'seller').order_by('-purchase_date')
    return render(request, 'marketplace/order_history.html', {'orders': orders})

@login_required
def sales_history(request):
    # Fetch orders where the current user is the seller
    sales = Order.objects.filter(seller=request.user).select_related('book', 'buyer').order_by('-purchase_date')
    return render(request, 'marketplace/sales_history.html', {'sales': sales})