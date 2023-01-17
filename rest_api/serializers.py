from rest_framework import serializers

from base_app.models import Author, Book, LibraryUser, BookCopy, BorrowRecord


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    author = AuthorSerializer(many=False)

    class Meta:
        model = Book
        fields = '__all__'


class LibraryUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = LibraryUser
        fields = ('username', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        library_user = LibraryUser(**validated_data)
        library_user.set_password(password)
        library_user.save()
        return library_user


class BookCopySerializer(serializers.ModelSerializer):
    book = BookSerializer(many=False)

    class Meta:
        model = BookCopy
        fields = '__all__'


class BorrowRecordSerializer(serializers.ModelSerializer):
    book_copy = BookCopySerializer(many=False)

    class Meta:
        model = BorrowRecord
        fields = '__all__'
