from datetime import timedelta
from unittest import mock

from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone

import rest_api.services as services
from base_app.models import Author, Book, BookCopy, BorrowRecord, LibraryUser


class HelperFunctionsTest(TestCase):
    def setUp(self):
        self.return_days = 14 # return_book_within_days
        self.normal_cd = 90 # normal_author_book_cool_down_period_in_days
        self.popular_cd = 180 # popular_author_book_cool_down_period_in_days
        d1 = timezone.now()
        d2 = timezone.now()+timedelta(days=self.return_days)
        author = Author.objects.create(name='Bjarne Stroustrup', is_popular=False)
        book = Book.objects.create(title='A Tour of C++', author=author)
        copy = BookCopy.objects.create(book=book, book_copy_type=BookCopy.BOOK_COPY_TYPE.HANDMADE)
        user = LibraryUser.objects.create(username='JD', password='pass')
        borrow = BorrowRecord.objects.create(borrow_date=d1, return_date=d2, book_copy=copy, library_user=user)

        author = Author.objects.create(name='Guido van Rossum', is_popular=False)
        self.normal_book = Book.objects.create(title='An Introduction to Python', author=author)
        copy = BookCopy.objects.create(book=self.normal_book, book_copy_type=BookCopy.BOOK_COPY_TYPE.HARDCOVER)
        self.normal_user = LibraryUser.objects.create(username='NK', password='pass')
        self.normal_borrow_record = BorrowRecord.objects.create(borrow_date=d1, return_date=d2, book_copy=copy, library_user=self.normal_user)

        author = Author.objects.create(name='James Gosling', is_popular=True)
        self.popular_book = Book.objects.create(title='The Java Language Specification', author=author)
        self.copy = BookCopy.objects.create(book=self.popular_book, book_copy_type=BookCopy.BOOK_COPY_TYPE.HANDMADE)
        self.user = LibraryUser.objects.create(username='JG', password='pass')

    def tearDown(self):
        BorrowRecord.objects.all().delete()
        LibraryUser.objects.all().delete()
        BookCopy.objects.all().delete()
        Book.objects.all().delete()
        Author.objects.all().delete()

    def test__is_author_popular_returns_valid_result(self):
        result_1_should_be_true = services._is_author_popular('Jack Black')
        result_2_should_be_true = services._is_author_popular('jonas brothers')
        result_3_should_be_false = services._is_author_popular('Black Panther')
        result_4_should_be_false = services._is_author_popular('')
        self.assertEqual(result_1_should_be_true, True)
        self.assertEqual(result_2_should_be_true, True)
        self.assertEqual(result_3_should_be_false, False)
        self.assertEqual(result_4_should_be_false, False)

    def test__is_popular_raises_exception_for_invalid_arguments(self):
        self.assertRaises(ValidationError, services._is_author_popular, 1)

    def test__get_distinct_book_copy_ids_of_borrowed_books(self):
        expected_ids = []
        expected_ids.append(BookCopy.objects.get(book__title='A Tour of C++').book_copy_id)
        expected_ids.append(BookCopy.objects.get(book__title='An Introduction to Python').book_copy_id)
        returned_ids = services._get_distinct_book_copy_ids_of_borrowed_books()
        self.assertTrue(len(returned_ids), len(expected_ids))
        for id in returned_ids:
            self.assertTrue(id in expected_ids)

    def test__create_new_borrow_record(self):
        created_record = services._create_new_borrow_record(self.popular_book.owl_id, self.user.username)
        self.assertEqual(created_record.book_copy.book_copy_id, self.copy.book_copy_id)
        self.assertEqual(created_record.library_user.username, self.user.username)
        borrow_date = created_record.borrow_date
        expected_return_date = borrow_date+timedelta(days=self.return_days)
        self.assertEqual(created_record.return_date, expected_return_date)

    def test__get_cool_down_period_of_popular_author_in_days(self):
        expected_duration = self.popular_cd
        returned_duration = services._get_cool_down_period_of_popular_author_in_days()
        self.assertEqual(returned_duration, expected_duration)

    def test__get_cool_down_period_of_normal_author_in_days(self):
        expected_duration = self.normal_cd
        returned_duration = services._get_cool_down_period_of_normal_author_in_days()
        self.assertEqual(returned_duration, expected_duration)

    def test__get_cool_down_period_in_days(self):
        expected_duration = self.popular_cd
        owl_id_of_book_with_popular_author = self.popular_book.owl_id
        returned_duration = services._get_cool_down_period_in_days(owl_id=owl_id_of_book_with_popular_author)
        self.assertEqual(returned_duration, expected_duration)
        expected_duration = self.normal_cd
        owl_id_of_book_with_normal_author = self.normal_book.owl_id
        returned_duration = services._get_cool_down_period_in_days(owl_id=owl_id_of_book_with_normal_author)
        self.assertEqual(returned_duration, expected_duration)

    def test__get_cool_down_period_end_date(self):
        borrow_date = timezone.now()
        returned_date = services._get_cool_down_period_end_date(
                        previous_borrow_date=borrow_date, owl_id=self.normal_book.owl_id)
        self.assertEqual(returned_date, borrow_date+timedelta(days=self.normal_cd))

    def test__can_borrow_book_again(self):
        borrow_date = timezone.now()
        result = services._can_borrow_book_again(
                    previous_borrow_date=borrow_date, owl_id=self.normal_book.owl_id)
        self.assertEqual(result, False)
        borrow_date = timezone.now()-timedelta(days=self.normal_cd)
        result = services._can_borrow_book_again(
                    previous_borrow_date=borrow_date, owl_id=self.normal_book.owl_id)
        self.assertEqual(result, True)

    def test__borrow_book_again(self):
        borrow_record = self.normal_borrow_record
        updated_borrow_record = services._borrow_book_again(borrow_record.borrow_record_id)
        self.assertEqual(updated_borrow_record.book_copy.book_copy_id, borrow_record.book_copy.book_copy_id)
        self.assertEqual(updated_borrow_record.library_user.username, borrow_record.library_user.username)
        borrow_date = updated_borrow_record.borrow_date
        self.assertEqual(updated_borrow_record.return_date, borrow_date+timedelta(days=self.return_days))

    def test__get_previous_borrow_record(self):
        borrow_record = self.normal_borrow_record
        returned_record = services._get_previous_borrow_record(
                            owl_id=self.normal_book.owl_id, username=self.normal_user.username)
        self.assertEqual(returned_record.borrow_date, borrow_record.borrow_date)
        self.assertEqual(returned_record.return_date, borrow_record.return_date)
        self.assertEqual(returned_record.book_copy.book_copy_id, borrow_record.book_copy.book_copy_id)
        self.assertEqual(returned_record.library_user.username, borrow_record.library_user.username)
        returned_record = services._get_previous_borrow_record(owl_id=None, username=self.normal_user.username)
        self.assertEqual(returned_record, None)

    @mock.patch('rest_api.services._borrow_book_again')
    @mock.patch('rest_api.services._can_borrow_book_again')
    def test__try_update_borrow_record_successful_updation(self, mocked_func_bottom, mocked_func_top):
        mocked_func_bottom.return_value = True
        owl_id = self.normal_book.owl_id
        borrow_date = self.normal_borrow_record.borrow_date-timedelta(days=self.normal_cd)
        borrow_record_id = self.normal_borrow_record.borrow_record_id
        services._try_update_borrow_record(
            owl_id=owl_id, borrow_date=borrow_date, borrow_record_id=borrow_record_id)
        mocked_func_bottom.assert_called_with(borrow_date, owl_id)
        mocked_func_top.assert_called_with(borrow_record_id)

    @mock.patch('rest_api.services._can_borrow_book_again')
    def test__try_update_borrow_record_raises_exception(self, mocked_func):
        mocked_func.return_value = False
        owl_id = self.normal_book.owl_id
        borrow_date = self.normal_borrow_record.borrow_date-timedelta(days=self.normal_cd)
        borrow_record_id = self.normal_borrow_record.borrow_record_id
        self.assertRaises(ValidationError, services._try_update_borrow_record,
                            owl_id=owl_id, borrow_date=borrow_date, borrow_record_id=borrow_record_id)

    def test__validate_book_owl_id_does_not_raise_exception(self):
        self.assertEqual(services._validate_book_owl_id(self.normal_book.owl_id), None)

    def test__validate_book_owl_id_raises_exception(self):
        self.assertRaises(Exception, services._validate_book_owl_id, owl_id=None)


