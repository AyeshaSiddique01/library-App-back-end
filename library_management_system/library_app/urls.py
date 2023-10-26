from django.urls import include, path
from rest_framework.routers import DefaultRouter

from library_app.views import (AuthorViewSet, BooksViewSet, LibrarianViewSet,
                    BookRequestViewSet, TicketViewSet, UserViewSet, RoleViewSet, update_password)

router = DefaultRouter()
router.register(r"role", RoleViewSet, basename="role")
router.register(r"librarian", LibrarianViewSet, basename="librarian")
router.register(r"users", UserViewSet, basename="user")
router.register(r"author", AuthorViewSet, basename="author")
router.register(r"books", BooksViewSet, basename="book")
router.register(r"request_book", BookRequestViewSet, basename="book_requested")
router.register(r"tickets", TicketViewSet, basename="tickets")

urlpatterns = [
    path("", include(router.urls)),
    path('update_password/', update_password, name='update_password'),
]
