from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.

class CustomUser(AbstractUser):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    username = models.CharField(max_length=200, unique=True)
    email = models.EmailField()
    address = models.CharField(max_length=200, blank=True, null=True)
    phone_number = models.CharField(max_length=200, null=True, blank=True)


class Customer(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.email


class DeliveryPerson(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    is_accepted=models.BooleanField(default=False)
    is_available=models.BooleanField(default=True)
    ride_number = models.CharField(max_length=20)


    def __str__(self):
        return f'Name: {self.user.username}  ,Phone Number: {self.user.phone_number}  , Ride Number: {self.ride_number}'
