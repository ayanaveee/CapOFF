from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
        path('index/', views.IndexView.as_view(), name='index'),
        path('catalog/', views.ProductCatalogView.as_view(), name='catalog'),
        path('detail_products/<int:product_id>/', views.ProductDetailView.as_view(), name='product_detail'),

        path('basket/create/', views.BasketItemsCreateView.as_view(), name='basket'),
        path('basket/add/<int:storage_id>/', views.AddToBasketView.as_view(), name='add_to_basket'),

        path('favorites/', views.FavoriteListView.as_view(), name='favorites_list'),
        path('favorites/add/<int:product_id>/', views.AddToFavoriteView.as_view(), name='add_to_favorite'),
]

