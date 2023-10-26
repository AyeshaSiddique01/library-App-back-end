from rest_framework import serializers

from library_app.models import Author, Book, BookRequest, Ticket, User, Role


class RoleSerializer(serializers.ModelSerializer):
    """Serializer for the Role model"""
    class Meta:
        """Configuration class defining the model and fields to include"""

        model = Role
        fields = ["id", "role"]


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model"""

    class Meta:
        """Configuration class defining the model and fields to include"""

        model = User
        fields = ["id", "username", "email", "password", "role"]


class AuthorSerializer(serializers.ModelSerializer):
    """Serializer for the Author model"""

    class Meta:
        """Configuration class defining the model and fields to include"""

        model = Author
        fields = ["id", "name", "email", "gender"]


class BookCreateSerializer(serializers.ModelSerializer):
    """Serializer to create, update and partial update Book objects"""
    class Meta:
        """Configuration class defining the model and fields to include"""

        model = Book
        fields = ["id", "name", "image", "publisher", "inventory", "author"]


class BookViewSerializer(serializers.ModelSerializer):
    """Serializer to view Books with author details"""
    author = AuthorSerializer(many=True)
    class Meta:
        """Configuration class defining the model and fields to include"""

        model = Book
        fields = ["id", "name", "image", "publisher", "inventory", "author"]


class BookRequestViewSerializer(serializers.ModelSerializer):
    """Serializer for the BookRequest model"""
    book = BookViewSerializer(many=False)
    class Meta:
        """Configuration class defining the model and fields to include"""

        model = BookRequest
        fields = ["id", "status", "requested_date", "issued_date", "returned_date", "book", "user"]

class BookRequestCreateSerializer(serializers.ModelSerializer):
    """Serializer for the BookRequest model"""

    class Meta:
        """Configuration class defining the model and fields to include"""

        model = BookRequest
        fields = ["id", "status", "requested_date", "issued_date", "returned_date", "book", "user"]


class TicketSerializer(serializers.ModelSerializer):
    """Serializer for the Ticket model"""

    class Meta:
        """Configuration class defining the model and fields to include"""

        model = Ticket
        fields = ["id", "request_message", "response_message", "status", "user"]
