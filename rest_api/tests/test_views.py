from datetime import timedelta
from unittest import mock

from django.utils import timezone
from rest_framework.test import APITestCase

from base_app.models import Author, Book, BookCopy, BorrowRecord, LibraryUser


class ViewsHttpEndpointTest(APITestCase):
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
        copy = BookCopy.objects.create(book=self.popular_book, book_copy_type=BookCopy.BOOK_COPY_TYPE.HANDMADE)
        self.popular_user = LibraryUser.objects.create(username='JG', password='pass')

    def tearDown(self):
        BorrowRecord.objects.all().delete()
        LibraryUser.objects.all().delete()
        BookCopy.objects.all().delete()
        Book.objects.all().delete()
        Author.objects.all().delete()

    def test_get_all_books_api(self):
        url = '/'
        response = self.client.get(url)
        expected_value = Book.objects.all().count()
        response_data_len = len(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data_len, expected_value)

    def test_get_all_available_books_api(self):
        url = '/books/available/'
        response = self.client.get(url)
        expected_value = 1
        response_data_len = len(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data_len, expected_value)

    def test_get_all_books_by_author_name_api(self):
        author_name = 'gosling'
        url = f'/books/author/{author_name}'
        response = self.client.get(url)
        expected_value = 1
        response_data_len = len(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data_len, expected_value)

    def test_borrow_book_api_successful_request(self):
        # force authenticate client
        self.client.force_authenticate(user=self.normal_user)
        self.assertEqual(BorrowRecord.objects.all().count(), 2)
        url = '/accounts/borrow/'
        book_owl_id = self.popular_book.owl_id
        response = self.client.post(url, {'owl_id': f'{book_owl_id}'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(BorrowRecord.objects.all().count(), 3)

    def test_return_book_api(self):
        self.client.force_authenticate(user=self.normal_user)
        borrow_record = BorrowRecord.objects.get_borrow_record_by_owl_id_and_username(
                        owl_id=self.normal_book.owl_id, username=self.normal_user.username)
        self.assertEqual(borrow_record.is_returned, False)
        url = '/accounts/return/'
        book_owl_id = self.normal_book.owl_id
        response = self.client.put(url, {'owl_id': f'{book_owl_id}'})
        self.assertEqual(response.status_code, 200)
        borrow_record = BorrowRecord.objects.get_borrow_record_by_owl_id_and_username(
                        owl_id=self.normal_book.owl_id, username=self.normal_user.username)
        self.assertEqual(borrow_record.is_returned, True)

    @mock.patch('rest_api.services.get_next_borrow_date')
    def test_get_book_availability_api(self, mocked_func):
        self.client.force_authenticate(user=self.normal_user)

        mocked_func.return_value = 'You can borrow this book again on DD/MM/YYYY'
        book_owl_id = self.normal_book.owl_id
        url = f'/accounts/availability/{book_owl_id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        mocked_func.assert_called_with(owl_id=f'{book_owl_id}', username=self.normal_user.username)
