"""Helper functions for application"""
from enum import Enum


class BookAttribute(Enum):
    """Enum for Book Attribute"""

    NAME = "name"
    IMAGE = "image"
    PUBLISHER = "publisher"
    INVENTORY = "inventory"
    AUTHOR_NAME = "author_name"
