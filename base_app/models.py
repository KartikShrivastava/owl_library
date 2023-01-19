import uuid

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError, models


# This model handles all queries related to Author model
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

    def get_author_by_owl_id(self, owl_id):
        if owl_id is None:
            raise ValidationError('Invalid owl_id')

        queryset = self.get_queryset()
        try:
            author = queryset.filter(book__owl_id=owl_id).get()
            return author
        except ObjectDoesNotExist as e:
            raise e

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
        if book.title is None or len(book.title) == 0:
            raise ValidationError('Cannot insert book with an empty title')

        queryset = self.get_queryset()
        try:
            return queryset.create(title=book.title, author=book.author)
        # raise ObjectDoesNotExist when book.author is null
        except ObjectDoesNotExist as e:
            raise e

    def get_book_by_owl_id(self, owl_id):
        queryset = self.get_queryset()
        try:
            return queryset.filter(owl_id=owl_id).get()
        except ObjectDoesNotExist as e:
            raise e

    # (Warning) use only if book with given title is known to exist, instead use
    # get_all_books_with_similar_title to check availability of book(s) with similar title
    def get_book_by_exact_title(self, book_title):
        queryset = self.get_queryset()
        try:
            return queryset.filter(title=book_title).get()
        except ObjectDoesNotExist as e:
            raise e

    # search is not case_sensitive
    def get_all_books_by_similar_title(self, book_title):
        queryset = self.get_queryset()
        books = queryset.filter(title__icontains=book_title)
        return books

    def get_all_books_by_author_id_list(self, author_id_list):
        queryset = self.get_queryset()
        books = queryset.filter(author_id__in=author_id_list)
        return books

    def get_all_books(self):
        queryset = self.get_queryset()
        return queryset.all()

    def update_book_title(self, owl_id, new_book_title):
        if new_book_title is None or len(new_book_title) == 0:
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


# Abstract representation of a book
class Book(models.Model):
    owl_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200)
    author = models.ForeignKey('Author', on_delete=models.PROTECT)

    objects = BookManager()

    class Meta:
        unique_together = ('title', 'author')

    def __str__(self) -> str:
        return f'{self.title}'


class BookCopyManager(models.Manager):
    def insert_book_copy(self, book_copy):
        if book_copy.book_copy_type not in BookCopy.BOOK_COPY_TYPE:
            raise ValidationError('Cannot insert BookCopy with invalid BOOK_COPY_TYPE')

        queryset = self.get_queryset()
        try:
            return queryset.create(book=book_copy.book,
                                   book_copy_type=book_copy.book_copy_type)
        except ObjectDoesNotExist as e:
            raise e

    def get_book_copy_with_matching_owl_id(self, owl_id):
        queryset = self.get_queryset()
        try:
            return queryset.filter(book__owl_id=owl_id).get()
        except Exception as e:
            raise e

    def update_book_copy_type(self, book_copy_id, new_book_copy_type):
        if new_book_copy_type not in BookCopy.BOOK_COPY_TYPE:
            raise ValidationError('Cannot update BookCopy with invalid BOOK_COPY_TYPE')

        queryset = self.get_queryset()
        rows_affected = queryset.filter(book_copy_id=book_copy_id) \
                                .update(book_copy_type=new_book_copy_type)
        return rows_affected

    def delete_book_copy(self, book_copy_id):
        queryset = self.get_queryset()
        rows_affected = queryset.filter(book_copy_id=book_copy_id).delete()[0]
        return rows_affected


# This model represents one or more physical/soft copy of a book present in library
class BookCopy(models.Model):
    book_copy_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # remove unique constraint and use ForeignKey to store more copies of the same book
    book = models.OneToOneField('Book', on_delete=models.PROTECT, unique=True)

    class BOOK_COPY_TYPE(models.TextChoices):
        PAPERBACK = 'pb', 'PAPERBACK'
        HARDCOVER = 'hc', 'HARDCOVER'
        HANDMADE = 'hm', 'HANDMADE'

    book_copy_type = models.CharField(
        max_length=2,
        choices=BOOK_COPY_TYPE.choices
    )

    objects = BookCopyManager()

    def __str__(self) -> str:
        return f'{self.book_copy_id} ({self.book})'


