from django.db.models import Q, Count
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product, ProductImage, Banner, Size, Storage
from .serializers import ProductListSerializer, BannerListSerializer, BasketItemsCreateSerializer
from rest_framework import serializers, status


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['file']


class ProductDetailSerializer(serializers.ModelSerializer):
    sizes = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    recommended_products = serializers.SerializerMethodField()
    category = serializers.StringRelatedField()
    brands = serializers.StringRelatedField(many=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'category', 'brands', 'description',
            'cover', 'images', 'sizes', 'new_price', 'old_price',
            'recommended_products'
        ]

    def get_sizes(self, obj):
        sizes = Size.objects.all()
        result = {}
        for size in sizes:
            storage = Storage.objects.filter(product=obj, size=size, quantity__gte=1).exists()
            if storage:
                result[size.title] = {"id": size.id}
        return result

    def get_images(self, obj):
        images = ProductImage.objects.filter(product=obj)
        return ProductImageSerializer(images, many=True).data

    def get_recommended_products(self, obj):
        products = Product.objects.filter(category=obj.category).exclude(id=obj.id)[:4]
        return ProductListSerializer(products, many=True).data



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


class ProductCatalogView(APIView):
    def get(self, request):
        sort = request.GET.get('sort')
        category_id = request.GET.get('category')
        brand_id = request.GET.get('brand')

        catalog_banner = Banner.objects.filter(location='catalog_head')
        products = Product.objects.all()

        if category_id:
            products = products.filter(category_id=category_id)
        if brand_id:
            products = products.filter(brands__id=brand_id)

        if sort == 'popular':
            products = products.annotate(
                orders_count=Count('storages__orderitems', distinct=True)
            ).order_by('-orders_count', '-id')
        elif sort == 'new':
            products = products.order_by('-created_at')
        elif sort == 'cheap':
            products = products.order_by('new_price', 'old_price')
        elif sort == 'expensive':
            products = products.order_by('-new_price', '-old_price')

        return Response({
            "catalog_banner": BannerListSerializer(catalog_banner, many=True).data,
            "products_catalog": ProductListSerializer(products, many=True).data
        })


class ProductDetailView(APIView):
    def get(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)


class BasketItemsCreateView(APIView):
    def post(self, request):
        serializer = BasketItemsCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
