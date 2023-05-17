from django.db import models
from django.urls import reverse
from accounts.models import DeliveryPerson, Customer


class IsActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True)


class Tag(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Food(models.Model):
    name = models.CharField(max_length=225)
    description = models.TextField()
    tags = models.ManyToManyField(Tag)
    price = models.FloatField(default=0.00)
    optional_items = models.ManyToManyField('OptionalItem', related_name='foods')
    picture = models.ImageField(upload_to='media')
    is_active = models.BooleanField(default=True)

    objects = models.Manager()
    active_objects = IsActiveManager()

    def get_absolute_url(self):
        return reverse('food_detail', args=[str(self.pk)])

    def __str__(self):
        return self.name


class OptionalItem(models.Model):
    name = models.CharField(max_length=225)
    picture = models.ImageField(upload_to='media', blank=True, null=True)
    price = models.FloatField(default=0.00)

    def __str__(self):
        return self.name


class OrderedFood(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    session_id = models.CharField(max_length=500, blank=True, null=True)
    food = models.ForeignKey(Food, on_delete=models.CASCADE)
    optional_items = models.ManyToManyField(OptionalItem, through='OrderedOptionalItem')
    food_quantity = models.IntegerField(default=1, blank=True, null=True)
    created = models.DateField(auto_now_add=True, null=True, blank=True)
    updated = models.DateField(auto_now=True, null=True, blank=True)

    def get_ordered_optional_items(self):
        return self.orderedoptionalitem_set.all()

    @property
    def get_ordered_optional_items_name(self):
        return [item.optional_item.name for item in self.orderedoptionalitem_set.all() if item.quantity > 0]

    def get_total_price(self):
        food_price = self.food.price * self.food_quantity

        optional_items_price = sum(
            item.price * ordered_item.quantity
            for ordered_item in self.orderedoptionalitem_set.all()
            for item in (ordered_item.optional_item.all() if hasattr(ordered_item.optional_item, 'all') else [
                ordered_item.optional_item])
        )
        return food_price + optional_items_price

    def __str__(self):
        return f'{self.food}'


class OrderedOptionalItem(models.Model):
    ordered_food = models.ForeignKey(OrderedFood, on_delete=models.CASCADE)
    optional_item = models.ForeignKey(OptionalItem, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    created = models.DateField(auto_now_add=True, null=True, blank=True)
    updated = models.DateField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return f'{self.quantity} {self.optional_item.name} for food: {self.ordered_food.food.name} by {self.ordered_food.user}'

    def get_total_price(self):
        return self.optional_item.price * self.quantity


class FoodCart(models.Model):
    user = models.ForeignKey(Customer, on_delete=models.CASCADE, blank=True, null=True)
    session_id = models.CharField(max_length=500, blank=True, null=True)
    ordered_food = models.ManyToManyField(OrderedFood, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)
    date_checked_out = models.DateTimeField(null=True, blank=True)
    is_checked_out = models.BooleanField(default=False)
    created = models.DateField(auto_now_add=True, null=True, blank=True)
    updated = models.DateField(auto_now=True, null=True, blank=True)


    # def cart_number_of_items(self):
    #     return self.ordered_food.count()

    def get_total_price(self):
        total_price = sum(ordered_food.get_total_price() for ordered_food in self.ordered_food.all())
        return total_price

    def __str__(self):
        return f"{self.user}'s cart for {self.ordered_food.all()}"


class DeliveryEntity(models.Model):
    food_cart = models.ForeignKey(FoodCart, on_delete=models.CASCADE, blank=True, null=True)
    session_id = models.CharField(max_length=500, blank=True,null=True)
    phone_number = models.CharField(max_length=20, null=True, blank=True)
    owner = models.ForeignKey(Customer, on_delete=models.CASCADE, null=True, blank=True)
    delivery_person = models.ForeignKey(DeliveryPerson, on_delete=models.SET_NULL, null=True, blank=True)
    address = models.CharField(max_length=500)
    is_active = models.BooleanField(default=True)
    ongoing_status = models.BooleanField(default=False)
    is_accepted = models.BooleanField(default=False)
    accept_delivery = models.BooleanField(default=False)
    created = models.DateField(auto_now_add=True, null=True, blank=True)
    updated = models.DateField(auto_now=True, null=True, blank=True)

    objects = models.Manager()
    active_objects = IsActiveManager()

    class Meta:
        ordering = ['-created']

    def __str__(self):
        if self.owner:
            return f"{self.owner.user.username}'s delivery entity for {[ordered_food.food.name for ordered_food in self.food_cart.ordered_food.all()]}"
        else:
            return f"{self.session_id}'s delivery entity for {[ordered_food.food.name for ordered_food in self.food_cart.ordered_food.all()]}"


class OngoingOrder(models.Model):
    LOCATION_ISSUES = 'LOCATION ISSUES'
    DELIVERY_ISSUES = 'DELIVERY ISSUES'
    FOOD_ISSUES = 'FOOD ISSUES'
    OTHER = 'OTHER'
    CANCEL_REASON_CHOICES = [
        (LOCATION_ISSUES, 'Location Issues'),
        (DELIVERY_ISSUES, 'Delivery Issues'),
        (FOOD_ISSUES, 'Food Issues'),
        (OTHER, 'Other'),
    ]

    delivery_entity = models.OneToOneField(DeliveryEntity, on_delete=models.CASCADE, null=True, blank=True)
    is_cancelled = models.BooleanField(default=False)
    cancel_reason = models.CharField(max_length=50, choices=CANCEL_REASON_CHOICES, blank=True)
    created = models.DateField(auto_now_add=True, null=True, blank=True)
    updated = models.DateField(auto_now=True, null=True, blank=True)

    class Meta:
        ordering = ['-created']

    def cancel_order(self, reason=''):
        if not self.is_cancelled:
            self.is_cancelled = True
            self.cancel_reason = reason
            self.save()

    def __str__(self):
        return f"OngoingOrder for {self.delivery_entity}"


# class SelectedLocation(models.Model):
#     location = models.Po
#
#     def __str__(self):
#         return self.location
