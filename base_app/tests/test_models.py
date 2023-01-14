from django.test import TestCase
from django.db import models
from datetime import datetime, timedelta
from base_app.models import Author, Book, BookCopy, LibraryUser, BorrowRecord

class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = Author.objects.create(name='Napoleon Hill', is_popular=False)
    
    def test_object_name(self) -> None:
        self.assertEqual(str(self.author), f'{self.author.name}')

class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = Author.objects.create(name='Napoleon Hill', is_popular=False)
        cls.book = Book.objects.create(title='Think And Grow Rich', author=cls.author)
    
    def test_object_name(self) -> None:
        self.assertEqual(str(self.book), f'{self.book.title}')

class BookCopyModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = Author.objects.create(name='Napoleon Hill', is_popular=False)
        cls.book = Book.objects.create(title='Think And Grow Rich', author=cls.author)
        cls.bookCopy = BookCopy.objects.create(book=cls.book, book_copy_type='pb')
    
    def test_object_name(self) -> None:
        self.assertEqual(str(self.bookCopy), f'{self.bookCopy.book_copy_id} ({self.bookCopy.book})')

    def test_book_attribute_on_delete_value(self) -> None:
        self.assertEqual(self.bookCopy._meta.get_field('book').remote_field.on_delete, models.PROTECT)

class BorrowRecordModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = Author.objects.create(name='Napoleon Hill', is_popular=False)
        cls.book = Book.objects.create(title='Think And Grow Rich', author=cls.author)
        cls.bookCopy = BookCopy.objects.create(book=cls.book, book_copy_type='pb')
        cls.libraryUser = LibraryUser(email='john.doe@gmail.com', username='John Doe', password='pass')
        cls.borrowRecord = BorrowRecord(borrow_date=datetime.now(),
                                        return_date=datetime.now()+timedelta(days=14),
                                        book_copy=cls.bookCopy,
                                        library_user=cls.libraryUser)
    
    def test_object_name(self) -> None:
        self.assertEqual(str(self.borrowRecord), f'{self.borrowRecord.borrow_record_id}')

    def test_book_copy_attribute_on_delete_value(self) -> None:
        self.assertEqual(self.borrowRecord._meta.get_field('book_copy').remote_field.on_delete, models.PROTECT)

    def test_library_user_attribute_on_delete_value(self) -> None:
        self.assertEqual(self.borrowRecord._meta.get_field('library_user').remote_field.on_delete, models.PROTECT)
