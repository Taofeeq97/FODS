from random import choice
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render, redirect
from django.urls import reverse, reverse_lazy
from django.views import View, generic
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib import messages
from django.core.mail import send_mail
from accounts.models import DeliveryPerson
from .forms import (
    DeliveryEntityForm, TagForm, OptionalItemForm, FoodCreateForm
)
from .models import (
    Food, FoodCart, OrderedFood, DeliveryEntity,
    OngoingOrder, Tag, OptionalItem, OrderedOptionalItem
)
from .documents import FoodDocument


# Create your views here.


class AdminRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser


class FoodListView(generic.ListView):
    model = Food
    template_name = 'orders/foods.html'
    context_object_name = 'foods'
    queryset = Food.active_objects.all()

    def get_queryset(self):
        queryset = super().get_queryset()
        search_query = self.request.GET.get('search_query')
        if search_query:
            search = FoodDocument.search().query("match", name=search_query)
            results = search.execute()
            food_ids = [hit.meta.id for hit in results]
            queryset = queryset.filter(id__in=food_ids)
        return queryset


def detail_view(request, pk):
    if request.method == 'POST':
        food = Food.objects.get(id=pk)
        food_quantity = int(request.POST.get('quantity'))
        optional_items = []
        optional_item_quantities = []
        ip_address = request.META.get('REMOTE_ADDR')
        for key, value in request.POST.items():
            if key.startswith('optional_item_'):
                optional_item_id = key.split('_')[-1]
                optional_item = OptionalItem.objects.get(id=optional_item_id)
                optional_items.append(optional_item)
                optional_item_quantities.append(int(value))
        if request.user.is_authenticated:
            ordered_food = OrderedFood.objects.create(
                user=request.user.customer,
                food=food,
                food_quantity=food_quantity
            )
        else:
            ordered_food = OrderedFood.objects.create(
                ip_address=ip_address,
                food=food,
                food_quantity=food_quantity
            )

        for item, quantity in zip(optional_items, optional_item_quantities):
            ordered_optional_item = OrderedOptionalItem.objects.create(
                ordered_food=ordered_food,
                optional_item=item,
                quantity=quantity
            )
        if request.user.is_authenticated:
            selected_cart = FoodCart.objects.filter(user=request.user.customer, is_checked_out=False).first()
            if selected_cart is not None:
                existing_ordered_food = selected_cart.ordered_food.filter(food=ordered_food.food).first()
                if existing_ordered_food is not None:
                    existing_ordered_food.food_quantity += ordered_food.food_quantity
                    existing_ordered_optional_items = existing_ordered_food.get_ordered_optional_items()

                    for ordered_optional_item in ordered_food.get_ordered_optional_items():
                        existing_optional_item = existing_ordered_optional_items.filter(
                            optional_item=ordered_optional_item.optional_item).first()
                        if existing_optional_item is not None:
                            existing_optional_item.quantity += ordered_optional_item.quantity
                            existing_optional_item.save()
                        else:
                            existing_ordered_food.optional_items.add(ordered_optional_item.optional_item,
                                                                     through_defaults={
                                                                         'quantity': ordered_optional_item.quantity})
                    existing_ordered_food.save()
                    messages.success(request, f'{ordered_food} successfully added to your cart')
                    return redirect('cart')

                selected_cart.ordered_food.add(ordered_food)
                messages.success(request, f'{ordered_food} successfully addedd')
                return redirect('cart')

            new_cart = FoodCart.objects.create(user=request.user.customer)
            new_cart.ordered_food.add(ordered_food)
            new_cart.save()
            messages.success(request, f'{ordered_food} successfully added to your cart')
            return redirect('cart')

        else:
            selected_cart = FoodCart.objects.filter(ip_address=ip_address,
                                                    is_checked_out=False).first()
            if selected_cart is not None:
                existing_ordered_food = selected_cart.ordered_food.filter(food=ordered_food.food).first()
                print('yes', existing_ordered_food)
                if existing_ordered_food is not None:
                    existing_ordered_food.food_quantity += ordered_food.food_quantity
                    existing_ordered_optional_items = existing_ordered_food.get_ordered_optional_items()

                    for ordered_optional_item in ordered_food.get_ordered_optional_items():
                        existing_optional_item = existing_ordered_optional_items.filter(
                            optional_item=ordered_optional_item.optional_item).first()
                        if existing_optional_item is not None:
                            existing_optional_item.quantity += ordered_optional_item.quantity
                            existing_optional_item.save()
                        else:
                            existing_ordered_food.optional_items.add(ordered_optional_item.optional_item,
                                                                     through_defaults={
                                                                         'quantity': ordered_optional_item.quantity})

                    existing_ordered_food.save()
                    messages.success(request, f'{ordered_food} successfully added to your cart')
                    return redirect('cart')
                else:
                    selected_cart.ordered_food.add(ordered_food)
                    messages.success(request, f'{ordered_food} successfully addedd')
                    return redirect('cart')
            else:
                new_cart = FoodCart.objects.create(ip_address=ip_address)
                new_cart.ordered_food.add(ordered_food)
                new_cart.save()
                messages.success(request, f'{ordered_food} successfully added to your cart')
                return redirect('cart')

    else:
        food = Food.objects.get(id=pk)
        optional_items = OptionalItem.objects.filter(foods=food)
        return render(request, 'orders/single-food.html', {'single_food': food, 'optional_items': optional_items})


