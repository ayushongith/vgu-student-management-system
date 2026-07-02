from django.urls import path
from . import views

urlpatterns = [
    path('', views.fee_list, name='fee_list'),
    path('pay/create/', views.fee_payment_create, name='fee_payment_create'),
    path('categories/', views.fee_category_list, name='fee_category_list'),
    path('categories/create/', views.fee_category_create, name='fee_category_create'),
]
