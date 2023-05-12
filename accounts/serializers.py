from rest_framework import serializers
from .models import Customer, DeliveryPerson


class DeliveryPersonSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = DeliveryPerson
        fields = '__all__'


class CustomerSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Customer
        fields = '__all__'
