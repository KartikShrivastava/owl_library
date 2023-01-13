from django.contrib import admin
from .models import Author, Book, BookCopy, LibraryUser, BorrowRecord

admin.site.register(Author)
admin.site.register(Book)
admin.site.register(BookCopy)
admin.site.register(LibraryUser)
admin.site.register(BorrowRecord)
