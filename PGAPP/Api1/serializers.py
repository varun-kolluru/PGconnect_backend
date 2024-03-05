from rest_framework import serializers
from .models import Pgs_Data,Room_Info,Guest_Info,Payments
from django.contrib.auth import get_user_model

UserModel=get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserModel
        fields = '__all__'

class Pgs_Data_serializer(serializers.ModelSerializer):
    class Meta:
        model = Pgs_Data
        fields = '__all__'

class Room_Info_serializer(serializers.ModelSerializer):
    class Meta:
        model = Room_Info
        fields = '__all__'

class Guest_Info_serializer(serializers.ModelSerializer):
    class Meta:
        model = Guest_Info
        fields = '__all__'

class Payments_serializer(serializers.ModelSerializer):
    class Meta:
        model = Payments
        fields = '__all__'

