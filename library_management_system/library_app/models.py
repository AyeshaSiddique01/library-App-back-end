from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class Roles(models.TextChoices):
    """
    Defining the choices of users roles.

    This class is used to define the different roles that users can have in the system.

    Choices:
        USER: A regular user.
        LIBRARIAN: A librarian who can manage the library's collection and users.
        ADMIN: An administrator who has full control over the system and can create librarian.
    """

    USER = 1, "user"
    LIBRARIAN = 2, "librarian"
    ADMIN = 3, "admin"


class GenderType(models.TextChoices):
    """
    Defining the choices of users gender.

    Choices:
        MALE: A male user.
        FEMALE: A female user.
    """

    MALE = "M", _("Male")
    FEMALE = "F", _("Female")


class RequestStatus(models.TextChoices):
    """
    Defining the choices of request status.

    This class is used to define the different status of request of user to issue book.

    Choices:
        PENDING: A user requested and librarian hasn't accepted.
        REJECTED: Librarian did not accept issue request.
        ISSUED: Librarian has accepted requested and issued book.
        RETURNED: User returned the issued book.
    """

    PENDING = "pending"
    REJECTED = "rejected"
    ISSUED = "issued"
    RETURNED = "returned"


class TicketStatus(models.TextChoices):
    """
    Defining the choices of ticket status.

    This class is used to define the different status of ticket generated by user.

    Choices:
        PENDING: A user generated ticket and librarian hasn't accepted.
        REJECTED: Librarian did not accept ticket request.
        ACCEPTED: Librarian has accepted requested and added book.
    """

    PENDING = "pending"
    REJECTED = "rejected"
    ACCEPTED = "accepted"


class Role(models.Model):
    """
    This class represents roles of user in the system

    Additional fields:
        role: A string representing the role. The valid roles are defined in the `Roles` enum.
    """

    role = models.CharField(choices=Roles.choices)


class User(AbstractUser):
    """
    This class represents a user in the system. It inherits from Django's built-in AbstractUser class.

    Additional fields:
        role: User's role which has many to many relationship with Role class.
    """

    role = models.ManyToManyField("Role")

    def has_role(self, id):
        return self.role.filter(pk=id).exists()


class Author(models.Model):
    """
    Model representing an author.

    Attributes:
        name (str): The name of the author. Required field.
        gender (str): The gender of the author. Choices are 'M' for male and 'F' for female. Defaults to male.
        email (str): The email address of the author. Unique field.
    """

    name = models.CharField(max_length=30, null=False)
    gender = models.CharField(
        max_length=1, choices=GenderType.choices, default=GenderType.MALE
    )
    email = models.EmailField(max_length=50, unique=True)

    def __str__(self):
        return self.name


def upload_to(instance, filename):
    return f'images/{filename}'


class Book(models.Model):
    """
    This class represents a book in the system.

    Attributes:
        name: The name of the book.
        image: The image of the book.
        publisher: The publisher of the book.
        inventory: The number of copies of the book in stock.
        author: The author of the book which has many to many relationship with the Author class.
    """

    name = models.CharField(max_length=50)
    image = models.ImageField(
        upload_to=upload_to, default="images/default.png")
    publisher = models.CharField(max_length=50)
    inventory = models.IntegerField(default=0)

    author = models.ManyToManyField("Author")

    def __str__(self):
        return self.name


class BookRequest(models.Model):
    """
    This class represents a requested book by users in the system.

    Attributes:
        status: The string represents status of the request. The valid status are defined in the `Status` enum.
        requested_date: The date user request for a book.
        issued_date: The date librarian accept request and issue book.
        returned_date: The date user return the book, by default it is 15 days next to issued date.
        book: The book user requests which is foreign key from the Book class.
        user: The user that requests the book which is foreign key from the User class.
    """

    status = models.CharField(choices=RequestStatus.choices)
    requested_date = models.DateField(default=timezone.now)
    issued_date = models.DateField(null=True)
    returned_date = models.DateField(null=True)

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.book.name + " issued by " + self.user.email


class Ticket(models.Model):
    """
    This class represents a request to add book by users to librarian.

    Attributes:
        request_message: The string represents request of user to add book.
        response_message: The string represents response of librarian.
        status:  The string represents status of the ticket. The valid status are defined in the `Status` enum.
        user: The user that requests to add book which is foreign key from the User class.
    """

    request_message = models.CharField(max_length=100)
    response_message = models.CharField(max_length=100, null=True)
    status = models.CharField(choices=TicketStatus.choices)

    user = models.ForeignKey(User, on_delete=models.CASCADE)
