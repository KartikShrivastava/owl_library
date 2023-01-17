from datetime import timedelta

from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist, ValidationError

from base_app.models import Author, Book, BookCopy, BorrowRecord, LibraryUser


def _is_author_popular(name):
    if len(name) == 0:
        return False
    # identity author with name starting with letter 'j' or 'J' as popular
    return name[0] == 'j' or name[0] == 'J'


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
        book = Book.objects.get_book_with_exact_title(book_title=book_title)
        book_copy_instance = BookCopy(book=book, book_copy_type=book_type)
        BookCopy.objects.insert_book_copy(book_copy_instance)
    except Exception as e:
        raise e


def _get_borrow_records_of_all_borrowed_books():
    borrowed_books = BorrowRecord.objects.filter(is_returned=False)
    return borrowed_books


def _get_distinct_book_copy_ids_of_borrowed_books():
    borrowed_books = _get_borrow_records_of_all_borrowed_books()
    distinct_book_copy_ids_of_borrowed_books = borrowed_books.values_list(
                                        'book_copy_id', flat=True).distinct()
    return distinct_book_copy_ids_of_borrowed_books


def get_all_available_book_copies():
    distinct_book_copy_ids_of_borrowed_books = _get_distinct_book_copy_ids_of_borrowed_books()
    available_book_copies = BookCopy.objects.exclude(
                            book_copy_id__in=distinct_book_copy_ids_of_borrowed_books)
    return available_book_copies


# Warning: This method throws exception if author with name does not exist
# Use get_all_books_by_similar_author_name(...) instead for better user experience
def get_all_books_by_exact_author_name(name):
    author_with_exact_name = Author.objects.get_author_with_exact_name(name)
    books = Book.objects.filter(author_id=author_with_exact_name.author_id)
    return books


def get_all_books_by_similar_author_name(name):
    authors_with_similar_name = Author.objects.get_all_authors_with_similar_name(name)
    books = Book.objects.filter(
            author_id__in=authors_with_similar_name.values_list('author_id', flat=True))
    return books


def _get_previous_borrow_record(owl_id, username):
    # throws exception if borrow record does not exist, i.e. book wasn't borrowed previously
    try:
        borrow_record = BorrowRecord.objects.get_borrow_record_by_owl_id_and_username(
                        owl_id=owl_id, username=username)
        return borrow_record
    except Exception:
        return None


def _get_book_borrow_duration_in_days():
    return 14


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
    # taking average number of days in a month as 30
    num_days_in_month = 30
    return num_days_in_month * cool_down_period_in_months


def _get_cool_down_period_of_normal_author_in_days():
    cool_down_period_in_months = 3
    # taking average number of days in a month as 30
    num_days_in_month = 30
    return num_days_in_month * cool_down_period_in_months


def _get_author_by_owl_id_of_book(owl_id):
    return Author.objects.filter(book__owl_id=owl_id)


def _get_cool_down_period_in_days(owl_id):
    author = _get_author_by_owl_id_of_book(owl_id=owl_id)
    author_name = author.name
    if _is_author_popular(author_name) is True:
        return _get_cool_down_period_of_popular_author_in_days
    else:
        return _get_cool_down_period_of_normal_author_in_days


def _get_cool_down_period_end_date(previous_borrow_date, owl_id):
    cool_down_period_in_days = _get_cool_down_period_in_days(owl_id)
    cool_down_period_end_date = previous_borrow_date+timedelta(days=cool_down_period_in_days)
    return cool_down_period_end_date


def _can_borrow_book_again(previous_borrow_date, owl_id):
    cool_down_period_end_date = _get_cool_down_period_end_date(previous_borrow_date)
    current_borrow_date = timezone.now()
    is_cool_down_period_ended = cool_down_period_end_date < current_borrow_date
    return is_cool_down_period_ended


def borrow_book(owl_id, username):
    previous_borrow_record = _get_previous_borrow_record(owl_id, username)
    if previous_borrow_record is None:
        new_borrow_record = _create_new_borrow_record(owl_id, username)
        return new_borrow_record
    else:
        previous_borrow_date = previous_borrow_record.borrow_date
        if _can_borrow_book_again(previous_borrow_date, owl_id) is True:
            current_date = timezone.now()
            new_borrow_date = current_date
            new_return_date = current_date+current_date+timedelta(
                    days=_get_book_borrow_duration_in_days())
            new_return_status = False
            updated_borrow_record = BorrowRecord.objects.update_borrow_record(
                                    borrow_date=new_borrow_date, return_date=new_return_date,
                                    is_returned=new_return_status)
            return updated_borrow_record
        else:
            raise ValidationError('Cannot borrow back book too frequently')


def _is_book_already_returned(borrow_record_id):
    borrow_record = BorrowRecord.objects.get_borrow_record_by_id(
                    borrow_record_id=borrow_record_id)
    is_returned = borrow_record.is_returned
    return is_returned is True


# returns True is book returned successfully else False
def return_book(owl_id, username):
    try:
        borrow_record = BorrowRecord.objects.get_borrow_record_by_owl_id_and_username(
                        owl_id=owl_id, username=username)
    except ObjectDoesNotExist as e:
        raise e

    if _is_book_already_returned(borrow_record.borrow_record_id) is True:
        raise ValidationError('Book already returned')

    rows_affected = BorrowRecord.objects.update_return_status(
                    borrow_record_id=borrow_record.borrow_record_id)
    return rows_affected == 1


def get_next_borrow_date(owl_id, username):
    try:
        borrow_record = BorrowRecord.objects.get_borrow_record_by_owl_id_and_username(
                        owl_id=owl_id, username=username)
    except ObjectDoesNotExist:
        return 'You can borrow this book immediately'

    previous_borrow_date = borrow_record.borrow_date
    cool_down_period_end_date = _get_cool_down_period_end_date(previous_borrow_date, owl_id)
    current_borrow_date = timezone.now()
    if cool_down_period_end_date < current_borrow_date:
        return 'You can borrow this book immediately'
    else:
        date = cool_down_period_end_date.date()
        formatted_date = f'{date.day}/{date.month}/{date.year}'
        return f'You can borrow this book again on {formatted_date}'
