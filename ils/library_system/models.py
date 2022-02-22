from django.db import models

from django.forms import ModelForm, Textarea
# Create your models here.


class Book:
    id: int
    title: str
    author: str
    category: str
    publisher: str
    publication_year: int
    borrower_id: int
    due_date: int
    reserver_id: int


class User(models.Model):
    user_id = models.CharField(max_length=45)
    user_password = models.CharField(max_length=45)


class Meta:
    db_table = "user"
