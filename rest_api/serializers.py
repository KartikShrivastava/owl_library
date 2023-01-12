from rest_framework import serializers
from base_app.models import Book, Borrower, BookBorrower

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'
