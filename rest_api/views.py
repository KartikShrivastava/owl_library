from rest_framework.response import Response
from rest_framework.decorators import api_view
from base_app.models import Book
from .serializers import BookSerializer

@api_view(['GET'])
def getAllBooks(request) -> Response:
    books = Book.objects.all()
    bookSerializer = BookSerializer(books, many=True)
    return Response(bookSerializer.data)

@api_view(['GET'])
def getBookDetails(request, owl_id) -> Response:
    return Response()

@api_view(['POST'])
def borrowBook(request) -> Response:
    return Response()

@api_view(['UPDATE'])
def returnBook(request) -> Response:
    return Response()
