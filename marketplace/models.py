from django.db import models
from django.contrib.auth.models import User

# Create your models here.
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
    isbn = models.CharField(max_length=13, blank=True, null=True) # ISBNs are usually 10 or 13 digits
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=2) # Max 9999.99
    photo = models.ImageField(upload_to='book_photos/', blank=True, null=True)

    is_sold = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author}"

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