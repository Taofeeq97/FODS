from django.http import HttpResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LogoutView
from django.contrib import messages
from django.db import IntegrityError
from accounts.models import DeliveryPerson, CustomUser
from accounts.forms import (
    CustomerCreationForm, LoginForm, CustomerUpdateForm, DeliveryPersonForm
)


class CustomerAccountCreateView(generic.CreateView):
    template_name = 'orders/create_custome_account.html'
    form_class = CustomerCreationForm
    success_url = reverse_lazy('foods')

    def form_valid(self, form):
        customer = form.save(commit=False)
        user = customer.user
        try:
            login(self.request, user)
            messages.success(self.request, 'Account creation was successful')
        except IntegrityError:
            messages.info('Username or Email has already been taken')
            return self.form_invalid(form)

        return redirect(self.success_url)


class CustomLoginView(generic.FormView):
    form_class = LoginForm
    template_name = 'orders/login.html'
    success_url = reverse_lazy('foods')

    def form_valid(self, form):
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
            messages.success(self.request, 'Login Successful')
            return super().form_valid(form)
        else:
            messages.error(self.request, 'Invalid login credentials')
            return self.form_invalid(form)


class MyLogoutView(LoginRequiredMixin, LogoutView):
    next_page = reverse_lazy('foods')


class CustomerDetailsUpdateView(LoginRequiredMixin, generic.UpdateView):
    model = CustomUser
    form_class = CustomerUpdateForm
    template_name = 'orders/update_profile.html'
    success_url = reverse_lazy('profile')

    def get_object(self):
        return self.request.user

    def form_valid(self, form):
        customer = form.save(commit=False)
        customer.user = self.request.user
        customer.save()
        messages.success(self.request, 'Profile Updated successfully')
        return super(CustomerDetailsUpdateView, self).form_valid(form)


class CreateDeliveryPersonView(generic.CreateView):
    model = DeliveryPerson
    form_class = DeliveryPersonForm
    template_name = 'orders/create_delivery_person.html'
    success_url = reverse_lazy('foods')

    def form_valid(self, form):
        user = form.save()
        delivery_person = DeliveryPerson.objects.create(
            user=user,
            ride_number=form.cleaned_data.get('ride_number')
        )
        return HttpResponse('driver account created')
