from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import APIException
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

import rest_api.services as services
from base_app.models import Book, LibraryUser

from .serializers import (BookSerializer, BorrowRecordSerializer,
                          LibraryUserSerializer)


@api_view(['GET'])
def get_all_books_api(request):
    books = Book.objects.all()
    book_serializer = BookSerializer(books, many=True)
    return Response(book_serializer.data)


@api_view(['GET'])
def get_all_available_books_api(request):
    books = services.get_all_available_books()
    book_serializer = BookSerializer(books, many=True)
    return Response(book_serializer.data)


@api_view(['GET'])
def get_all_books_by_author_name_api(request, name):
    books = services.get_all_books_by_similar_author_name(name)
    book_serializer = BookSerializer(books, many=True)
    return Response(book_serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def borrow_book_api(request):
    username = request.user.username
    owl_id = request.data.get('owl_id', None)
    try:
        borrow_record = services.borrow_book(owl_id=owl_id, username=username)
        borrow_record_serializer = BorrowRecordSerializer(borrow_record, many=False)
        return Response(borrow_record_serializer.data)
    except Exception as e:
        raise APIException(detail=e)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def return_book_api(request):
    username = request.user.username
    owl_id = request.data.get('owl_id', None)
    try:
        success = services.return_book(owl_id=owl_id, username=username)
        if success is True:
            return Response('Book returned successfully')
        else:
            return Response('Book not returned, please try again')
    except Exception as e:
        raise APIException(detail=e)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_book_availability_api(request, owl_id):
    username = request.user.username
    try:
        info = services.get_next_borrow_date(owl_id=owl_id, username=username)
        return Response(info)
    except Exception as e:
        raise APIException(detail=e)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_my_borrow_records_api(request):
    username = request.user.username
    borrow_records = services.get_my_borrow_records(username=username)
    borrow_records_serializer = BorrowRecordSerializer(borrow_records, many=True)
    return Response(borrow_records_serializer.data)


# class based library user create view, temporary untested code
class LibraryUserCreate(generics.CreateAPIView):
    queryset = LibraryUser.objects.all()
    serializer_class = LibraryUserSerializer
    permission_classes = (AllowAny, )
