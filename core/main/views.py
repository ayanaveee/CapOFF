from django.db.models import Q, Count
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product, Banner
from .serializers import ProductListSerializer, BannerListSerializer

#class IndexView(APIView):
    #def get(self, request):
        #products = Product.objects.all()
        #serializer = ProductListSerializer(products, many=True)

        #return Response(serializer.data)

class IndexView(APIView):
    def get(self, request):
        index_banner = Banner.objects.filter(Q(location='index_head') | Q(location='index_middle'))
        popular_brands = Banner.objects.all()[:4]
        best_seller_products = Product.objects.all()[:4]
        discounted_products = Product.objects.filter(new_price__isnull=False)[:4]

        popular_brands_serializer = BannerListSerializer(popular_brands, many=True)
        best_seller_products_serializer = ProductListSerializer(best_seller_products, many=True)
        discounted_products_serializer = ProductListSerializer(discounted_products, many=True)
        index_banner_serializer = BannerListSerializer(index_banner, many=True)

        return Response({
            "index_banner": index_banner_serializer.data,
            "popular_brands": popular_brands_serializer.data,
            "best_seller_products": best_seller_products_serializer.data,
            "discounted_products": discounted_products_serializer.data
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