class CartView(generic.TemplateView):
    template_name = 'orders/cart.html'
    success_url = reverse_lazy('foods')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        if self.request.user.is_authenticated:
            user = self.request.user.customer
            cart = FoodCart.objects.filter(user=user, is_checked_out=False).first()
        else:
            ip_address = self.request.META.get('REMOTE_ADDR')
            cart = FoodCart.objects.filter(ip_address=ip_address, is_checked_out=False).first()

        if cart is not None:
            cart_items = cart.ordered_food.prefetch_related('optional_items').all()

            for item in cart_items:
                item.optional_items_total_price = sum(
                    ordered_optional_item.get_total_price()
                    for ordered_optional_item in item.orderedoptionalitem_set.all()
                )

                # Filter out any optional items that are not ordered
                item.ordered_optional_items = [
                    ordered_optional_item
                    for ordered_optional_item in item.orderedoptionalitem_set.all()

                    if ordered_optional_item.quantity > 0
                ]

            context['cart_items'] = cart_items
            context['cart'] = cart
            context['total'] = cart.get_total_price()
        else:
            context['cart_items'] = []
            context['total'] = 0

        return context

    def get_success_url(self):
        user_choice = self.request.session.get('user_choice')
        cart_id = self.request.POST.get('cart_id')
        if user_choice == 'delivery':
            return reverse_lazy('delivery', kwargs={'cart_id': cart_id})
        elif user_choice == 'pickup':
            return reverse_lazy('pickup', kwargs={'cart_id': cart_id})
        else:
            messages.error(self.request, 'You have to make a choice')
            return reverse_lazy('cart')

    def post(self, request, *args, **kwargs):
        user_choice = request.POST.get('choice')
        request.session['user_choice'] = user_choice
        return HttpResponseRedirect(self.get_success_url())


class RemoveFoodCartItemView(View):
    def get(self, request, food_id, cart_id):
        if request.user.is_authenticated:
            user = request.user.customer
            cart = FoodCart.objects.filter(user=user, id=cart_id).first()
        else:
            ip_address = request.META.get('REMOTE_ADDR')
            cart = FoodCart.objects.filter(ip_address=ip_address, id=cart_id).first()

        if cart is not None:
            food_item = get_object_or_404(OrderedFood, food__id=food_id, foodcart=cart)
            food_item.delete()
            messages.info(request, f'{food_item} has been removed')

        return redirect('cart')


class DeliveryView(View):
    def get(self, request, *args, **kwargs):
        food_cart = FoodCart.objects.get(id=kwargs['cart_id'])
        context = {
            'food_cart': food_cart,
            'cart_items': food_cart.ordered_food.all(),
            'total': sum([cart_item.get_total_price() for cart_item in food_cart.ordered_food.all()])
        }
        return render(request, 'orders/delivery.html', context)

    def post(self, request, *args, **kwargs):
        address = request.POST.get('address')
        city = request.POST.get('city').lower()
        phone_number = request.POST.get('phone_number')
        if city != 'ibadan':
            messages.error(request, 'Sorry, we do not deliver outside of Ibadan.')
            return redirect('cart')
        if request.user.is_authenticated:
            delivery_entity = DeliveryEntity.objects.create(
                food_cart=FoodCart.objects.get(id=kwargs['cart_id']),
                owner=request.user.customer,
                address=address,
                phone_number=request.user.phone_number
            )
            food_cart = delivery_entity.food_cart
            food_cart.is_checked_out = True
            food_cart.save()
            messages.success(request,
                             f'Thank you for your Patronage, Here is your {delivery_entity} you will be allocated a driver when the order is accepted')
        else:
            delivery_entity = DeliveryEntity.objects.create(
                food_cart=FoodCart.objects.get(id=kwargs['cart_id']),
                ip_address=request.META.get('REMOTE_ADDR'),
                address=address,
                phone_number=phone_number
            )
            food_cart = delivery_entity.food_cart
            food_cart.is_checked_out = True
            food_cart.save()
            messages.success(request,
                             f'Thank you for your Patronage, you will be allocated a driver when the order is accepted')
        return redirect(reverse_lazy('order_confirmation', kwargs={'pk': delivery_entity.id}))


