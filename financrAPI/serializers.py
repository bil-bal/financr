from rest_framework import serializers
from data.models import Expense, Category, Monthly
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
