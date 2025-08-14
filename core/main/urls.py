from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
        path('index/', views.IndexView.as_view(), name='index'),
        path('catalog/', views.ProductCatalogView.as_view(), name='catalog'),
]

