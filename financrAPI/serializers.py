from rest_framework import serializers
from data.models import Expense, Category, Monthly
from django.contrib.auth.models import User
from data.views import decr, gen_encr, encr
from financr.settings import SECRET_KEY

class BitFieldSerializer(serializers.Field):
    def to_representation(self, obj):
        obj = float(decr(gen_encr(SECRET_KEY), bytes(obj)))
        
        return float(obj)

    def to_internal_value(self, obj):
        obj = encr(gen_encr(SECRET_KEY), str(obj))

        return bytes(obj)

class ExpenseSerializer(serializers.ModelSerializer):
    price_b = BitFieldSerializer()
    class Meta:
        model = Expense
        fields = "__all__"

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = "__all__"

class MonthlySerializer(serializers.ModelSerializer):
    monthly = BitFieldSerializer()
    class Meta:
        model = Monthly
        fields = "__all__"

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username", "password", "first_name", "last_name", "email")
        extra_kwargs = {'password': {'write_only': True}, 
                        'is_superuser': {'read_only': True}, 
                        'is_staff': {'read_only': True}, 
                        'is_active': {'read_only': True}, 
                        'date_joined': {'read_only': True}, 
                        'groups': {'read_only': True}, 
                        'user_permissions': {'read_only': True}, 
                        'last_login': {'read_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
