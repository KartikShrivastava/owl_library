import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model
from django.db import DatabaseError
from django.core.exceptions import ObjectDoesNotExist

# This class handles all queries related to Author model
class AuthorManager(models.Manager):
    def insert_author(self, author):
        queryset = self.get_queryset()
        try:
            return queryset.create(name=author.name, is_popular=author.is_popular)
        except DatabaseError as e:
            raise e

    def get_author_count(self):
        queryset = self.get_queryset()
        return queryset.count()

    def get_author_with_exact_name(self, name):
        queryset = self.get_queryset()
        try:
            return queryset.filter(name=name).get()
        except ObjectDoesNotExist as e:
            raise e

    # this search is not case-sensitive
    def get_all_authors_with_similar_name(self, name):
        queryset = self.get_queryset()
        authors = queryset.filter(name__icontains=name)
        return authors

    def update_author_name(self, old_author_name, new_author_name):
        queryset = self.get_queryset()
        rows_affected = queryset.filter(name=old_author_name).update(name=new_author_name)
        return rows_affected

    def update_author_popularity(self, author_name, is_popular):
        queryset = self.get_queryset()
        rows_affected = queryset.filter(name=author_name).update(is_popular=is_popular)
        return rows_affected
    
    def delete_author(self, author_name):
        queryset = self.get_queryset()
        rows_affected = queryset.filter(name=author_name).delete()[0]
        return rows_affected

class Author(models.Model):
    author_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(unique=True, max_length=200, help_text='Full name of author')
    is_popular = models.BooleanField()

    objects = AuthorManager()

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

# LibraryUser is a django User
class LibraryUser(AbstractUser):
    pass

    def __str__(self):
        return self.username

class BorrowRecord(models.Model):
    borrow_record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    borrow_date = models.DateTimeField()
    return_date = models.DateTimeField()
    is_returned = models.BooleanField(default=False)

    book_copy = models.ForeignKey('BookCopy', on_delete=models.PROTECT)
    # extended django user (LibraryUser) is referenced by get_user_model()
    library_user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)

    class Meta:
        unique_together = ('book_copy', 'library_user')

    def __str__(self) -> str:
        return f'{self.borrow_record_id}'
