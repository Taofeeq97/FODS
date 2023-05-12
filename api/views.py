from django.shortcuts import get_object_or_404
from django.core.mail import send_mail
from rest_framework import generics, status
from rest_framework.permissions import IsAdminUser, AllowAny, BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import (
    FoodSerializer, TagSerializer, OptionalItemsSerializer, OrderedFoodSerializer,
    FoodCartSerializer, DeliveryEntitySerializer, OngoingOrderSerializer,
    CustomerSerializer, DeliveryPersonSerializer, LoginSerializer
)
from Orders.models import (
    Food, Tag, OptionalItem, OrderedFood, FoodCart, OrderedOptionalItem, OngoingOrder,
    DeliveryEntity
)
from rest_framework.permissions import IsAuthenticated
from Orders.documents import FoodDocument


# Create your views here.

class IsOwnerOrIPMixin(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user.is_authenticated:
            return obj.owner == request.user.customer
        else:
            ip_address = request.META.get('REMOTE_ADDR')
            return obj.ip_address == ip_address


class FoodListAPIVIew(generics.ListAPIView):
    queryset = Food.active_objects.all()
    serializer_class = FoodSerializer


class DetailAPIView(generics.RetrieveAPIView):
    serializer_class = FoodSerializer
    queryset = Food.active_objects.all()
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return self.retrieve(request, *args, **kwargs)

    def post(self, request, pk):
        food = Food.objects.get(id=pk)
        food_quantity = int(request.data.get('quantity'))
        optional_items = []
        optional_item_quantities = []
        ip_address = request.META.get('REMOTE_ADDR')
        for key, value in request.data.items():
            if key.startswith('optional_item_'):
                optional_item_id = key.split('_')[-1]
                optional_item = OptionalItem.objects.get(id=optional_item_id)
                optional_items.append(optional_item)
                optional_item_quantities.append(int(value))

        ordered_food_kwargs = {
            'food': food,
            'food_quantity': food_quantity,
        }
        if request.user.is_authenticated:
            ordered_food_kwargs['user'] = request.user.customer
        else:
            ordered_food_kwargs['ip_address'] = ip_address

        ordered_food = OrderedFood.objects.create(**ordered_food_kwargs)

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
                    return Response({'message': f'{ordered_food} successfully added to your cart'},
                                    status=status.HTTP_201_CREATED)

                selected_cart.ordered_food.add(ordered_food)
                return Response({'message': f'{ordered_food} successfully added'}, status=status.HTTP_201_CREATED)

            new_cart = FoodCart.objects.create(user=request.user.customer)
            new_cart.ordered_food.add(ordered_food)
            new_cart.save()
            return Response({'message': f'{ordered_food} successfully added to your cart'},
                            status=status.HTTP_201_CREATED)
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
                    return Response({'message': f'{ordered_food} successfully added to your cart'},
                                    status=status.HTTP_201_CREATED)
                else:
                    selected_cart.ordered_food.add(ordered_food)
                    return Response({'message': f'{ordered_food} successfully added to your cart'},
                                    status=status.HTTP_201_CREATED)
            else:
                new_cart = FoodCart.objects.create(ip_address=ip_address)
                new_cart.ordered_food.add(ordered_food)
                new_cart.save()
                return Response({'message': f'{ordered_food} successfully added to your cart'},
                                status=status.HTTP_201_CREATED)


class FoodListCreateUpdateDeleteAPIView(generics.ListAPIView, generics.CreateAPIView, generics.UpdateAPIView,
                                        generics.DestroyAPIView):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    permission_classes = [IsAdminUser]


class TagListAPIview(generics.ListAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser]


class TagDetailUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [IsAdminUser]


class OptionalItemListAPIView(generics.ListAPIView):
    queryset = OptionalItem.objects.all()
    serializer_class = OptionalItemsSerializer
    permission_classes = [IsAdminUser]


class OptionalItemDetailUpdateDeleteAPIView(generics.RetrieveUpdateDestroyAPIView):
    queryset = OptionalItem.objects.all()
    serializer_class = OptionalItemsSerializer
    permission_classes = [IsAdminUser]


class OrderedFoodCreateAPIView(generics.CreateAPIView):
    queryset = OrderedFood.objects.all()
    serializer_class = OrderedFoodSerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save(ip_address=self.request.META('REMOTE ADDRS', None))


class FoodCartAPIView(IsOwnerOrIPMixin, generics.RetrieveAPIView):
    queryset = FoodCart.objects.all()
    serializer_class = FoodCartSerializer

    def get_object(self):
        if self.request.user.is_authenticated:
            user = self.request.user.customer
            cart = FoodCart.objects.filter(user=user, is_checked_out=False).first()
            print('user is authenticated')
        else:
            ip_address = self.request.META.get('REMOTE_ADDR')
            cart = FoodCart.objects.filter(ip_address=ip_address, is_checked_out=False).first()
            print('user is not authenticated')

        if cart is None:
            return Response({'message': "Cart not found"}, status=status.HTTP_404_NOT_FOUND)
        return cart


class RemoveFoodCartItemAPIView(IsOwnerOrIPMixin, generics.DestroyAPIView):
    queryset = OrderedFood.objects.all()
    serializer_class = OrderedFoodSerializer

    def delete(self, request, ordered_food_id):
        ordered_food = get_object_or_404(OrderedFood, id=ordered_food_id)
        ordered_food.delete()
        return Response({'message': f'{ordered_food} has been removed'}, status=status.HTTP_200_OK)


class PlaceFoodOrderAPIView(IsOwnerOrIPMixin, generics.CreateAPIView):
    queryset = DeliveryEntity.objects.all()
    serializer_class = DeliveryEntitySerializer

    def perform_create(self, serializer):
        food_cart = get_object_or_404(FoodCart, id=self.kwargs.get('food_cart_id'))
        if self.request.user.is_authenticated:
            owner = self.request.user.customer
            phone_number = self.request.user.phone_number
            address = self.request.user.address
            ip_address = None
        else:
            owner = None
            ip_address = self.request.META.get('REMOTE_ADDR')
        data = {'food_cart': food_cart, 'owner': owner, 'address': address, 'phone_number': phone_number,
                'ip_address': ip_address, 'is_active': True}
        food_cart.is_checked_out = True
        food_cart.save()
        serializer.save(**data)
        return Response({'message': "Order has been placed successfully"}, status=status.HTTP_201_CREATED)


class UserDashboardAPIView(IsOwnerOrIPMixin, generics.RetrieveAPIView):
    serializer_class = DeliveryEntitySerializer

    def get_object(self):
        if self.request.user.is_authenticated:
            return DeliveryEntity.objects.filter(owner=self.request.user.customer, is_active=True).first()
        else:
            return DeliveryEntity.objects.filter(ip_address=self.request.META.get('REMOTE_ADDR'),
                                                 is_active=True).first()

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class UserAcceptDeliveryAPIView(IsOwnerOrIPMixin, generics.UpdateAPIView):
    queryset = DeliveryEntity.objects.all()
    serializer_class = DeliveryEntitySerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        delivery_entity = self.get_object()
        if delivery_entity.is_accepted and delivery_entity.ongoing_status:
            delivery_entity.accept_delivery = True
            delivery_entity.is_active = False
            delivery_entity.save()
            response_data = {'message': ' You have accepted the delivery'}
            return Response(response_data, status=status.HTTP_200_OK)
        else:
            response_data = {'message': 'You can not accept delivery at this time'}
            return Response(response_data, status=status.HTTP_404_NOT_FOUND)


class AdminAcceptOrderAPIView(generics.UpdateAPIView):
    queryset = DeliveryEntity
    serializer_class = DeliveryEntitySerializer
    lookup_field = 'pk'
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        delivery_entity = self.get_object()
        delivery_entity.is_accepted = True
        delivery_entity.ongoing_status = True
        delivery_entity.save()
        response_data = {'message': 'You have accepted this order, delivery status is: ongoing'}
        return Response(response_data, status=status.HTTP_200_OK)


class DeliveryEntityDetailAPIView(generics.RetrieveAPIView):
    queryset = DeliveryEntity.objects.all()
    serializer_class = DeliveryEntitySerializer


class OngoingOrderListAPIView(generics.ListAPIView):
    queryset = OngoingOrder.objects.all()
    serializer_class = OngoingOrderSerializer
    permission_classes = [IsAdminUser]


class OngoingOrderDetailAPIView(generics.RetrieveAPIView):
    queryset = OngoingOrder.objects.all()
    serializer_class = OngoingOrderSerializer
    permission_classes = [IsAdminUser]


class CancelOngoingOrderAPIView(generics.UpdateAPIView):
    queryset = OngoingOrder.objects.all()
    serializer_class = OngoingOrderSerializer
    permission_classes = [IsAdminUser]

    def update(self, request, *args, **kwargs):
        ongoing_order = self.get_object()
        cancel_reason = request.data.get('cancel_reason', '')

        if cancel_reason:
            ongoing_order.cancel(cancel_reason)
            subject = 'Your ongoing Food order With tao Kitchen has been cancelled'
            message = f'Your ongoing Food order with ID {ongoing_order.id} has been cancelled for {cancel_reason}'
            from_email = 'otutaiwo1@gmail.com'
            recipient_list = [ongoing_order.delivery_entity.owner.user.email]
            send_mail(subject, message, from_email, recipient_list)

            ongoing_order.delivery_entity.ongoing_status = False
            ongoing_order.delivery_entity.save()

            serializer = self.get_serializer(ongoing_order)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Please select a cancel reason.'}, status=status.HTTP_404_NOT_FOUND)


class CustomerRegistrationAPIView(APIView):
    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            customer = serializer.save()
            response_data = {
                'message': 'Customer account created successfully',
                'customer_id': customer.id
            }
            return Response(response_data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DeliveryPersonCreateAccountAPIView(APIView):
    def post(self, request):
        serializer = DeliveryPersonSerializer(data=request.data)
        if serializer.is_valid():
            delivery_person = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerLoginAPIView(generics.CreateAPIView):
    serializer_class = LoginSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return Response(serializer.validated_data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomerDetailsUpdateAPIView(generics.UpdateAPIView):
    serializer_class = CustomerSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user.customer

    def perform_update(self, serializer):
        serializer.save()


class FoodSearchAPIView(APIView):
    def get(self, request):
        search_query = request.GET.get('search_query')
        if search_query:
            search = FoodDocument.search().query("match", name=search_query)
            results = search.execute()
            food_ids = [hit.meta.id for hit in results]
            foods = Food.active_objects.filter(id__in=food_ids)
            if foods:
                serialized_foods = FoodSerializer(foods, many=True, context={'request': request})
                return Response(serialized_foods.data)
            else:
                response_data = {'message': 'No food with this name is found'}
                return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        response_data = {'message': 'Please provide a search query'}
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)