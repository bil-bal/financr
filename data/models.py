from django.db import models
from django.contrib.auth.models import User, auth

# Create your models here.

class Expense(models.Model):
    objects = models.Manager()
    date = models.DateField()
    category = models.TextField(max_length = 20)
    price_b = models.BinaryField(max_length = 150)
    notes = models.TextField(max_length = 100, default="-")
    user = models.ForeignKey(User, on_delete = models.CASCADE)

class Category(models.Model):
    objects = models.Manager()
    cat = models.TextField(max_length = 15)
    user = models.ForeignKey(User, on_delete = models.CASCADE)

class Monthly(models.Model):
    objects = models.Manager()
    monthly = models.BinaryField(max_length = 150)
    user = models.ForeignKey(User, on_delete = models.CASCADE)