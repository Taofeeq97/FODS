from django.contrib.auth import authenticate
from rest_framework import serializers
from Orders.models import OptionalItem, OrderedOptionalItem, OrderedFood, OngoingOrder, DeliveryEntity, FoodCart, Food, \
    Tag
from accounts.models import CustomUser, Customer, DeliveryPerson
from rest_framework_simplejwt.tokens import RefreshToken


class CustomUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'username', 'email', 'address', 'phone_number', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = CustomUser(**validated_data)
        if password is not None:
            user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password is not None:
            instance.set_password(password)
        return super().update(instance, validated_data)


class CustomerSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = Customer
        fields = ['user']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user_serializer = CustomUserSerializer(data=user_data)
        user_serializer.is_valid(raise_exception=True)
        user = user_serializer.save()
        customer = Customer.objects.create(user=user, **validated_data)
        return customer

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user
        user_serializer = CustomUserSerializer(user, data=user_data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        return super().update(instance, validated_data)


class DeliveryPersonSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer()

    class Meta:
        model = DeliveryPerson
        fields = ['user', 'is_accepted', 'is_available', 'ride_number']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = CustomUserSerializer().create(user_data)
        delivery_person = DeliveryPerson.objects.create(user=user, **validated_data)
        return delivery_person

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user')
        user = instance.user
        user_serializer = CustomUserSerializer(user, data=user_data, partial=True)
        user_serializer.is_valid(raise_exception=True)
        user_serializer.save()
        return super().update(instance, validated_data)


class TagSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class OptionalItemsSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = OptionalItem
        fields = '__all__'


class FoodSerializer(serializers.HyperlinkedModelSerializer):
    tags = TagSerializer(many=True)
    optional_items = OptionalItemsSerializer(many=True)

    class Meta:
        model = Food
        fields = '__all__'

    def get_tags(self, obj):
        return [tag.name for tag in obj.tags.all()]

    def get_optional_items(self, obj):
        return [item.name for item in obj.optional_items.all()]


class OrderedFoodSerializer(serializers.ModelSerializer):
    optional_items = serializers.ReadOnlyField()

    class Meta:
        model = OrderedFood
        fields = ['id', 'user', 'ip_address', 'food', 'optional_items', 'food_quantity', 'created', 'get_total_price']

    def get_total_price(self, obj):
        return obj.get_total_price()


class OrderedOptionalItemSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = OrderedOptionalItem
        fields = '__all__'

    def get_total_price(self, obj):
        return obj.get_total_price()


class FoodCartSerializer(serializers.ModelSerializer):
    # ordered_food = OrderedFoodSerializer(many=True, read_only=True)
    cart_number_of_items = serializers.ReadOnlyField()
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = FoodCart
        fields = '__all__'

    def get_total_price(self, obj):
        return obj.get_total_price()


class DeliveryEntitySerializer(serializers.ModelSerializer):
    food_cart = FoodCartSerializer(read_only=True)
    owner = CustomerSerializer(read_only=True)

    class Meta:
        model = DeliveryEntity
        fields = '__all__'


class OngoingOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OngoingOrder
        fields = '__all__'


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        # Perform authentication here
        user = authenticate(username=username, password=password)

        if user is None:
            raise serializers.ValidationError('Invalid login credentials')

        # Authentication is successful, generate tokens
        refresh = RefreshToken.for_user(user)
        attrs['access_token'] = str(refresh.access_token)
        attrs['refresh_token'] = str(refresh)

        return attrs

