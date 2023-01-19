from datetime import timedelta

from django.core.exceptions import ValidationError
from django.utils import timezone

from base_app.models import Author, Book, BookCopy, BorrowRecord, LibraryUser


def _is_author_popular(name):
    if type(name) != str:
        raise ValidationError('Only string arguments are allowed')
    if len(name) == 0:
        return False
    # identity author with name starting with letter 'j' or 'J' as popular
    return name[0] == 'j' or name[0] == 'J'


def _get_distinct_book_copy_ids_of_borrowed_books():
    borrowed_books = BorrowRecord.objects.get_all_borrow_records_by_return_status(
                        is_returned=False)
    distinct_book_copy_ids_of_borrowed_books = borrowed_books.values_list(
                                                'book_copy_id', flat=True).distinct()
    return distinct_book_copy_ids_of_borrowed_books


def _get_book_borrow_duration_in_days():
    return 14


def _get_number_of_days_in_month():
    # taking average number of days in a month as 30
    return 30


def _create_new_borrow_record(owl_id, username):
    book_copy = BookCopy.objects.get_book_copy_with_matching_owl_id(owl_id=owl_id)
    library_user = LibraryUser.objects.get(username=username)
    current_date = timezone.now()
    borrow_date = current_date
    return_date = current_date+timedelta(days=_get_book_borrow_duration_in_days())
    borrow_record_instance = BorrowRecord(
                                borrow_date=borrow_date, return_date=return_date,
                                is_returned=False, book_copy=book_copy,
                                library_user=library_user)
    borrow_record = BorrowRecord.objects.insert_borrow_record(
                    borrow_record=borrow_record_instance)
    return borrow_record


def _get_cool_down_period_of_popular_author_in_days():
    cool_down_period_in_months = 6
    return _get_number_of_days_in_month() * cool_down_period_in_months


def _get_cool_down_period_of_normal_author_in_days():
    cool_down_period_in_months = 3
    return _get_number_of_days_in_month() * cool_down_period_in_months


def _get_cool_down_period_in_days(owl_id):
    author_name = Author.objects.get_author_by_owl_id(owl_id=owl_id).name
    if _is_author_popular(author_name) is True:
        return _get_cool_down_period_of_popular_author_in_days()
    else:
        return _get_cool_down_period_of_normal_author_in_days()


def _get_cool_down_period_end_date(previous_borrow_date, owl_id):
    cool_down_period_in_days = _get_cool_down_period_in_days(owl_id)
    cool_down_period_end_date = previous_borrow_date+timedelta(days=cool_down_period_in_days)
    return cool_down_period_end_date


def _can_borrow_book_again(previous_borrow_date, owl_id):
    cool_down_period_end_date = _get_cool_down_period_end_date(previous_borrow_date, owl_id)
    current_borrow_date = timezone.now()
    is_cool_down_period_ended = cool_down_period_end_date < current_borrow_date
    return is_cool_down_period_ended


def _borrow_book_again(borrow_record_id):
    current_date = timezone.now()
    new_borrow_date = current_date
    new_return_date = current_date+timedelta(days=_get_book_borrow_duration_in_days())
    new_return_status = False
    rows_affected = BorrowRecord.objects.update_dates_and_status(
                    borrow_record_id=borrow_record_id, borrow_date=new_borrow_date,
                    return_date=new_return_date, return_status=new_return_status)
    if rows_affected != 1:
        raise ValidationError('Something went wrong, please try again')
    updated_borrow_record = BorrowRecord.objects.get_borrow_record_by_owl_id(
                            borrow_record_id=borrow_record_id)
    return updated_borrow_record


# returns None if borrow record does not exist, i.e. book wasn't borrowed previously
def _get_previous_borrow_record(owl_id, username):
    try:
        borrow_record = BorrowRecord.objects.get_borrow_record_by_owl_id_and_username(
                        owl_id=owl_id, username=username)
        return borrow_record
    except Exception:
        return None


def _try_update_borrow_record(owl_id, borrow_date, borrow_record_id):
    if _can_borrow_book_again(borrow_date, owl_id) is True:
        updated_borrow_record = _borrow_book_again(borrow_record_id)
        return updated_borrow_record
    else:
        raise ValidationError('Cannot borrow book again too frequently')


def _validate_book_owl_id(owl_id):
    try:
        Book.objects.get_book_by_owl_id(owl_id=owl_id)
    except Exception as e:
        raise e


def add_author(author_name):
    is_popular = _is_author_popular(author_name)
    author_instance = Author(name=author_name, is_popular=is_popular)
    try:
        return Author.objects.insert_author(author=author_instance)
    except Exception as e:
        raise e


def add_book(book_title, author_name):
    try:
        author = Author.objects.get_author_with_exact_name(name=author_name)
        book_instance = Book(title=book_title, author=author)
        return Book.objects.insert_book(book_instance)
    except Exception as e:
        raise e


def add_book_copy(book_title, book_type):
    try:
        book = Book.objects.get_book_by_exact_title(book_title=book_title)
        book_copy_instance = BookCopy(book=book, book_copy_type=book_type)
        BookCopy.objects.insert_book_copy(book_copy_instance)
    except Exception as e:
        raise e


def get_all_books():
    return Book.objects.get_all_books()


def get_all_available_books():
    distinct_book_copy_ids_of_borrowed_books = _get_distinct_book_copy_ids_of_borrowed_books()
    books = Book.objects.exclude(
            bookcopy__book_copy_id__in=distinct_book_copy_ids_of_borrowed_books)
    return books


def get_all_books_by_similar_author_name(name):
    authors_with_similar_name = Author.objects.get_all_authors_with_similar_name(name)
    author_ids_with_similar_name = authors_with_similar_name.values_list(
                                    'author_id', flat=True)
    books = Book.objects.get_all_books_by_author_id_list(
            author_id_list=author_ids_with_similar_name)
    return books


def borrow_book(owl_id, username):
    borrow_record = _get_previous_borrow_record(owl_id, username)
    if borrow_record is None:
        new_borrow_record = _create_new_borrow_record(owl_id, username)
        return new_borrow_record
    else:
        updated_borrow_record = _try_update_borrow_record(
                                owl_id, borrow_record.borrow_date,
                                borrow_record.borrow_record_id)
        return updated_borrow_record


# returns True is book returned successfully else False
def return_book(owl_id, username):
    try:
        borrow_record = BorrowRecord.objects.get_borrow_record_by_owl_id_and_username(
                        owl_id=owl_id, username=username)
        rows_affected = BorrowRecord.objects.update_return_status(
                        borrow_record_id=borrow_record.borrow_record_id,
                        return_status=True)
        return rows_affected == 1
    except Exception as e:
        raise e


def get_next_borrow_date(owl_id, username):
    _validate_book_owl_id(owl_id=owl_id)

    borrow_record = _get_previous_borrow_record(owl_id=owl_id, username=username)
    if borrow_record is None:
        return 'You can borrow this book immediately'
    elif borrow_record.is_returned is False:
        return 'You have not returned this book yet, kindly return it first'

    previous_borrow_date = borrow_record.borrow_date
    current_borrow_date = timezone.now()
    cool_down_period_end_date = _get_cool_down_period_end_date(previous_borrow_date, owl_id)

    if cool_down_period_end_date < current_borrow_date:
        return 'Book is now available, you can borrow it immediately'
    else:
        date = cool_down_period_end_date.date()
        formatted_date = f'{date.day}/{date.month}/{date.year}'
        return f'You can borrow this book again on {formatted_date}'


def get_my_borrow_records(username):
    return BorrowRecord.objects.get_all_borrow_records_by_username(username=username)
