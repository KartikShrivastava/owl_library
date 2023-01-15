import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError, models


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

    # (Recommended) use only if author with given name exist, instead use
    # get_all_authors_with_similar_name to check author(s) in library with similar name
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


class BookManager(models.Manager):
    def insert_book(self, book):
        if book.title == None or len(book.title) == 0:
            raise ValidationError('Cannot insert book with an empty title')

        queryset = self.get_queryset()
        try:
            return queryset.create(title=book.title, author=book.author)
        # raise ObjectDoesNotExist when book.author is null
        except ObjectDoesNotExist as e:
            raise e

    def get_book_with_owl_id(self, owl_id):
        queryset = self.get_queryset()
        try:
            return queryset.filter(owl_id=owl_id).get()
        except ObjectDoesNotExist as e:
            raise e

    # (Recommended) use only if book with given title exist, instead use
    # get_all_books_with_similar_title to check availability of book(s) with similar title
    def get_book_with_exact_title(self, book_title):
        queryset = self.get_queryset()
        try:
            return queryset.filter(title=book_title).get()
        except ObjectDoesNotExist as e:
            raise e

    # search is not case_sensitive
    def get_all_books_with_similar_title(self, book_title):
        queryset = self.get_queryset()
        books = queryset.filter(title__icontains=book_title)
        return books

    def get_all_books_with_similar_author_name(self, author_name):
        queryset = self.get_queryset()
        books = queryset.filter(author__name__icontains=author_name)
        return books

    def get_all_books(self):
        queryset = self.get_queryset()
        return queryset.all()

    def update_book_title(self, owl_id, new_book_title):
        if len(new_book_title) == 0:
            raise ValidationError('Cannot update book title with an empty string')
        queryset = self.get_queryset()
        rows_affected = queryset.filter(owl_id=owl_id).update(title=new_book_title)
        return rows_affected

    def update_book_author(self, owl_id, new_book_author):
        queryset = self.get_queryset()
        rows_affected = queryset.filter(owl_id=owl_id).update(author=new_book_author)
        return rows_affected

    def delete_book(self, owl_id):
        queryset = self.get_queryset()
        rows_affected = queryset.filter(owl_id=owl_id).delete()[0]
        return rows_affected


class Book(models.Model):
    owl_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.PROTECT)

    objects = BookManager()

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
