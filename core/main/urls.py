from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
        path('index/', views.IndexView.as_view(), name='index'),
        path('catalog/', views.ProductCatalogView.as_view(), name='catalog'),
        path('detail_products/<int:product_id>/', views.ProductDetailView.as_view(), name='product_detail'),

        path('basket/create/', views.BasketItemsCreateView.as_view(), name='basket'),
]

