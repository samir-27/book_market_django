from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib import messages
from .models import Book, Wishlist, Order, CartItem
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
    
    in_wishlist = False
    in_cart = False
    
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, book=book).exists()
        # Check if the user already has this specific book in their cart
        in_cart = CartItem.objects.filter(user=request.user, book=book).exists()
        
    return render(request, 'marketplace/book_detail.html', {
        'book': book, 
        'in_wishlist': in_wishlist,
        'in_cart': in_cart 
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
    wishlist_item = Wishlist.objects.filter(user=request.user, book=book).first()
    
    if wishlist_item:
        wishlist_item.delete()
    else:
        Wishlist.objects.create(user=request.user, book=book)
        
    # NEW: Redirect back to the previous page (HTTP_REFERER), not always to book_detail.
    # This allows users to click "Remove" from the Wishlist page itself!
    previous_url = request.META.get('HTTP_REFERER', 'book_list')
    return redirect(previous_url)



@login_required
def my_wishlist(request):
    # Fetch all wishlist items for this user
    # select_related('book') makes the database query much faster by grabbing book data at the same time
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('book').order_by('-added_at')
    return render(request, 'marketplace/wishlist.html', {'wishlist_items': wishlist_items})

@login_required
def my_listings(request):
    # Fetch all books listed by the current user, newest first
    books = Book.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'marketplace/my_listings.html', {'books': books})


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
def edit_book(request, book_id):
    # seller=request.user ensures users cannot edit someone else's book
    book = get_object_or_404(Book, id=book_id, seller=request.user)
    
    if request.method == 'POST':
        # 'instance=book' tells Django to UPDATE the existing book instead of creating a new one
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, f'"{book.title}" updated successfully!')
            return redirect('book_detail', book_id=book.id)
    else:
        # Pre-populate the form with existing data
        form = BookForm(instance=book)
        
    return render(request, 'marketplace/edit_book.html', {'form': form, 'book': book})

@login_required
def delete_book(request, book_id):
    if request.method == 'POST':
        # Ensure only the owner can delete the book
        book = get_object_or_404(Book, id=book_id, seller=request.user)
        title = book.title
        book.delete()
        messages.success(request, f'"{title}" was successfully deleted.')
        return redirect('my_listings')
        
    return redirect('my_listings')

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


@login_required
def add_to_cart(request, book_id):
    if request.method == 'POST':
        book = get_object_or_404(Book, id=book_id)
        # Prevent adding sold books or your own books
        if not book.is_sold and book.seller != request.user:
            # get_or_create prevents errors if they spam the button
            CartItem.objects.get_or_create(user=request.user, book=book)
            messages.success(request, f"{book.title} added to your cart!")
    return redirect('book_detail', book_id=book_id)

@login_required
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        item = get_object_or_404(CartItem, id=item_id, user=request.user)
        item.delete()
        messages.info(request, "Item removed from cart.")
    return redirect('view_cart')

@login_required
def view_cart(request):
    cart_items = CartItem.objects.filter(user=request.user).select_related('book')
    # Calculate the total price of all items in the cart
    total_price = sum(item.book.price for item in cart_items if not item.book.is_sold)
    
    return render(request, 'marketplace/cart.html', {
        'cart_items': cart_items,
        'total_price': total_price
    })

@login_required
def checkout_cart(request):
    if request.method == 'POST':
        cart_items = CartItem.objects.filter(user=request.user).select_related('book')
        if not cart_items:
            return redirect('view_cart')
            
        successful_orders = 0
        for item in cart_items:
            if not item.book.is_sold:
                Order.objects.create(
                    book=item.book,
                    buyer=request.user,
                    seller=item.book.seller,
                    purchase_price=item.book.price
                )
                item.book.is_sold = True
                item.book.save()
                
                # <-- NEW: Remove this book from EVERYONE'S wishlist because it's sold!
                Wishlist.objects.filter(book=item.book).delete()
                
                successful_orders += 1
                
        cart_items.delete()
        if successful_orders > 0:
            messages.success(request, f"Successfully purchased {successful_orders} books!")
        else:
            messages.error(request, "Checkout failed. The books may have already been sold.")
            
        return redirect('order_history')