# LibraryUser model is actually a django User
class LibraryUser(AbstractUser):
    pass

    def __str__(self):
        return self.username


class BorrowRecordManager(models.Manager):
    def _borrow_date_greater_than_return_date(self, borrow_record):
        if borrow_record.borrow_date is not None and borrow_record.return_date is not None:
            if borrow_record.borrow_date > borrow_record.return_date:
                return True
        return False

    def insert_borrow_record(self, borrow_record):
        if self._borrow_date_greater_than_return_date(borrow_record=borrow_record) is True:
            raise ValidationError('Borrow date cannot be greater than return date')

        queryset = self.get_queryset()
        try:
            return queryset.create(borrow_date=borrow_record.borrow_date,
                                   return_date=borrow_record.return_date,
                                   is_returned=borrow_record.is_returned,
                                   book_copy=borrow_record.book_copy,
                                   library_user=borrow_record.library_user)
        except (DatabaseError, ObjectDoesNotExist) as e:
            raise e

    def get_borrow_record_by_owl_id(self, borrow_record_id):
        queryset = self.get_queryset()
        try:
            return queryset.filter(borrow_record_id=borrow_record_id).get()
        except ObjectDoesNotExist as e:
            raise e

    def get_borrow_record_by_owl_id_and_username(self, owl_id, username):
        queryset = self.get_queryset()
        try:
            return queryset.filter(book_copy__book__owl_id=owl_id,
                                   library_user__username=username).get()
        except ObjectDoesNotExist as e:
            raise e

    def get_all_borrow_records_by_owl_id(self, owl_id):
        queryset = self.get_queryset()
        borrow_records = queryset.filter(book_copy__book__owl_id=owl_id)
        return borrow_records

    def get_all_borrow_records_by_username(self, username):
        queryset = self.get_queryset()
        borrow_records = queryset.filter(library_user__username=username)
        return borrow_records

    def get_all_borrow_records_by_return_status(self, is_returned):
        queryset = self.get_queryset()
        borrow_records = queryset.filter(is_returned=is_returned)
        return borrow_records

    def update_return_status(self, borrow_record_id, return_status):
        queryset = self.get_queryset()
        rows_affected = queryset.filter(
                        borrow_record_id=borrow_record_id).update(is_returned=return_status)
        return rows_affected

    # update borrow_date, return_date and is_returned of BorrowRecord with borrw_record_id
    def update_dates_and_status(self, borrow_record_id, borrow_date, return_date,
                                return_status):
        if borrow_date >= return_date:
            raise ValidationError('Borrow date cannot be greater than return date')
        queryset = self.get_queryset()
        rows_affected = queryset.filter(borrow_record_id=borrow_record_id).update(
                        borrow_date=borrow_date, return_date=return_date,
                        is_returned=return_status)
        return rows_affected

    def delete_borrow_record_by_borrow_record_id(self, borrow_record_id):
        queryset = self.get_queryset()
        rows_affected = queryset.filter(
                        borrow_record_id=borrow_record_id).delete()[0]
        return rows_affected


# This model helps in maintaining relation between BookCopy and LibraryUser models
class BorrowRecord(models.Model):
    borrow_record_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    borrow_date = models.DateTimeField()
    return_date = models.DateTimeField()
    is_returned = models.BooleanField(default=False)

    book_copy = models.ForeignKey('BookCopy', on_delete=models.PROTECT)
    # extended django user (LibraryUser) is referenced by get_user_model()
    library_user = models.ForeignKey(get_user_model(), on_delete=models.PROTECT)

    objects = BorrowRecordManager()

    class Meta:
        unique_together = ('book_copy', 'library_user')

    def __str__(self) -> str:
        return f'{self.borrow_record_id}'
