from django.urls import path, include
import financrAPI.views
from rest_framework import routers
from rest_framework.authtoken import views

router = routers.DefaultRouter()
router.register('expenses', financrAPI.views.ExpenseView)
router.register('monthly', financrAPI.views.MonthlyView)
router.register('category', financrAPI.views.CategoryView)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api-token-auth/', views.obtain_auth_token, name="api-token-auth")
]