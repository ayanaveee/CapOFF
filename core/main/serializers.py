from rest_framework import serializers
from .models import Product, Category, Brand, Banner


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title')

class BrandListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'title', 'logo')


class ProductListSerializer(serializers.ModelSerializer):
    category = CategoryListSerializer()
    brands = BrandListSerializer(many=True)
    class Meta:
        model = Product
        fields = "__all__"

class BannerListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        exclude = ('is_active',)