from django.shortcuts import render
from .serializers import ExpenseSerializer, CategorySerializer, MonthlySerializer
from data.models import Expense, Category, Monthly
from rest_framework import viewsets, response
from data.views import decr, gen_encr, encr
from financr.settings import SECRET_KEY
from django.db.models import Q
from datetime import datetime
from django.http import Http404
from rest_framework.mixins import UpdateModelMixin

import time

# Create your views here.


class ExpenseView(viewsets.ModelViewSet):
    queryset = Expense.objects.all()
    serializer_class = ExpenseSerializer

    def get_queryset(self):
        user = self.request.user

        values = {
            'user': user,
            'category': self.request.query_params.get('category', None),
            'date__gte': self.request.query_params.get('start', None),
            'date__lte': self.request.query_params.get('end', None),
            'notes__icontains': self.request.query_params.get('notes', None)
        }

        arguments = {}

        for k, v in values.items():
            if v:
                arguments[k] = v

        data = Expense.objects.filter(**arguments).order_by("-date")

        return data

    def create(self, request):
        price_b = self.request.data['price_b']
        user = self.request.user.id
        category = self.request.data['category']
        date = self.request.data['date']

        if self.request.data["notes"].strip() == "":
            note = "-"
        else:
            note = self.request.data["notes"]

        serializer = ExpenseSerializer(data={'user': user, 'price_b': price_b, 'category': category, 'date': date, 'notes': note})

        serializer.is_valid()

        serializer.save()

        return response.Response(serializer.data)

class MonthlyView(viewsets.ModelViewSet):
    queryset = Monthly.objects.all()
    serializer_class = MonthlySerializer

    def get_queryset(self):
        user = self.request.user
        data = Monthly.objects.filter(user=user)

        return data

    def create(self, request):
        user = self.request.user.id
        monthly = self.request.data['monthly']
        
        serializer = MonthlySerializer(data={'user': user, 'monthly': monthly})

        serializer.is_valid()
        serializer.save()

        return response.Response(serializer.data)


class CategoryView(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def get_queryset(self):
        user = self.request.user
        return Category.objects.filter(user=user)

    def create(self, request):
        user = self.request.user.id
        category = self.request.data['cat']

        serializer = CategorySerializer(data={'user': user, 'cat': category})

        serializer.is_valid()
        serializer.save()

        return response.Response(serializer.data)
