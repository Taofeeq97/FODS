from django.core.exceptions import ValidationError
from django import forms
from .models import Customer, CustomUser, DeliveryPerson
from django.contrib.auth import get_user_model


class CustomerCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email', 'address', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(CustomerCreationForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Email has already been taken, try a more unique one")
        return email

    def clean_username(self):
        username = self.cleaned_data['username']
        if CustomUser.objects.filter(username=username).exists():
            raise forms.ValidationError("Username has already been taken.")
        return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if len(phone_number) <= 11 or not phone_number.isnumeric():
            raise forms.ValidationError("Please enter a valid 10-digit phone number.")
        return phone_number

    def clean_confirm_password(self):
        password = self.cleaned_data.get('password')
        confirm_password = self.cleaned_data.get('confirm_password')
        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return confirm_password

    def save(self, commit=True):
        user = CustomUser.objects.create_user(
            username=self.cleaned_data['username'],
            password=self.cleaned_data['password'],
            email=self.cleaned_data['email'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name'],
            address=self.cleaned_data['address'],
            phone_number=self.cleaned_data['phone_number']
        )
        customer = Customer.objects.create(
            user=user,
        )
        customer.save()
        return customer


class CustomerUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'username', 'email', 'address', 'phone_number')

    def __init__(self, *args, **kwargs):
        super(CustomerUpdateForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

    # def clean_email(self):
    #     email = self.cleaned_data['email']
    #     if CustomUser.objects.filter(email=email).exists():
    #         raise forms.ValidationError("Email has been taken.")
    #     return email
    #
    # def clean_username(self):
    #     username = self.cleaned_data['username']
    #     if CustomUser.objects.filter(username=username).exists():
    #         raise forms.ValidationError("Username has been taken")
    #     return username

    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if len(phone_number) <= 11 or not phone_number.isnumeric():
            raise forms.ValidationError("Please enter a valid 10-digit phone number.")
        return phone_number

    def save(self, commit=True):
        user = super().save(commit=False)
        user.address = self.cleaned_data['address']
        user.phone_number = self.cleaned_data['phone_number']
        user.save()
        return user


class LoginForm(forms.Form):
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'input input--text', 'placeholder': 'Enter your username...'}))
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'input input--password', 'placeholder': '••••••••'}))


class DeliveryPersonForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    ride_number = forms.CharField(widget=forms.TextInput)

    class Meta:
        model = CustomUser
        fields = ['username', 'password', 'email', 'address', 'phone_number', 'ride_number']

    def __init__(self, *args, **kwargs):
        super(DeliveryPersonForm, self).__init__(*args, **kwargs)

        for name, field in self.fields.items():
            field.widget.attrs.update({'class': 'input'})

    def clean_username(self):
        username = self.cleaned_data.get('username')
        User = get_user_model()

        if User.objects.filter(username=username).exists():
            raise ValidationError("This username is already taken.")

        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        User = get_user_model()

        if User.objects.filter(email=email).exists():
            raise ValidationError("This email is already taken.")

        return email
