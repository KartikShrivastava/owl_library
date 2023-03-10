import uuid
from datetime import timedelta

from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import DatabaseError, models
from django.test import TestCase
from django.utils import timezone

from base_app.models import Author, Book, BookCopy, BorrowRecord, LibraryUser


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

    def test_insert_author_raises_exception_for_duplicate_name(self):
        author1 = Author(name='Robert C. Martin', is_popular=False)
        Author.objects.insert_author(author1)
        author2 = Author(name='Robert C. Martin', is_popular=True)
        self.assertRaises(DatabaseError, Author.objects.insert_author, author=author2)

    def test_get_author_count(self):
        self.assertEqual(Author.objects.get_author_count(), 1)

    def test_get_author_with_exact_name_returns_valid_author(self):
        returned_author = Author.objects.get_author_with_exact_name(self.author.name)
        self.assertEqual(returned_author.name, self.author.name)
        self.assertEqual(returned_author.is_popular, self.author.is_popular)

    def test_get_author_with_exact_name_raises_exception_if_author_doesnt_exist(self):
        test_name = 'John Doe'
        self.assertRaises(ObjectDoesNotExist, Author.objects.get_author_with_exact_name,
                          test_name)

    def test_get_all_authors_with_similar_name_returns_valid_authors(self):
        Author.objects.create(name='William S. Vincent', is_popular=False)
        Author.objects.create(name='William C. Wake', is_popular=True)

        search_name = 'william'
        authors = list(Author.objects.get_all_authors_with_similar_name(search_name))

        self.assertEqual(len(authors), 2)

        for author in authors:
            self.assertTrue(search_name in author.name.lower())

    def test_get_author_by_owl_id_returns_valid_author(self):
        author = Author.objects.create(name='William S. Vincent', is_popular=False)
        book = Book.objects.create(author=author, title='Refactoring Workbook')
        returned_author = Author.objects.get_author_by_owl_id(owl_id=book.owl_id)
        self.assertEqual(returned_author.name, author.name)
        self.assertEqual(returned_author.is_popular, author.is_popular)

    def test_get_author_by_owl_id_raises_exception_for_invalid_owl_id(self):
        random_owl_id = uuid.uuid4()
        self.assertRaises(Exception, Author.objects.get_author_by_owl_id,
                          owl_id=random_owl_id)
        self.assertRaises(Exception, Author.objects.get_author_by_owl_id, owl_id=None)

    def test_update_author_name(self):
        old_name = self.author.name
        new_name = 'James Arthur Gosling'
        rows_affected = Author.objects.update_author_name(old_name, new_name)
        self.assertEqual(rows_affected, 1)
        self.assertRaises(ObjectDoesNotExist, Author.objects.get_author_with_exact_name,
                          old_name)

    def test_update_author_popularity(self):
        old_is_popular = self.author.is_popular
        rows_affected = Author.objects.update_author_popularity(self.author.name,
                                                                not old_is_popular)
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


class BookManagerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.insert_author(author=Author(name='Guido van Rossum',
                                                  is_popular=False))

    def test_insert_book_successful_insertion(self):
        title = 'An Introduction to Python'
        book = Book(title=title, author=self.author)
        inserted_book = Book.objects.insert_book(book=book)
        self.assertEqual(inserted_book.title, title)

    def test_insert_book_raises_exception_for_missing_author(self):
        book = Book(title='An Introduction to Python', author=None)
        self.assertRaises(ObjectDoesNotExist, Book.objects.insert_book, book=book)

    def test_insert_book_raises_exception_for_missing_title(self):
        book = Book(title=None, author=self.author)
        self.assertRaises(ValidationError, Book.objects.insert_book, book=book)

    def test_insert_book_raises_exception_for_empty_title(self):
        book = Book(title='', author=self.author)
        self.assertRaises(ValidationError, Book.objects.insert_book, book=book)

    def test_get_book_with_owl_id_returns_valid_book(self):
        book = Book(title='An Introduction to Python', author=self.author)
        inserted_book = Book.objects.insert_book(book=book)
        search_result = Book.objects.get_book_by_owl_id(owl_id=inserted_book.owl_id)
        self.assertEqual(search_result.owl_id, inserted_book.owl_id)

    def test_get_book_with_owl_id_raises_exception_if_book_not_found(self):
        random_uuid = uuid.uuid4()
        self.assertRaises(ObjectDoesNotExist, Book.objects.get_book_by_owl_id, random_uuid)

    def test_get_book_with_exact_title_returns_valid_book(self):
        title = 'An Introduction to Python'
        book = Book(title=title, author=self.author)
        Book.objects.insert_book(book=book)
        search_result = Book.objects.get_book_by_exact_title(book_title=title)
        self.assertEqual(search_result.title, title)

    def test_get_book_with_exact_title_raises_exception_if_book_doesnt_exist(self):
        title = 'An Introduction to Python'
        self.assertRaises(ObjectDoesNotExist, Book.objects.get_book_by_exact_title,
                          book_title=title)

    def test_get_all_books_with_similar_title_returns_valid_books(self):
        title1 = 'Django for APIs: Build web APIs with Python & Django'
        author1 = Author.objects.insert_author(author=Author(name='William S. Vincent',
                                                             is_popular=False))
        Book.objects.insert_book(book=Book(title=title1, author=author1))
        title2 = 'An Introduction to Python'
        author2 = self.author
        Book.objects.insert_book(book=Book(title=title2, author=author2))
        search_string = 'python'
        books = list(Book.objects.get_all_books_by_similar_title(book_title=search_string))
        self.assertEqual(len(books), 2)
        for book in books:
            self.assertTrue(search_string in book.title.lower())

    def test_get_all_books_by_author_id_list(self):
        author_1 = Author.objects.create(name='William S. Vincent', is_popular=False)
        author_2 = Author.objects.create(name='William C. Wake', is_popular=False)
        Book.objects.create(author=author_1,
                            title='Django for APIs: Build web APIs with Python & Django')
        Book.objects.create(author=author_1, title='Django for Professionals')
        Book.objects.create(author=author_2, title='Refactoring Workbook')
        author_id_list = [author_1.author_id, author_2.author_id]
        books = Book.objects.get_all_books_by_author_id_list(author_id_list=author_id_list)
        self.assertEqual(len(books), 3)

        author_id_list = [self.author.author_id]
        books = Book.objects.get_all_books_by_author_id_list(author_id_list=author_id_list)
        self.assertEqual(len(books), 0)

    def test_get_all_books(self):
        author1 = self.author
        book1 = Book(title='An Introduction to Python', author=author1)
        author2 = Author.objects.insert_author(author=Author(name='William S. Vincent',
                                                             is_popular=False))
        book2 = Book(title='Django for APIs: Build web APIs with Python & Django',
                     author=author2)
        author3 = Author.objects.insert_author(author=Author(name='James Gosling',
                                                             is_popular=True))
        book3 = Book(title='The Java Language Specification', author=author3)
        Book.objects.insert_book(book1)
        Book.objects.insert_book(book2)
        Book.objects.insert_book(book3)
        books = list(Book.objects.get_all_books())
        self.assertEqual(len(books), 3)

    def test_update_book_title_successful_updation(self):
        old_title = 'Intro to Python'
        inserted_book = Book.objects \
                            .insert_book(book=Book(title=old_title, author=self.author))
        new_title = 'An Introduction to Python'
        rows_affected = Book.objects.update_book_title(inserted_book.owl_id, new_title)
        self.assertEqual(rows_affected, 1)

    def test_update_book_title_raises_exception_for_empty_title(self):
        old_title = 'An Introduction to Python'
        inserted_book = Book.objects \
                            .insert_book(book=Book(title=old_title, author=self.author))
        new_title = ''
        self.assertRaises(ValidationError,
                          Book.objects.update_book_title,
                          inserted_book.owl_id, new_title)

    def test_update_book_author_successful_updation(self):
        old_author = self.author
        title = 'A Tour of C++'
        book = Book(title=title, author=old_author)
        inserted_book = Book.objects.insert_book(book=book)
        new_author = Author.objects.insert_author(author=Author(name='Bjarne Stroustrup',
                                                  is_popular=False))
        rows_affected = Book.objects.update_book_author(inserted_book.owl_id,
                                                        new_book_author=new_author)
        self.assertEqual(rows_affected, 1)

    def test_delete_book_successful_deletion(self):
        book = Book(title='An Introduction to Python', author=self.author)
        inserted_book = Book.objects.insert_book(book=book)
        rows_affected = Book.objects.delete_book(inserted_book.owl_id)
        self.assertEqual(rows_affected, 1)


