from django.test import TestCase
from django.db import models
from datetime import datetime, timedelta
from base_app.models import Author, Book, BookCopy, LibraryUser, BorrowRecord
from django.db import DatabaseError
from django.core.exceptions import ObjectDoesNotExist

class AuthorManagerTest(TestCase):
    @classmethod
    def setUp(cls):
        # insert one entry in the database before each test
        cls.author = Author(name='James Gosling', is_popular=True)
        Author.objects.insert_author(cls.author)

    def test_insert_author_successful_insertion(self):
        author = Author(name='Robert C. Martin', is_popular=False)
        returned_author = Author.objects.insert_author(author)
        self.assertEqual(returned_author.name, author.name)

    def test_insert_author_raises_exception(self):
        author1 = Author(name='Robert C. Martin', is_popular=False)
        Author.objects.insert_author(author1)
        author2 = Author(name='Robert C. Martin', is_popular=True)
        self.assertRaises(DatabaseError, Author.objects.insert_author, author2)

    def test_get_author_count(self):
        self.assertEqual(Author.objects.get_author_count(), 1)
    
    def test_get_author_with_exact_name_returns_valid_author(self):
        returned_author = Author.objects.get_author_with_exact_name(self.author.name)
        self.assertEqual(returned_author.name, self.author.name)
        self.assertEqual(returned_author.is_popular, self.author.is_popular)

    def test_get_author_with_exact_name_raises_exception(self):
        test_name = 'John Doe'
        self.assertRaises(ObjectDoesNotExist, Author.objects.get_author_with_exact_name, test_name)

    def test_get_all_authors_with_similar_name_returns_valid_authors(self):
        Author.objects.create(name='William S. Vincent', is_popular=False)
        Author.objects.create(name='William C. Wake', is_popular=True)

        search_name = 'william'
        authors = list(Author.objects.get_all_authors_with_similar_name(search_name))

        self.assertEqual(len(authors), 2)

        for author in authors:
            self.assertTrue(search_name in author.name.lower())

    def test_update_author_name(self):
        old_name = self.author.name
        new_name = 'James Arthur Gosling'
        rows_affected = Author.objects.update_author_name(old_name, new_name)
        self.assertEqual(rows_affected, 1)
        self.assertRaises(ObjectDoesNotExist, Author.objects.get_author_with_exact_name, old_name)
    
    def test_update_author_popularity(self):
        old_is_popular = self.author.is_popular
        rows_affected = Author.objects.update_author_popularity(self.author.name, not old_is_popular)
        self.assertEqual(rows_affected, 1)
        updated_author = Author.objects.get_author_with_exact_name(self.author.name)
        self.assertEqual(updated_author.is_popular, not old_is_popular)

    def test_delete_author_successful_deletion(self):
        record_count = Author.objects.get_author_count()
        rows_affected = Author.objects.delete_author(self.author.name)
        self.assertEqual(rows_affected, 1)
        self.assertEqual(Author.objects.filter(name=self.author.name).count(), record_count-1)

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
