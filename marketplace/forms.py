# marketplace/forms.py

from django import forms
from .models import Book

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        # The 'seller' and 'is_sold' fields will be handled by our backend automatically.
        fields = ['title', 'author', 'isbn', 'condition', 'price', 'photo']
        
        # We add Bootstrap CSS classes to the form inputs so they look nice
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'author': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Optional'}),
            'condition': forms.Select(attrs={'class': 'form-select'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }