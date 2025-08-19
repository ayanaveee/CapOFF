from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework import status
from django_filters.rest_framework import DjangoFilterBackend
from django_filters import rest_framework as filters
from.filters import ProductFilter
from .models import Product, Favorite, Banner, Storage, Basket, BasketItems, Order, OrderItems
from .serializers import (
    ProductListSerializer,
    BannerListSerializer,
    ProductDetailSerializer,
    BasketItemsCreateSerializer,
    BasketItemsSerializer,
    FavoriteSerializer,
    CheckoutSerializer,
    OrderSerializer
)


class IndexView(APIView):
    def get(self, request):
        index_banner = Banner.objects.filter(Q(location='index_head') | Q(location='index_middle'))
        popular_brands = Banner.objects.all()[:4]
        best_seller_products = Product.objects.all()[:4]
        discounted_products = Product.objects.filter(new_price__isnull=False)[:4]

        return Response({
            "index_banner": BannerListSerializer(index_banner, many=True).data,
            "popular_brands": BannerListSerializer(popular_brands, many=True).data,
            "best_seller_products": ProductListSerializer(best_seller_products, many=True).data,
            "discounted_products": ProductListSerializer(discounted_products, many=True).data
        })


from rest_framework import generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import Product, Banner
from .serializers import ProductListSerializer, BannerListSerializer
from .filters import ProductFilter


class ProductCatalogView(generics.ListAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductListSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def list(self, request, *args, **kwargs):
        catalog_banner = Banner.objects.filter(location='catalog_head')

        filtered_products = self.filter_queryset(self.get_queryset())

        return Response({
            "catalog_banner": BannerListSerializer(catalog_banner, many=True).data,
            "products_catalog": ProductListSerializer(filtered_products, many=True).data
        })


class ProductDetailView(APIView):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)


class BasketItemsCreateView(APIView):
    def post(self, request):
        serializer = BasketItemsCreateSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            basket_item = serializer.save()
            return Response(BasketItemsSerializer(basket_item).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FavoriteListView(APIView):
    def get(self, request):
        favorites = Favorite.objects.filter(user=request.user)
        serializer = FavoriteSerializer(favorites, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class AddToFavoriteView(APIView):
    def post(self, request, product_id):
        user = request.user
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": "Товар не найден"}, status=status.HTTP_404_NOT_FOUND)

        favorite, created = Favorite.objects.get_or_create(user=user, product=product)
        if not created:
            return Response({"detail": "Товар уже в избранном"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = FavoriteSerializer(favorite)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RemoveFromFavoriteView(APIView):
    def delete(self, request, product_id):
        user = request.user
        try:
            favorite = Favorite.objects.get(user=user, product_id=product_id)
            favorite.delete()
            return Response({"detail": "Товар удалён из избранного"}, status=status.HTTP_204_NO_CONTENT)
        except Favorite.DoesNotExist:
            return Response({"detail": "Товар не найден в избранном"}, status=status.HTTP_404_NOT_FOUND)


class CheckoutAPIView(generics.GenericAPIView):
    serializer_class = CheckoutSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        basket_id = serializer.validated_data['basket_id']
        basket = Basket.objects.get(id=basket_id, user=request.user)

        order = Order.objects.create(
            user=request.user,
            total_price=basket.total_price,
            status="Создан"
        )

        for item in basket.items.all():
            OrderItems.objects.create(
                order=order,
                storage=item.storage,
                quantity=item.quantity)

        basket.items.all().delete()
        basket.update_total()

        return Response({"detail": f"Заказ #{order.id} создан успешно."}, status=status.HTTP_201_CREATED)


class OrderListAPIView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).order_by('-created_at')

class OrderDetailAPIView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'id'

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)