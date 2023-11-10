from datetime import datetime, timedelta, timezone

from django.contrib.auth.hashers import make_password
from django.db.models import F, Q
from django.utils import timezone
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from library_app.decorators import setup_eager_loading
from library_app.models import (Author, Book, BookRequest, RequestStatus, Role,
                                Roles, Ticket, TicketStatus, User)
from library_app.permissions import (BookPermission, IsAdmin, IsLibrarian,
                                     RequestPermission, UserHandlePermission)
from library_app.serializer import (AuthorSerializer, BookCreateSerializer,
                                    BookRequestCreateSerializer,
                                    BookRequestViewSerializer,
                                    BookViewSerializer, RoleSerializer,
                                    TicketSerializer, UserSerializer)
from library_app.tasks.send_book_request import send_request_book_mail
from library_app.tasks.send_ticket import send_ticket_mail
from library_app.tasks.update_status import send_update_status_mail


class UserViewSet(viewsets.ModelViewSet):
    """
    A viewset for handling User-related actions such as creating, retrieving,
    updating, and destroying User instances.

    Attributes:
        permission_classes (list): A list of permission classes that control
            access to the viewset.
        serializer_class (Serializer): The serializer class responsible for
            converting User objects to JSON and vice versa.

    Methods:
        get_queryset(self): Get a filtered queryset of User objects based on
            the current user.
        create(self, request, *args, **kwargs): Handle POST requests to create
            new User instances, including user role assignment and password
            hashing.

    """

    permission_classes = [UserHandlePermission]
    serializer_class = UserSerializer

    @setup_eager_loading
    def get_queryset(self):
        user = self.request.user
        return User.objects.filter(username=user.username)

    def create(self, request, *args, **kwargs):
        """
        Handle POST requests to create a new user and perform necessary
        operations such as role assignment and password hashing.

        Args:
            request (HttpRequest): The HTTP request object containing user
                data in the request body.

        Returns:
            Response: A response object with a success message and a status
            code of 201 (Created) upon successful signup. If the provided data
            is invalid, a response with error details and a status code of 400
            (Bad Request) will be returned.

        """

        data = request.data
        user = {}
        user["username"] = data["username"]
        user["email"] = data["email"]
        user["role"] = [Roles.USER]
        user["password"] = make_password(data["password"])
        serializer = UserSerializer(data=user)

        if serializer.is_valid(raise_exception=True):
            user = serializer.save()
            return Response(
                {"message": "Sigup successfully"}, status=status.HTTP_201_CREATED
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def update_password(request):
    """
    Handle POST requests to partial_update a user of any role and perform necessary
    operations such as password hashing.

    Args:
        request (HttpRequest): The HTTP request object containing user
            data in the request body.

    Returns:
        Response: A response object with a success message and a status
        code of 201 (Created) upon successful update.

    """
    data = request.data
    password = make_password(data["password"])
    user = User.objects.select_related("role").filter(username=data["username"])
    if user:
        user.update(password=password)
        return Response(
            {"message": "Updated successfully"}, status=status.HTTP_201_CREATED
        )
    return Response(
        {"error": "User not found"},
        status=status.HTTP_203_NON_AUTHORITATIVE_INFORMATION,
    )


@api_view(["GET"])
def get_user_role(request):
    """
    Handle GET requests to get roles of logged in user.
    Args:
        request (HttpRequest): The HTTP request object containing user
            data in the request body.

    Returns:
        roles: Roles of user.

    """
    user = request.user
    if user.is_authenticated:
        roles = user.role.all()
        if len(roles) == 0:
            role_names = ["admin"]
            return Response(role_names)

        roles_name = ["user", "librarian", "admin"]
        role_names = [roles_name[int(role.role) - 1] for role in roles]
        return Response(role_names)

    return Response([])


class LibrarianViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing Librarian resources, including listing, creating,
    retrieving, updating, and deleting Librarian instances.

    Attributes:
        permission_classes (list): A list of permission classes that restrict
            access to administrators only.
        serializer_class (Serializer): The serializer class responsible for
            converting Librarian objects to JSON and vice versa.

    Methods:
        get_queryset(self): Get a filtered queryset of User objects with the
            'Librarian' role.
        create(self, request, *args, **kwargs): Handle POST requests to create
            a new Librarian instance, including role assignment and password
            hashing.

    """

    permission_classes = [IsAdmin]
    serializer_class = UserSerializer

    @setup_eager_loading
    def get_queryset(self):
        """
        Get a queryset of Librarian instances based on their 'Librarian' role.

        Returns:
            QuerySet: A filtered queryset containing Librarian objects.
        """
        return User.objects.filter(role=Roles.LIBRARIAN)

    def create(self, request, *args, **kwargs):
        """
        Handle POST requests to add a new librarian, including role assignment
        and password hashing.

        Args:
            request (HttpRequest): The HTTP request object containing librarian
                data in the request body.

        Returns:
            Response: A response object with a success message and a status
            code of 201 (Created) upon successful librarian addition. If the
            provided data is invalid, a response with error details and a
            status code of 400 (Bad Request) will be returned.

        """
        data = request.data
        librarian = {}
        librarian["username"] = data["username"]
        librarian["email"] = data["email"]
        librarian["role"] = [Roles.LIBRARIAN]
        librarian["password"] = make_password(data["password"])
        serializer = UserSerializer(data=librarian)

        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(
                {"message": "Librarian added successfully"},
                status=status.HTTP_201_CREATED,
            )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoleViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing Role resources, including listing, creating,
    retrieving, updating, and deleting Role instances.

    Attributes:
        queryset (QuerySet): The queryset containing all Role instances.
        permission_classes (list): A list of permission classes that restrict
            access to administrators only.
        serializer_class (Serializer): The serializer class responsible for
            converting Role objects to JSON and vice versa.

    """

    queryset = Role.objects.all()
    permission_classes = [IsAdmin]
    serializer_class = RoleSerializer


class AuthorViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing Author resources, including listing, creating,
    retrieving, updating, and deleting Author instances.

    Attributes:
        queryset (QuerySet): The queryset containing all Author instances.
        permission_classes (list): A list of permission classes that restrict
            access to librarians only.
        serializer_class (Serializer): The serializer class responsible for
            converting Author objects to JSON and vice versa.

    """

    queryset = Author.objects.all()
    permission_classes = [IsLibrarian]
    serializer_class = AuthorSerializer


class BooksViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing Book resources, including listing, creating,
    retrieving, updating, and deleting Book instances.

    Attributes:
        search_fields (list): A list of fields on which search queries can
            be performed when filtering books.
        filter_backends (tuple): A tuple of filter backend classes used to
            filter the list of books, with 'SearchFilter' as the primary
            filter backend.
        queryset (QuerySet): The queryset containing all Book instances.
        serializer_class (Serializer): The serializer class responsible for
            converting Book objects to JSON and vice versa.
        permission_classes (list): A list of permission classes that control
            access to the viewset, with 'BookPermission' for custom access
            control.

    """

    search_fields = ["name"]
    filter_backends = (filters.SearchFilter,)
    serializer_class = BookViewSerializer
    permission_classes = [BookPermission]
    parser_classes = (MultiPartParser, FormParser)

    @setup_eager_loading
    def get_queryset(self):
        return Book.objects.all()

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return BookCreateSerializer
        return self.serializer_class


class TicketViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing Ticket resources, including listing, creating,
    retrieving, updating, and deleting Ticket instances.

    Attributes:
        permission_classes (list): A list of permission classes that control
            access to the viewset, with 'RequestPermission' for custom access
            control.
        serializer_class (Serializer): The serializer class responsible for
            converting Ticket objects to JSON and vice versa.

    Methods:
        get_queryset(self): Get a filtered queryset of Ticket instances based
            on the user's role (USER or LIBRARIAN).
        create(self, request, *args, **kwargs): Handle POST requests to add a
            new ticket request by a user, including sending email notifications.
        partial_update(self, request, *args, **kwargs): Handle PATCH requests to
            update a ticket's status and response message by a librarian or
            update the ticket message by a user.

    """

    permission_classes = [RequestPermission]
    serializer_class = TicketSerializer

    @setup_eager_loading
    def get_queryset(self):
        """
        Get a queryset of Ticket instances based on the user's role.

        If the user has the role 'USER', return tickets associated with that
        user. Otherwise, return all tickets.

        Returns:
            QuerySet: A filtered queryset containing Ticket objects.
        """
        user = self.request.user

        if user.has_role(Roles.USER):
            return Ticket.objects.filter(user=user)
        return Ticket.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Handle POST requests to add a new ticket request by a user, including
        sending email notifications.

        Args:
            request (HttpRequest): The HTTP request object containing the ticket
                request data in the request body.

        Returns:
            Response: A response object with a success message and a status
            code of 201 (Created) upon successful ticket generation. If the
            request message is missing, a response with an error message and
            a status code of 403 (Forbidden) will be returned.

        """
        if not request.data.get("request_message"):
            return Response(
                {"message": "Request message should not be null"},
                status=status.HTTP_403_FORBIDDEN,
            )

        request_message = request.data["request_message"]
        user = request.user
        ticket = Ticket(
            request_message=request_message,
            status=TicketStatus.PENDING,
            user=user,
        )

        send_ticket_mail(ticket, user)
        ticket.save()
        return Response({"message": "Ticket generated"}, status=status.HTTP_201_CREATED)

    def partial_update(self, request, *args, **kwargs):
        """
        Handle PATCH requests to update a ticket's status and response message by
        a librarian or update the ticket message by a user.

        Args:
            request (HttpRequest): The HTTP request object containing the update
                data in the request body.

        Returns:
            Response: A response object with a success message and a status
            code of 202 (Accepted) upon successful updates. If the user is not
            authorized to update a specific field or if the field is missing,
            a response with an error message and a status code of 403 (Forbidden)
            will be returned.

        """
        data = request.data
        ticket_id = data["id"]
        ticket = Ticket.objects.get(pk=ticket_id)
        user = request.user

        if data.get("status") and user.has_role(Roles.LIBRARIAN):
            ticket.status = data["status"]
            ticket.response_message = data["response_message"]
            ticket.save()

            send_update_status_mail(ticket)
            return Response(
                {"message": "Response sent"}, status=status.HTTP_202_ACCEPTED
            )

        if data.get("request_message") and user.has_role(Roles.USER):
            ticket.request_message = data["request_message"]
            ticket.save()

            return Response(
                {"message": "Ticket message updated"}, status=status.HTTP_202_ACCEPTED
            )

        return Response(
            {"message": "You are not authorized to update that field"},
            status=status.HTTP_403_FORBIDDEN,
        )


class BookRequestViewSet(viewsets.ModelViewSet):
    """
    A viewset for managing Book Request resources, including listing,
    creating, retrieving, updating, and deleting Book Request instances.

    Attributes:
        serializer_class (Serializer): The serializer class responsible for
            converting Book Request objects to JSON and vice versa.
        permission_classes (list): A list of permission classes that control
            access to the viewset, with 'RequestPermission' for custom access
            control.

    Methods:
        get_queryset(self): Get a filtered queryset of Book Request instances
            based on the user's role (USER or LIBRARIAN).
        create(self, request, *args, **kwargs): Handle POST requests to add a
            new book request by a user, including sending email notifications.
        update(self, request, *args, **kwargs): Handle PATCH requests to update
            the status of book requests by librarians and users.

    """

    permission_classes = [RequestPermission]
    serializer_class = BookRequestViewSerializer

    def get_serializer_class(self):
        if self.action in ["create", "update", "partial_update"]:
            return BookRequestCreateSerializer
        return self.serializer_class

    @setup_eager_loading
    def get_queryset(self):
        """
        Get a queryset of Book Request instances based on the user's role.

        If the user has the role 'USER', return book requests associated with
        that user. Otherwise, return all book requests.

        Returns:
            QuerySet: A filtered queryset containing Book Request objects.
        """
        user = self.request.user
        if user.has_role(Roles.USER):
            return BookRequest.objects.filter(user=user)
        return BookRequest.objects.all()

    def create(self, request, *args, **kwargs):
        """
        Handle POST requests to add a new book request by a user, including
        sending email notifications.

        Args:
            request (HttpRequest): The HTTP request object containing the book
                request data in the request body.

        Returns:
            Response: A response object with a success message and a status
            code of 201 (Created) upon successful book request submission. If
            the request message is missing, the user has already requested three
            books, or the book is not available, a response with an appropriate
            error message and a status code of 403 (Forbidden) will be returned.

        """
        book_id = request.data["book"]
        book = Book.objects.get(pk=book_id)

        user = request.user
        user_issued_books = BookRequest.objects.filter(
            Q(user=user) & Q(status=RequestStatus.ISSUED)
        )

        if len(user_issued_books) >= 3:
            return Response(
                {"message": "You have already requested 3 books"},
                status=status.HTTP_403_FORBIDDEN,
            )

        if book.inventory <= 0:
            return Response(
                {"message": "The book is not available"},
                status=status.HTTP_403_FORBIDDEN,
            )

        requested_book = BookRequest(
            book=book,
            user=user,
            requested_date=datetime.now().date(),
            status=RequestStatus.PENDING,
        )

        send_request_book_mail(book, user)
        requested_book.save()

        return Response(
            BookRequestViewSerializer(requested_book).data,
            status=status.HTTP_201_CREATED,
        )

    def partial_update(self, request, *args, **kwargs):
        """
        Handle PATCH requests to update the status of book requests by
        librarians and users.

        Args:
            request (HttpRequest): The HTTP request object containing the update
                data in the request body.

        Returns:
            Response: A response object with a success message and a status
            code of 202 (Accepted) upon successful status updates. If the request
            status is not valid or the user is not authorized to update that
            field, a response with an error message and a status code of 403
            (Forbidden) will be returned.

        """
        data = request.data
        request_id = data["id"]
        status_ = data.get("status")

        if status_ == RequestStatus.ISSUED:
            BookRequest.objects.filter(pk=request_id).update(
                issued_date=datetime.now(), status=RequestStatus.ISSUED
            )

            book = BookRequest.objects.get(pk=request_id).book
            Book.objects.filter(id=book.id).update(inventory=F("inventory") - 1)

            return Response({"message": "Book issued"}, status=status.HTTP_202_ACCEPTED)

        if status_ == RequestStatus.REJECTED:
            BookRequest.objects.filter(pk=request_id).update(
                status=RequestStatus.REJECTED
            )

            return Response(
                {"message": "Request book rejected"},
                status=status.HTTP_202_ACCEPTED,
            )

        if status_ == RequestStatus.RETURNED:
            BookRequest.objects.filter(pk=request_id).update(
                returned_date=datetime.now(), status=RequestStatus.RETURNED
            )

            book = BookRequest.objects.get(pk=request_id).book
            Book.objects.filter(id=book.id).update(inventory=F("inventory") + 1)

            return Response(
                {"message": "Request returned"}, status=status.HTTP_202_ACCEPTED
            )

        return Response(
            {"message": "Request status is not valid"}, status=status.HTTP_403_FORBIDDEN
        )
