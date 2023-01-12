from rest_framework.response import Response
from rest_framework.decorators import api_view
from base_app.models import Book, Borrower, BookBorrower
from .serializers import BookSerializer

@api_view(['GET'])
def getAllBooks(request):
    books = Book.objects.all()
    bookSerializer = BookSerializer(books, many=True)
    return Response(bookSerializer.data)

@api_view(['GET'])
def getBookDetails(request, owl_id):
    return Response()

@api_view(['POST'])
def borrowBook(request):
    return Response()

@api_view(['UPDATE'])
def returnBook(request):
    return Response()
