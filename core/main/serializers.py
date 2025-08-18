from rest_framework import serializers
from .models import Product, Category, Brand, Banner, Size, Storage, ProductImage, BasketItems, Basket


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

class BasketItemsCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    size_id = serializers.IntegerField(write_only=True)
    quantity = serializers.IntegerField()
    total_price = serializers.IntegerField(write_only=True)

    def create(self, validated_data):
        basket,_ = Basket.objects.get_or_create(user=self.context['request'].user)
        product = Product.objects.filter(id=validated_data['product_id']).first()
        size = Size.objects.filter(id=validated_data['size_id']).first()

        storage_product = Storage.objects.filter(product=product, size=size).first()

        basket_items = BasketItems.objects.create(basket=basket, storage_product=storage_product, quantity=validated_data['quantity'])

        return basket_items
