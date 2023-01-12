from django.db import models
import uuid

class Book(models.Model):
    owl_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    author_name = models.CharField(max_length=200, help_text='Full name of author')
    
    BOOK_TYPE = (
        ('pb', 'PAPERBACK'),
        ('hc', 'HARDCOVER'),
        ('hm', 'HANDMADE'),
        ('nd', 'NOTDEFINED')
    )
    
    type = models.CharField(
        max_length=2,
        choices=BOOK_TYPE,
        blank=True,
        default='nd',
        help_text='Book type'
    )

    is_borrowed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} ({self.owl_id})'

class Borrower(models.Model):
    email = models.EmailField(primary_key=True)
    username = models.CharField(max_length=200)

    def __str__(self):
        return f'{self.username} ({self.email})'

class BookBorrower(models.Model):
    book_borrower_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    borrower_email = models.ForeignKey('Borrower', on_delete=models.CASCADE, null=True)
    book_owl_id = models.ForeignKey('Book', on_delete=models.CASCADE, null=True)
    borrow_date = models.DateTimeField(auto_now=True)
    due_date = models.DateTimeField(null=True, blank=True)
    next_borrow_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.book_borrower_id}'

# edit email field to make it editable
# add __string__ methods
# add get url methods
# fixed typo