class PickupView(View):
    def get(self, request, *args, **kwargs):
        food_cart = FoodCart.objects.get(id=kwargs['cart_id'])
        context = {
            'food_cart': food_cart,
            'cart_items': food_cart.ordered_food.all(),
            'total': sum([cart_item.get_total_price() for cart_item in food_cart.ordered_food.all()])
        }
        return render(request, 'orders/pickup.html', context)
    def post(self, request, *args, **kwargs):
        phone_number = request.POST.get('phone_number')
        pickup_entity = DeliveryEntity.objects.create(
            food_cart=FoodCart.objects.get(id=kwargs['cart_id']),
            phone_number=phone_number,
            owner=request.user.customer
        )

        food_cart = pickup_entity.food_cart
        food_cart.is_checked_out = True
        pickup_entity.is_active = False
        food_cart.save()
        messages.success(request, f'Thank you for your patronage! Your order will be ready for pickup.')
        return redirect(reverse_lazy('foods'))


class OrderConfirmationView(generic.DetailView):
    model = DeliveryEntity
    template_name = 'orders/order_confirmation.html'
    context_object_name = 'delivery_entity'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        delivery_entity = self.get_object()
        cart_items = delivery_entity.food_cart.ordered_food.all()
        total = sum([cart_item.get_total_price() for cart_item in cart_items])
        context.update({
            'cart_items': cart_items,
            'total': total,
        })
        return context


class UserDashboardView(View):
    template_name = 'orders/user_dashboard.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            active_delivery_entity = DeliveryEntity.objects.filter(owner=request.user.customer, is_active=True).first()
        else:
            active_delivery_entity = DeliveryEntity.objects.filter(ip_address=request.META.get('REMOTE_ADDR'),
                                                                   is_active=True).first()
        context = {
            'active_delivery_entity': active_delivery_entity
        }
        return render(request, self.template_name, context)

    def post(self, request, *args, **kwargs):
        delivery_entity_id = request.POST.get('delivery_entity_id')
        delivery_entity = get_object_or_404(DeliveryEntity, id=delivery_entity_id)
        if delivery_entity.is_accepted and delivery_entity.ongoing_status:
            delivery_entity.accept_delivery = True
            delivery_entity.is_active = False
            delivery_entity.save()
            messages.success(request, f'Order for {delivery_entity.food_cart} has been accepted.')
        else:
            messages.error(request, 'Cannot accept delivery entity at this time.')
        return redirect('user-dashboard')


class FoodCreateView(AdminRequiredMixin, SuccessMessageMixin, generic.CreateView):
    model = Food
    # fields = ['name', 'description', 'tags', 'price', 'optional_items', 'picture', 'is_active']
    form_class = FoodCreateForm
    template_name = 'orders/create-food-form.html'
    success_url = reverse_lazy('admin-list')
    success_message = "Food created successfully."


class CreateFoodTagView(AdminRequiredMixin, SuccessMessageMixin, generic.CreateView):
    model = Tag
    form_class = TagForm
    template_name = 'orders/create-optionalitem-form.html'
    success_url = reverse_lazy('admin-list')
    success_message = "Tags created successfully."


class CreateFoodOptionalItemView(AdminRequiredMixin, SuccessMessageMixin, generic.CreateView):
    model = OptionalItem
    form_class = OptionalItemForm
    template_name = 'orders/create-optionalitem-form.html'
    success_url = reverse_lazy('admin-list')
    success_message = "Optional Item created successfully."


