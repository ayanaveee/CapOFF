from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('index/', views.IndexView.as_view(), name='index'),
    path('catalog/', views.ProductCatalogView.as_view(), name='catalog'),
    path('product/<int:product_id>/',views.ProductDetailView.as_view(), name='product_detail'),

    path('basket/add/', views.BasketItemsCreateView.as_view(), name='basket_add'),

    path('favorites/', views.FavoriteListView.as_view(), name='favorite_list'),
    path('favorites/add/<int:product_id>/', views.AddToFavoriteView.as_view(), name='favorite_add'),
    path('favorites/remove/<int:product_id>/', views.RemoveFromFavoriteView.as_view(), name='favorite_remove'),

    path('checkout/', views.CheckoutAPIView.as_view(), name='checkout'),
    path('orders/', views.OrderListAPIView.as_view(), name='orders_list'),
    path('orders/<int:id>/', views.OrderDetailAPIView.as_view(), name='order_detail'),
]
