from django.contrib import admin
from .models import Customer, DeliveryPerson, CustomUser

# Register your models here.

admin.site.register(Customer)
admin.site.register(DeliveryPerson)
admin.site.register(CustomUser)