""" Management command to import books reading """
import csv

from django.core.management.base import BaseCommand

from library_app.models import Author, Book
from library_app.utils import BookAttribute


class Command(BaseCommand):
    """Command to import books from CSV file"""

    def add_arguments(self, parser):
        """Read adnd store csv file name from command line"""

        parser.add_argument("file_name", type=str, help="Path to the CSV file")

    def handle(self, *args, **kwargs):
        """Open and read file and store books in Database"""

        file_name = kwargs["file_name"]
        with open(file_name, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            books = [rc for rc in reader if self.is_valid_record(rc)]
            Book.objects.bulk_create(books)

            self.stdout.write(self.style.SUCCESS("Successfully imported books"))

    def is_valid_record(self, record):
        """
        Check Book record is valid or not

        Args:
            record: dictionary object to check validity

        Returns:
            boolean: true if the record  is valid otherwise false
        """

        return all(record.get(attr) for attr in BookAttribute)

    def create_object(self, record):
        """
        Creates object of Book of corresponding record

        Args:
            record: dictionary object to create object

        Returns:
            Book object of that record
        """
        return Book.objects.create(
            name=record[BookAttribute.NAME],
            image=record[BookAttribute.IMAGE],
            publisher=record[BookAttribute.PUBLISHER],
            inventory=record[BookAttribute.INVENTORY],
            author_name=Author.objects.filter(name=record[BookAttribute.AUTHOR_NAME]),
        )
