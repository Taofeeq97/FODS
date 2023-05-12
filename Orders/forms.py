from django import forms
from .models import Food, DeliveryEntity, FoodCart, OrderedFood, Tag, OptionalItem


class DeliveryEntityForm(forms.ModelForm):
    foods = forms.ModelMultipleChoiceField(queryset=Food.objects.all(), required=False,
                                           widget=forms.CheckboxSelectMultiple)
    optional_items = forms.ModelMultipleChoiceField(queryset=OptionalItem.objects.all(), required=False,
                                                    widget=forms.CheckboxSelectMultiple)

    class Meta:
        model = DeliveryEntity
        fields = ['owner', 'delivery_person', 'address', 'is_accepted']

    def __init__(self, *args, **kwargs):
        super(DeliveryEntityForm, self).__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

    def save(self, commit=True):
        delivery_entity = super().save(commit=commit)
        owner = self.cleaned_data.get('owner')
        delivery_person = self.cleaned_data.get('delivery_person')
        address = self.cleaned_data.get('address')
        foods = self.cleaned_data.get('foods')
        optional_items = self.cleaned_data.get('optional_items')

        ordered_foods = []
        for food in foods:
            ordered_food = OrderedFood.objects.create(
                user=owner,
                food=food,
            )
            ordered_foods.append(ordered_food)

        food_cart = FoodCart.objects.create(
            user=owner,
        )
        food_cart.ordered_food.set(ordered_foods)

        delivery_entity.food_cart = food_cart
        delivery_entity.owner = owner
        delivery_entity.address = address
        delivery_entity.delivery_person = delivery_person

        if commit:
            delivery_entity.save()

        return delivery_entity


class FoodCreateForm(forms.ModelForm):
    tags = forms.ModelMultipleChoiceField(
        queryset=Tag.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'input'}),
    )

    optional_items = forms.ModelMultipleChoiceField(
        queryset=OptionalItem.objects.all(),
        widget=forms.SelectMultiple(attrs={'class': 'input'}),
    )

    class Meta:
        model = Food
        fields = ['name', 'description', 'tags', 'price', 'optional_items', 'picture', 'is_active']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input'}),
            'description': forms.Textarea(attrs={'class': 'input'}),
            'price': forms.NumberInput(attrs={'class': 'input'}),
            'picture': forms.ClearableFileInput(attrs={'class': 'input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'input'}),
        }


class OptionalItemForm(forms.ModelForm):
    class Meta:
        model = OptionalItem
        fields = ['name', 'picture', 'price']

    def __init__(self, *args, **kwargs):
        super(OptionalItemForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})


    def clean_price(self):
        price = self.cleaned_data['price']
        try:
            float(price)
        except ValueError:
            try:
                int(price)
            except ValueError:
                raise forms.ValidationError("Please enter a valid price.")
        return price


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag
        fields = ['name']

    def __init__(self, *args, **kwargs):
        super(TagForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})
