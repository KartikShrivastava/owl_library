from django.db import models
import uuid

class Author(models.Model):
    name = models.CharField(primary_key=True, max_length=200, help_text='Full name of author')
    is_popular = models.BooleanField()

    def __str__(self) -> str:
        return f'{self.name}'

class Book(models.Model):
    owl_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.PROTECT)

    class Meta:
        unique_together = ('title', 'author')

    def __str__(self) -> str:
        return f'{self.title}'

class BookCopy(models.Model):
    book_copy_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    book = models.ForeignKey('Book', on_delete=models.PROTECT)
    
    BOOK_COPY_TYPE = (
        ('pb', 'PAPERBACK'),
        ('hc', 'HARDCOVER'),
        ('hm', 'HANDMADE'),
        ('nd', 'NOTDEFINED')
    )
    
    book_copy_type = models.CharField(
        max_length=2,
        choices=BOOK_COPY_TYPE,
        blank=True,
        default='nd'
    )

    def __str__(self) -> str:
        return f'{self.book_copy_id} ({self.book})'

class LibraryUser(models.Model):
    email = models.EmailField(primary_key=True)
    username = models.CharField(max_length=200, verbose_name='user name')

    def __str__(self) -> str:
        return f'{self.email}'

class BorrowRecord(models.Model):
    borrow_record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    borrow_date = models.DateTimeField()
    return_date = models.DateTimeField()
    is_returned = models.BooleanField(default=False)

    book_copy = models.ForeignKey('BookCopy', on_delete=models.PROTECT)
    library_user = models.ForeignKey('LibraryUser', on_delete=models.PROTECT)

    class Meta:
        unique_together = ('book_copy', 'library_user')

    def __str__(self) -> str:
        return f'{self.borrow_record_id}'
