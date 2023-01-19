from base_app.models import Author, Book, BookCopy

author = Author.objects.create(name='Robert C. Martin ', is_popular=False)
book = Book.objects.create(title='Clean Code', author=author)
book_copy = BookCopy.objects.create(book=book, book_copy_type='hm')

author = Author.objects.create(name='Greg Mckeown', is_popular=False)
# book without copy
book = Book.objects.create(title='Essentialism: The Disciplined Pursuit of Less', author=author)
book = Book.objects.create(title='Effortless: Make It Easier to Do What Matters Most', author=author)
book_copy = BookCopy.objects.create(book=book, book_copy_type='hc')

author = Author.objects.create(name='Dennis Ritchie', is_popular=False)
book = Book.objects.create(title='The C Programming Language', author=author)
book_copy = BookCopy.objects.create(book=book, book_copy_type='hc')

author = Author.objects.create(name='James Gosling', is_popular=True)
book = Book.objects.create(title='The Java Language Specification', author=author)
book_copy = BookCopy.objects.create(book=book, book_copy_type='pb')

author = Author.objects.create(name='Guido van Rossum', is_popular=False)
book = Book.objects.create(title='An Introduction to Python', author=author)
book_copy = BookCopy.objects.create(book=book, book_copy_type='hm')

author = Author.objects.create(name='Bjarne Stroustrup', is_popular=False)
book = Book.objects.create(title='A Tour of C++', author=author)
book_copy = BookCopy.objects.create(book=book, book_copy_type='hc')

author = Author.objects.create(name='William S. Vincent', is_popular=False)
book = Book.objects.create(title='Django for APIs: Build web APIs with Python & Django', author=author)
book_copy = BookCopy.objects.create(book=book, book_copy_type='pb')

author = Author.objects.create(name='William C. Wake', is_popular=False)
book = Book.objects.create(title='Refactoring Workbook', author=author)
book_copy = BookCopy.objects.create(book=book, book_copy_type='hc')

# extra author
author = Author.objects.create(name='Fred L. Drake', is_popular=False)
