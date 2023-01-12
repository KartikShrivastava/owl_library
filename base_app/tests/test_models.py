from django.test import TestCase
from datetime import datetime, timedelta
from base_app.models import Book, Borrower, BookBorrower

class BookModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Book.objects.create(title='Essentialism: The Disciplined Pursuit of Less',
                            author_name='Greg McKeown')
    
    def testVerboseNameOfAllAttributes(self) -> None:
        book = Book.objects.get(title='Essentialism: The Disciplined Pursuit of Less')
        self.assertEqual(book._meta.get_field('title').verbose_name, 'title')
        self.assertEqual(book._meta.get_field('author_name').verbose_name, 'author name')
        self.assertEqual(book._meta.get_field('type').verbose_name, 'book type')
        self.assertEqual(book._meta.get_field('is_borrowed').verbose_name, 'is borrowed')

    def testObjectName(self) -> None:
        book = Book.objects.get(title='Essentialism: The Disciplined Pursuit of Less')
        expectedObjectName = f'{book.title} ({book.owl_id})'
        self.assertEqual(str(book), expectedObjectName)
    
    def testTypeAttributeDefaultValue(self) -> None:
        book = Book.objects.get(title='Essentialism: The Disciplined Pursuit of Less')
        self.assertEqual(book.type, 'nd')
    
    def testIsBorrowedAttributeDefaultValue(self) -> None:
        book = Book.objects.get(title='Essentialism: The Disciplined Pursuit of Less')
        self.assertEqual(book.is_borrowed, False)

class BorrowerModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        Borrower.objects.create(email='john.doe@gmail.com',
                                username='John Doe')
    
    def testVerboseNameOfAllAttributes(self) -> None:
        borrower = Borrower.objects.get(email='john.doe@gmail.com')
        self.assertEqual(borrower._meta.get_field('email').verbose_name, 'email')
        self.assertEqual(borrower._meta.get_field('username').verbose_name, 'user name')

    def testObjectName(self) -> None:
        borrower = Borrower.objects.get(email='john.doe@gmail.com')
        expectedObjectName = f'{borrower.username} ({borrower.email})'
        self.assertEqual(str(borrower), expectedObjectName)

class BookBorrowerModelTest(TestCase):
    @classmethod
    def setUpTestData(cls) -> None:
        book = Book.objects.create(title='Essentialism: The Disciplined Pursuit of Less',
                            author_name='Greg McKeown',
                            type='pb')
        
        borrower = Borrower.objects.create(email='john.doe@gmail.com',
                                username='John Doe')

        BookBorrower.objects.create(borrower=borrower,
                                    book=book,
                                    due_date=datetime.now() + timedelta(days=30),
                                    next_borrow_date=datetime.now() + timedelta(days=120))
    
    def testVerboseNameOfAttributes(self) -> None:
        bookBorrower = BookBorrower.objects.get(borrower='john.doe@gmail.com')
        self.assertEqual(bookBorrower._meta.get_field('borrower').verbose_name, 'borrower')
        self.assertEqual(bookBorrower._meta.get_field('book').verbose_name, 'book')
        self.assertEqual(bookBorrower._meta.get_field('borrow_date').verbose_name, 'borrow date')
        self.assertEqual(bookBorrower._meta.get_field('due_date').verbose_name, 'due date')
        self.assertEqual(bookBorrower._meta.get_field('next_borrow_date').verbose_name, 'next borrow date')

    def testObjectName(self) -> None:
        bookBorrower = BookBorrower.objects.get(borrower='john.doe@gmail.com')
        expectedObjectName = f'{bookBorrower.book_borrower_id}'
        self.assertEqual(str(bookBorrower), expectedObjectName)
