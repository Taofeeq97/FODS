from django.contrib import admin
from .models import Food, OptionalItem, Tag,FoodCart,OrderedFood, DeliveryEntity, OngoingOrder, OrderedOptionalItem

# Register your models here.

admin.site.register(Food)
admin.site.register(OptionalItem)
admin.site.register(Tag)
admin.site.register(FoodCart)
admin.site.register(OrderedOptionalItem)
admin.site.register(DeliveryEntity)
admin.site.register(OngoingOrder)
admin.site.register(OrderedFood)