class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.author = Author.objects.create(name='Napoleon Hill', is_popular=False)
        cls.book = Book.objects.create(title='Think And Grow Rich', author=cls.author)

    def test_object_name(self):
        self.assertEqual(str(self.book), f'{self.book.title}')


class BookCopyManagerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author_name = 'Greg Mckeown'
        book_title = 'Effortless: Make It Easier to Do What Matters Most'
        cls.author = Author.objects.insert_author(
                        author=Author(name=author_name, is_popular=False))
        cls.book = Book.objects.insert_book(book=Book(title=book_title, author=cls.author))

    def test_insert_book_copy_successful_insertion(self):
        book_copy = BookCopy(book=self.book, book_copy_type=BookCopy.BOOK_COPY_TYPE.HARDCOVER)
        inserted_book_copy = BookCopy.objects.insert_book_copy(book_copy=book_copy)
        self.assertEqual(inserted_book_copy.book.owl_id, self.book.owl_id)

    def test_insert_book_copy_raises_exception_for_missing_book(self):
        book_copy = BookCopy(book=None, book_copy_type=BookCopy.BOOK_COPY_TYPE.PAPERBACK)
        self.assertRaises(ObjectDoesNotExist, BookCopy.objects.insert_book_copy,
                          book_copy=book_copy)

    def test_insert_book_copy_raises_exception_for_invalid_book_copy_type(self):
        book_copy = BookCopy(book=self.book, book_copy_type='')
        self.assertRaises(ValidationError, BookCopy.objects.insert_book_copy,
                          book_copy=book_copy)
        book_copy = BookCopy(book=self.book, book_copy_type=None)
        self.assertRaises(ValidationError, BookCopy.objects.insert_book_copy,
                          book_copy=book_copy)

    def test_get_book_copy_with_matching_owl_id_returns_valid_book_copy(self):
        book_copy = BookCopy(book=self.book, book_copy_type=BookCopy.BOOK_COPY_TYPE.PAPERBACK)
        search_owl_id = self.book.owl_id
        BookCopy.objects.insert_book_copy(book_copy=book_copy)
        search_result = BookCopy.objects \
                                .get_book_copy_with_matching_owl_id(owl_id=search_owl_id)
        self.assertEqual(search_result.book.owl_id, search_owl_id)

    def test_get_book_copy_with_matching_owl_id_raises_exception_on_failed_search(self):
        search_owl_id = uuid.uuid4()
        self.assertRaises(ObjectDoesNotExist,
                          BookCopy.objects.get_book_copy_with_matching_owl_id,
                          owl_id=search_owl_id)

    def test_update_book_copy_type_successful_updation(self):
        book_copy = BookCopy(book=self.book, book_copy_type=BookCopy.BOOK_COPY_TYPE.PAPERBACK)
        book_copy_id = BookCopy.objects.insert_book_copy(book_copy=book_copy).book_copy_id
        new_book_copy_type = BookCopy.BOOK_COPY_TYPE.HARDCOVER
        rows_affected = BookCopy.objects.update_book_copy_type(
                                         book_copy_id=book_copy_id,
                                         new_book_copy_type=new_book_copy_type)
        self.assertEqual(rows_affected, 1)

    def test_update_book_copy_type_riases_exception_for_invalid_book_copy_type(self):
        book_copy = BookCopy(book=self.book, book_copy_type=BookCopy.BOOK_COPY_TYPE.PAPERBACK)
        book_copy_id = BookCopy.objects.insert_book_copy(book_copy=book_copy).book_copy_id
        new_book_copy_type = ''
        self.assertRaises(ValidationError, BookCopy.objects.update_book_copy_type,
                          book_copy_id=book_copy_id,
                          new_book_copy_type=new_book_copy_type)

    def test_delete_book_copy_successful_deletion(self):
        book_copy = BookCopy(book=self.book, book_copy_type=BookCopy.BOOK_COPY_TYPE.PAPERBACK)
        book_copy_id = BookCopy.objects.insert_book_copy(book_copy=book_copy).book_copy_id
        rows_affected = BookCopy.objects.delete_book_copy(book_copy_id=book_copy_id)
        self.assertEqual(rows_affected, 1)

    def test_delete_book_copy_raises_exception_for_invalid_book_copy_id(self):
        self.assertRaises(ValidationError, BookCopy.objects.delete_book_copy, book_copy_id='')


class BookCopyModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = Author.objects.create(name='Napoleon Hill', is_popular=False)
        cls.book = Book.objects.create(title='Think And Grow Rich', author=cls.author)
        cls.bookCopy = BookCopy.objects.create(book=cls.book, book_copy_type='pb')

    def test_object_name(self) -> None:
        self.assertEqual(str(self.bookCopy),
                         f'{self.bookCopy.book_copy_id} ({self.bookCopy.book})')

    def test_book_attribute_on_delete_value(self) -> None:
        self.assertEqual(self.bookCopy._meta.get_field('book').remote_field.on_delete,
                         models.PROTECT)


class BorrowRecordManagerTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author.objects.insert_author(author=Author(name='Bjarne Stroustrup',
                                                            is_popular=False))
        book = Book.objects.insert_book(book=Book(title='A Tour of C++', author=author))
        book_copy = BookCopy(book=book, book_copy_type=BookCopy.BOOK_COPY_TYPE.HANDMADE)
        cls.book_copy = BookCopy.objects.insert_book_copy(book_copy=book_copy)
        cls.library_user = LibraryUser.objects.create(
                            email='john.doe@gmail.com', username='John Doe', password='pass')

    def setUp(self):
        self.borrow_record_instance = BorrowRecord(
                                        borrow_date=timezone.now(),
                                        return_date=timezone.now()+timedelta(days=14),
                                        book_copy=self.book_copy,
                                        library_user=self.library_user)

    def test_insert_borrow_record_successful_insertion(self):
        borrow_record = self.borrow_record_instance
        inserted_record = BorrowRecord.objects.insert_borrow_record(
                            borrow_record=borrow_record)
        self.assertEqual(inserted_record.borrow_date, borrow_record.borrow_date)
        self.assertEqual(inserted_record.return_date, borrow_record.return_date)
        self.assertEqual(inserted_record.is_returned, False)
        self.assertEqual(inserted_record.book_copy, borrow_record.book_copy)
        self.assertEqual(inserted_record.library_user, borrow_record.library_user)

    def test_insert_borrow_record_raises_exception_for_missing_book_copy(self):
        borrow_record = self.borrow_record_instance
        borrow_record.book_copy = None
        self.assertRaises(ObjectDoesNotExist,
                          BorrowRecord.objects.insert_borrow_record,
                          borrow_record=borrow_record)

    def test_insert_borrow_record_raises_exception_for_missing_library_user(self):
        borrow_record = self.borrow_record_instance
        borrow_record.library_user = None
        self.assertRaises(ObjectDoesNotExist,
                          BorrowRecord.objects.insert_borrow_record,
                          borrow_record=borrow_record)

    def test_insert_borrow_record_raises_exception_for_missing_borrow_or_return_dates(self):
        borrow_record = BorrowRecord(
                        book_copy=self.book_copy, library_user=self.library_user)
        self.assertRaises(DatabaseError,
                          BorrowRecord.objects.insert_borrow_record,
                          borrow_record=borrow_record)

    def test_insert_borrow_record_raises_exception_for_return_less_than_borrow_date(self):
        borrow_record = self.borrow_record_instance
        borrow_record.borrow_date = borrow_record.return_date + timedelta(minutes=1)
        self.assertRaises(ValidationError,
                          BorrowRecord.objects.insert_borrow_record,
                          borrow_record=borrow_record)

    def test_get_borrow_record_by_id(self):
        borrow_record = self.borrow_record_instance
        borrow_record_id = BorrowRecord.objects.insert_borrow_record(
                            borrow_record=borrow_record).borrow_record_id
        search_result = BorrowRecord.objects.get_borrow_record_by_owl_id(
                        borrow_record_id=borrow_record_id)
        self.assertEqual(search_result.borrow_record_id, borrow_record_id)

    def test_get_borrow_record_by_id_raises_exception_for_invalid_borrow_record_id(self):
        self.assertRaises(Exception, BorrowRecord.objects.get_borrow_record_by_owl_id,
                          borrow_record_id=None)
        random_borrow_record_id = uuid.uuid4()
        self.assertRaises(Exception, BorrowRecord.objects.get_borrow_record_by_owl_id,
                          borrow_record_id=random_borrow_record_id)

    def test_get_borrow_record_by_owl_id_and_username_returns_valid_record(self):
        borrow_record = self.borrow_record_instance
        inserted_record = BorrowRecord.objects.insert_borrow_record(
                            borrow_record=borrow_record)
        owl_id = inserted_record.book_copy.book.owl_id
        username = inserted_record.library_user.get_username()
        search_result = BorrowRecord.objects.get_borrow_record_by_owl_id_and_username(
                        owl_id=owl_id, username=username)
        self.assertEqual(search_result, inserted_record)

    # test situation when owl_id or username is equal to None
    def test_get_borrow_record_by_owl_id_and_username_raises_exception(self):
        borrow_record = self.borrow_record_instance
        inserted_record = BorrowRecord.objects.insert_borrow_record(
                            borrow_record=borrow_record)
        owl_id = inserted_record.book_copy.book.owl_id
        username = inserted_record.library_user.get_username()
        self.assertRaises(ObjectDoesNotExist,
                          BorrowRecord.objects.get_borrow_record_by_owl_id_and_username,
                          owl_id=None, username=username)
        self.assertRaises(ObjectDoesNotExist,
                          BorrowRecord.objects.get_borrow_record_by_owl_id_and_username,
                          owl_id=owl_id, username=None)

    def test_get_all_borrow_records_by_owl_id_returns_valid_records(self):
        # insert two records belonging to same book_copy but different users
        # which is possible if second user borrows book after first user has returned it
        owl_id = self.book_copy.book.owl_id
        borrow_record = self.borrow_record_instance
        BorrowRecord.objects.insert_borrow_record(borrow_record=borrow_record)
        library_user_2 = LibraryUser.objects.create(username='Ravi')
        borrow_record.library_user = library_user_2
        BorrowRecord.objects.insert_borrow_record(borrow_record=borrow_record)
        borrow_records = list(BorrowRecord.objects.get_all_borrow_records_by_owl_id(
                           owl_id=owl_id))
        self.assertEqual(len(borrow_records), 2)

    def test_get_all_borrow_records_by_username_returns_valid_records(self):
        # insert two records belonging to same user but different book_copies
        username = self.library_user.username
        borrow_record = self.borrow_record_instance
        BorrowRecord.objects.insert_borrow_record(borrow_record=borrow_record)
        book_2 = Book.objects.insert_book(book=Book(
                    title='The Design and Evolution of C++',
                    author=self.book_copy.book.author))
        book_copy_instance_2 = BookCopy(
                                book=book_2, book_copy_type=BookCopy.BOOK_COPY_TYPE.HANDMADE)
        book_copy_2 = BookCopy.objects.insert_book_copy(book_copy=book_copy_instance_2)
        borrow_record.book_copy = book_copy_2
        BorrowRecord.objects.insert_borrow_record(borrow_record=borrow_record)
        borrow_records = list(BorrowRecord.objects.get_all_borrow_records_by_username(
                            username=username))
        self.assertEqual(len(borrow_records), 2)

    def test_get_all_borrow_records_by_return_status_returns_valid_result(self):
        borrow_record = self.borrow_record_instance
        BorrowRecord.objects.insert_borrow_record(borrow_record=borrow_record)
        book_2 = Book.objects.insert_book(book=Book(
                    title='The Design and Evolution of C++',
                    author=self.book_copy.book.author))
        book_copy_instance_2 = BookCopy(
                                book=book_2, book_copy_type=BookCopy.BOOK_COPY_TYPE.HANDMADE)
        book_copy_2 = BookCopy.objects.insert_book_copy(book_copy=book_copy_instance_2)
        borrow_record.book_copy = book_copy_2
        BorrowRecord.objects.insert_borrow_record(borrow_record=borrow_record)
        results = BorrowRecord.objects.get_all_borrow_records_by_return_status(
                    is_returned=False)
        self.assertEqual(len(results), 2)
        for borrow_record in results:
            self.assertEqual(borrow_record.is_returned, False)

        results = BorrowRecord.objects.get_all_borrow_records_by_return_status(
                    is_returned=True)
        self.assertEqual(len(results), 0)

    def test_update_return_status_successful_updation(self):
        borrow_record = self.borrow_record_instance
        borrow_record_id = BorrowRecord.objects.insert_borrow_record(
                            borrow_record=borrow_record).borrow_record_id
        new_return_status = True
        rows_affected = BorrowRecord.objects.update_return_status(
                        borrow_record_id=borrow_record_id, return_status=new_return_status)
        self.assertEqual(rows_affected, 1)
        self.assertEqual(BorrowRecord.objects.get_borrow_record_by_owl_id(
                            borrow_record_id=borrow_record_id).is_returned, new_return_status)

    def test_update_dates_and_status_successful_updation(self):
        borrow_record = self.borrow_record_instance
        borrow_record_id = BorrowRecord.objects.insert_borrow_record(
                            borrow_record=borrow_record).borrow_record_id
        new_borrow_date = timezone.now()
        new_return_date = timezone.now()+timedelta(days=14)
        rows_affected = BorrowRecord.objects.update_dates_and_status(
                        borrow_record_id=borrow_record_id, borrow_date=new_borrow_date,
                        return_date=new_return_date, return_status=False)
        self.assertEqual(rows_affected, 1)

    def test_update_dates_and_status_raises_exception_for_invalid_dates(self):
        borrow_record = self.borrow_record_instance
        borrow_record_id = BorrowRecord.objects.insert_borrow_record(
                            borrow_record=borrow_record).borrow_record_id
        new_borrow_date = timezone.now()
        new_return_date = new_borrow_date
        self.assertRaises(Exception, BorrowRecord.objects.update_dates_and_status,
                          borrow_record_id=borrow_record_id, borrow_date=new_borrow_date,
                          return_date=new_return_date, return_status=False)

    def test_delete_borrow_record_successful_deletion(self):
        borrow_record = self.borrow_record_instance
        borrow_record_id = BorrowRecord.objects.insert_borrow_record(
                            borrow_record=borrow_record).borrow_record_id
        rows_affected = BorrowRecord.objects.delete_borrow_record_by_borrow_record_id(
                        borrow_record_id=borrow_record_id)
        self.assertEqual(rows_affected, 1)

    def test_delete_borrow_record_do_nothing_for_none_borrow_record_id(self):
        self.assertEqual(BorrowRecord.objects.delete_borrow_record_by_borrow_record_id(
                            borrow_record_id=None), 0)

    def test_delete_borrow_record_raises_exception_for_invalid_borrow_record_id(self):
        self.assertRaises(ValidationError,
                          BorrowRecord.objects.delete_borrow_record_by_borrow_record_id,
                          borrow_record_id='')


class BorrowRecordModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        author = Author(name='Bjarne Stroustrup', is_popular=False)
        cls.author = Author.objects.insert_author(author=author)
        book = Book(title='A Tour of C++', author=cls.author)
        cls.book = Book.objects.insert_book(book=book)
        book_copy = BookCopy(book=cls.book, book_copy_type=BookCopy.BOOK_COPY_TYPE.HANDMADE)
        cls.book_copy = BookCopy.objects.insert_book_copy(book_copy=book_copy)
        cls.library_user = LibraryUser.objects.create(email='john.doe@gmail.com',
                                                      username='John Doe',
                                                      password='pass')
        borrow_record = BorrowRecord(borrow_date=timezone.now(),
                                     return_date=timezone.now()+timedelta(days=14),
                                     book_copy=cls.book_copy,
                                     library_user=cls.library_user)
        cls.borrow_record = BorrowRecord.objects.insert_borrow_record(
                            borrow_record=borrow_record)

    def test_object_name(self):
        self.assertEqual(str(self.borrow_record), f'{self.borrow_record.borrow_record_id}')

    def test_book_copy_attribute_on_delete_value(self):
        book_copy_on_delete_value = self.borrow_record._meta.get_field(
                                    'book_copy').remote_field.on_delete
        self.assertEqual(book_copy_on_delete_value, models.PROTECT)

    def test_library_user_attribute_on_delete_value(self):
        library_user_on_delete_value = self.borrow_record._meta.get_field(
                                        'library_user').remote_field.on_delete
        self.assertEqual(library_user_on_delete_value, models.PROTECT)