class HttpEndpointFunctionsTest(TestCase):
    def setUp(self):
        self.return_days = 14 # return_book_within_days
        self.normal_cd = 90 # normal_author_book_cool_down_period_in_days
        self.popular_cd = 180 # popular_author_book_cool_down_period_in_days
        d1 = timezone.now()
        d2 = timezone.now()+timedelta(days=self.return_days)
        author = Author.objects.create(name='Bjarne Stroustrup', is_popular=False)
        book = Book.objects.create(title='A Tour of C++', author=author)
        copy = BookCopy.objects.create(book=book, book_copy_type=BookCopy.BOOK_COPY_TYPE.HANDMADE)
        user = LibraryUser.objects.create(username='JD', password='pass')
        borrow = BorrowRecord.objects.create(borrow_date=d1, return_date=d2, book_copy=copy, library_user=user)

        author = Author.objects.create(name='Guido van Rossum', is_popular=False)
        self.normal_book = Book.objects.create(title='An Introduction to Python', author=author)
        copy = BookCopy.objects.create(book=self.normal_book, book_copy_type=BookCopy.BOOK_COPY_TYPE.HARDCOVER)
        self.normal_user = LibraryUser.objects.create(username='NK', password='pass')
        self.normal_borrow_record = BorrowRecord.objects.create(borrow_date=d1, return_date=d2, book_copy=copy, library_user=self.normal_user)

        author = Author.objects.create(name='James Gosling', is_popular=True)
        self.popular_book = Book.objects.create(title='The Java Language Specification', author=author)
        self.copy = BookCopy.objects.create(book=self.popular_book, book_copy_type=BookCopy.BOOK_COPY_TYPE.HANDMADE)
        self.user = LibraryUser.objects.create(username='JG', password='pass')

    def tearDown(self):
        BorrowRecord.objects.all().delete()
        LibraryUser.objects.all().delete()
        BookCopy.objects.all().delete()
        Book.objects.all().delete()
        Author.objects.all().delete()

    def test_get_all_books(self):
        expected_books = Book.objects.all()
        returned_books = services.get_all_books()
        self.assertEqual(len(returned_books), len(expected_books))
        for book in returned_books:
            self.assertTrue(book in expected_books)

    def test_get_all_available_books(self):
        expected_books = [self.popular_book]
        returned_books = services.get_all_available_books()
        self.assertEqual(len(returned_books), len(expected_books))
        for book in returned_books:
            self.assertTrue(book in expected_books)

    def test_get_all_books_by_similar_author_name(self):
        expected_books = [self.normal_book]
        returned_books = services.get_all_books_by_similar_author_name('Guido van Rossum')
        self.assertEqual(len(returned_books), len(expected_books))
        for book in returned_books:
            self.assertTrue(book in expected_books)

    @mock.patch('rest_api.services._get_previous_borrow_record', return_value=None)
    @mock.patch('rest_api.services._create_new_borrow_record')
    def test_borrow_book_creates_new_borrow_record(self, mocked_func_bottom, mocked_func_top):
        services.borrow_book(owl_id=self.popular_book.owl_id, username=self.user.username)
        mocked_func_top.assert_called_with(self.popular_book.owl_id, self.user.username)
        mocked_func_bottom.assert_called_with(self.popular_book.owl_id, self.user.username)

    @mock.patch('rest_api.services._get_previous_borrow_record')
    @mock.patch('rest_api.services._try_update_borrow_record')
    def test_borrow_book_updates_existing_borrow_record(self, mocked_func_bottom, mocked_func_top):
        borrow_record = BorrowRecord.objects.get(book_copy__book__owl_id=self.normal_book.owl_id)
        mocked_func_top.return_value = borrow_record
        services.borrow_book(owl_id=self.popular_book.owl_id, username=self.user.username)
        mocked_func_top.assert_called_with(self.popular_book.owl_id, self.user.username)
        mocked_func_bottom.assert_called_with(self.popular_book.owl_id, borrow_record.borrow_date,
                                              borrow_record.borrow_record_id)

    def test_return_book_successfully(self):
        rows_affected = services.return_book(self.normal_book.owl_id, self.normal_user.username)
        self.assertEqual(rows_affected, True)

    def test_return_book_raises_exception_for_invalid_input(self):
        self.assertRaises(Exception, services.return_book, None, self.normal_user.username)
        self.assertRaises(Exception, services.return_book, None, None)

    @mock.patch('rest_api.services._validate_book_owl_id')
    def test_get_next_borrow_date(self, mocked_func):
        owl_id = self.normal_book.owl_id
        popular_owl_id = self.popular_book.owl_id
        username = self.normal_user.username
        borrow_record_id = self.normal_borrow_record.borrow_record_id
        borrow_date = self.normal_borrow_record.borrow_date
        return_date = self.normal_borrow_record.return_date

        result = services.get_next_borrow_date(owl_id=popular_owl_id, username=username)
        mocked_func.assert_called_with(owl_id=popular_owl_id)
        self.assertEqual(result, 'You can borrow this book immediately')

        result = services.get_next_borrow_date(owl_id=owl_id, username=username)
        mocked_func.assert_called_with(owl_id=owl_id)
        self.assertEqual(result, 'You have not returned this book yet, kindly return it first')
        
        BorrowRecord.objects.update_return_status(borrow_record_id=borrow_record_id, return_status=True)
        expected_date = borrow_date+timedelta(days=self.normal_cd)
        expected_date_string = f'{expected_date.day}/{expected_date.month}/{expected_date.year}'
        result = services.get_next_borrow_date(owl_id=owl_id, username=username)
        self.assertEqual(result, f'You can borrow this book again on {expected_date_string}')

        BorrowRecord.objects.update_dates_and_status(
            borrow_record_id=borrow_record_id,
            borrow_date=borrow_date-timedelta(days=self.normal_cd),
            return_date=return_date-timedelta(days=self.normal_cd),
            return_status=True)
        result = services.get_next_borrow_date(owl_id=owl_id, username=username)
        self.assertEqual(result, 'Book is now available, you can borrow it immediately')

    @mock.patch('base_app.models.BorrowRecord.objects.get_all_borrow_records_by_username')
    def test_get_my_borrow_records(self, mocked_func):
        services.get_my_borrow_records(username=self.normal_user.username)
        mocked_func.assert_called_with(username=self.normal_user.username)
