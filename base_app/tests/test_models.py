from django.test import TestCase
from django.db import models
from datetime import datetime, timedelta
from base_app.models import Author, Book, BookCopy, LibraryUser, BorrowRecord

class AuthorModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = Author.objects.create(name='Napoleon Hill', is_popular=False)
    
    def testVerboseNameValueOfAllAttributes(self) -> None:
        self.assertEqual(self.author._meta.get_field('name').verbose_name, 'name')
        self.assertEqual(self.author._meta.get_field('is_popular').verbose_name, 'is popular')

    def testObjectName(self) -> None:
        self.assertEqual(str(self.author), f'{self.author.name}')

    def testNameAttributeMaxLengthValue(self) -> None:
        self.assertEqual(self.author._meta.get_field('name').max_length, 200)

    def testNameAttributeHelpTextValue(self) -> None:
        self.assertEqual(self.author._meta.get_field('name').help_text, 'Full name of author')

class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = Author.objects.create(name='Napoleon Hill', is_popular=False)

        cls.book = Book.objects.create(title='Think And Grow Rich', author=cls.author)
    
    def testVerboseNameValueOfAllAttributes(self) -> None:
        self.assertEqual(self.book._meta.get_field('title').verbose_name, 'title')
        self.assertEqual(self.book._meta.get_field('author').verbose_name, 'author')

    def testObjectName(self) -> None:
        self.assertEqual(str(self.book), f'{self.book.title}')

    def testTitleAttributeMaxLengthValue(self) -> None:
        self.assertEqual(self.book._meta.get_field('title').max_length, 200)
    
    def testAuthorAttributeOnDeleteValue(self) -> None:
        self.assertEqual(self.book._meta.get_field('author').remote_field.on_delete, models.PROTECT)

class BookCopyModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = Author.objects.create(name='Napoleon Hill', is_popular=False)

        cls.book = Book.objects.create(title='Think And Grow Rich', author=cls.author)

        cls.bookCopy = BookCopy.objects.create(book=cls.book, book_copy_type='pb')
    
    def testVerboseNameValueOfAllAttributes(self) -> None:
        self.assertEqual(self.bookCopy._meta.get_field('book').verbose_name, 'book')
        self.assertEqual(self.bookCopy._meta.get_field('book_copy_type').verbose_name, 'book copy type')
    
    def testObjectName(self) -> None:
        self.assertEqual(str(self.bookCopy), f'{self.bookCopy.book_copy_id} ({self.bookCopy.book})')

    def testBookCopyTypeAttributeDefaultValue(self) -> None:
        self.assertEqual(self.bookCopy._meta.get_field('book_copy_type').default, 'nd')

    def testBookAttributeOnDeleteValue(self) -> None:
        self.assertEqual(self.bookCopy._meta.get_field('book').remote_field.on_delete, models.PROTECT)

class LibraryUserModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.libraryUser = LibraryUser(email='john.doe@gmail.com', username='John Doe')
    
    def testVerboseNameOfAllAttributes(self) -> None:
        self.assertEqual(self.libraryUser._meta.get_field('email').verbose_name, 'email')
        self.assertEqual(self.libraryUser._meta.get_field('username').verbose_name, 'user name')

    def testObjectName(self) -> None:
        self.assertEqual(str(self.libraryUser), f'{self.libraryUser.email}')
    
    def testUsernameAttributeMaxLengthValue(self) -> None:
        self.assertEqual(self.libraryUser._meta.get_field('username').max_length, 200)

class BorrowRecordModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = Author.objects.create(name='Napoleon Hill',
                              is_popular=False)

        cls.book = Book.objects.create(title='Think And Grow Rich',
                            author=cls.author)

        cls.bookCopy = BookCopy.objects.create(book=cls.book, book_copy_type='pb')

        cls.libraryUser = LibraryUser(email='john.doe@gmail.com', username='John Doe')

        cls.borrowRecord = BorrowRecord(borrow_date=datetime.now(),
                                        return_date=datetime.now()+timedelta(days=14),
                                        book_copy=cls.bookCopy,
                                        library_user=cls.libraryUser)
    
    def testVerboseNameOfAllAttributes(self) -> None:
        self.assertEqual(self.borrowRecord._meta.get_field('borrow_date').verbose_name, 'borrow date')
        self.assertEqual(self.borrowRecord._meta.get_field('return_date').verbose_name, 'return date')
        self.assertEqual(self.borrowRecord._meta.get_field('is_returned').verbose_name, 'is returned')
        self.assertEqual(self.borrowRecord._meta.get_field('book_copy').verbose_name, 'book copy')
        self.assertEqual(self.borrowRecord._meta.get_field('library_user').verbose_name, 'library user')
    
    def testObjectName(self) -> None:
        self.assertEqual(str(self.borrowRecord), f'{self.borrowRecord.borrow_record_id}')

    def testIsReturnedAttributeDefaultValue(self) -> None:
        self.assertEqual(self.borrowRecord._meta.get_field('is_returned').default, False)

    def testBookCopyAttributeOnDeleteValue(self) -> None:
        self.assertEqual(self.borrowRecord._meta.get_field('book_copy').remote_field.on_delete, models.PROTECT)

    def testLibraryUserAttributeOnDeleteValue(self) -> None:
        self.assertEqual(self.borrowRecord._meta.get_field('library_user').remote_field.on_delete, models.PROTECT)
        