class FoodAdminListView(AdminRequiredMixin, generic.ListView):
    model = Food
    template_name = 'orders/food_admin_list.html'

    def post(self, request, *args, **kwargs):
        food_id = request.POST.get('food_id')
        food = Food.objects.get(id=food_id)
        food.is_active = not food.is_active
        food.save()
        messages.info(request, f'Food status has been changed to {food.is_active}')
        return HttpResponseRedirect(reverse('admin-list'))


class AdminOrderManagementView(AdminRequiredMixin, generic.ListView):
    model = DeliveryEntity
    context_object_name = 'delivery_entity_list'
    template_name = 'orders/order_management_list.html'

    def post(self, request, *args, **kwargs):
        delivery_entity_id = request.POST.get('delivery_entity_id')
        delivery_entity = get_object_or_404(DeliveryEntity, id=delivery_entity_id)
        delivery_entity.is_accepted = not delivery_entity.is_accepted
        messages.info(request, f'Delivery entity status has been changed to {delivery_entity.is_accepted}')
        if delivery_entity.is_accepted:
            delivery_persons = DeliveryPerson.objects.filter(is_available=True, is_accepted=True)
            ongoing_order = OngoingOrder.objects.create(
                delivery_entity=delivery_entity
            )
            ongoing_order.save()
            delivery_entity.ongoing_status = True
            ongoing_order.save()
            delivery_entity.save()
            if delivery_persons.exists():
                delivery_entity.delivery_person = choice(delivery_persons)
            else:
                delivery_entity.delivery_person = None
        else:
            delivery_entity.delivery_person = None
        delivery_entity.save()
        return HttpResponseRedirect('admin_order_management')


class ProfileView(LoginRequiredMixin, generic.TemplateView):
    template_name = 'orders/profile.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        customer = user.customer
        orders = DeliveryEntity.objects.filter(owner=customer, is_accepted=True)
        context['user'] = user
        context['customer'] = customer
        context['orders'] = orders
        return context


class DeliveryEntityCreateView(AdminRequiredMixin, SuccessMessageMixin, generic.CreateView):
    model = DeliveryEntity
    form_class = DeliveryEntityForm
    template_name = 'orders/create_delivery_entity.html'
    success_url = reverse_lazy('admin_order_management')
    success_message = 'delivery entity created successfully'


class DeliveryEntityUpdateView(AdminRequiredMixin, SuccessMessageMixin, generic.UpdateView):
    model = DeliveryEntity
    form_class = DeliveryEntityForm
    queryset = DeliveryEntity.active_objects.all()
    template_name = 'orders/update_delivery_entity.html'
    success_url = reverse_lazy('admin_order_management')
    success_message = 'Delivery Entity Updated successfully'


class DeliveryEntityDeleteView(AdminRequiredMixin, generic.DeleteView):
    model = DeliveryEntity
    success_url = reverse_lazy('admin_order_management')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        messages.info(request, 'Delivery Entity deleted successfully')
        return HttpResponseRedirect(self.get_success_url())


class OngoingOrderListView(AdminRequiredMixin, generic.ListView):
    model = OngoingOrder
    template_name = 'orders/ongoing_orders.html'
    context_object_name = 'ongoing_orders'


class OngoingOrderDetailView(AdminRequiredMixin, View):
    def get(self, request, pk):
        ongoing_order = get_object_or_404(OngoingOrder, id=pk)
        context = {'ongoing_order': ongoing_order}
        return render(request, 'orders/ongoing-order-detail.html', context)


class CancelOrderView(AdminRequiredMixin, View):
    def post(self, request, pk):
        ongoing_order = get_object_or_404(OngoingOrder, id=pk)
        cancel_reason = request.POST.get('cancel_reason', '')
        if cancel_reason:
            ongoing_order.cancel_order(cancel_reason)
            subject = 'Cancelled Food Order'
            message = f'Your ongoing Food order for {[name for name in ongoing_order.delivery_entity.food_cart.ordered_food.all()]} has been cancelled for  {cancel_reason}'
            from_email = 'otutaiwo1@gmail.com'
            recipient_list = [ongoing_order.delivery_entity.owner.user.email]
            send_mail(subject, message, from_email, recipient_list)
            ongoing_order.delivery_entity.ongoing_status = False
            ongoing_order.delivery_entity.save()
            messages.success(request, 'Ongoing Order has been cancelled successfully.')
        else:
            messages.error(request, 'Please select a cancel reason.')
        return redirect('ongoing_orders')
