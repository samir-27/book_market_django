from django.db import models
from django.contrib.auth.models import User

class Book(models.Model):
    CONDITION_CHOICES = [
        ('NEW', 'Brand New'),
        ('LIKE_NEW', 'Like New'),
        ('GOOD', 'Good'),
        ('FAIR', 'Fair'),
        ('POOR', 'Poor'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='books_for_sale')
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=13, blank=True, null=True)
    # --- NEW FIELD ---
    description = models.TextField(blank=True, null=True) 
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    photo = models.ImageField(upload_to='book_photos/', blank=True, null=True)
    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

class Order(models.Model):
    # OneToOne ensures a book can only be bought once
    book = models.OneToOneField(Book, on_delete=models.CASCADE)
    # The user who bought it
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchased_orders')
    # The user who sold it
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sold_orders')
    
    # We save the price here just in case the seller edits the book price later. 
    # This acts as a permanent receipt.
    purchase_price = models.DecimalField(max_digits=6, decimal_places=2)
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book.title} bought by {self.buyer.username}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        # This prevents a user from adding the same book to their wishlist twice
        unique_together = ('user', 'book') 

    def __str__(self):
        return f"{self.user.username} wants {self.book.title}"

class SellerRating(models.Model):
    # The user being rated (the seller)
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='seller_ratings')
    # The user giving the rating (the buyer)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='given_ratings')
    
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)]) # 1 to 5 stars
    review = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

def __str__(self):
        return f"{self.rating} stars for {self.seller.username} from {self.buyer.username}"