from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import Product, Category, Brand, Favorite, Banner, Size, Storage, ProductImage, BasketItems, Basket, \
    OrderItems, Order


class CategoryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'title')


class BrandListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = ('id', 'title', 'logo')


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['file']


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


class StorageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Storage
        fields = ['id', 'product', 'size', 'quantity']


class BasketItemsSerializer(serializers.ModelSerializer):
    storage = StorageSerializer(read_only=True)

    class Meta:
        model = BasketItems
        fields = ['id', 'storage', 'quantity', 'created_at']


# =========================
# Создаем сериализатор для добавления товара в корзину
# =========================
class BasketItemsCreateSerializer(serializers.ModelSerializer):
    product_id = serializers.IntegerField(write_only=True)
    size_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = BasketItems
        fields = ['id', 'product_id', 'size_id', 'quantity']

    def validate(self, attrs):
        product_id = attrs.get('product_id')
        size_id = attrs.get('size_id')

        try:
            storage = Storage.objects.get(product_id=product_id, size_id=size_id)
        except Storage.DoesNotExist:
            raise serializers.ValidationError("Такой товар с этим размером не найден.")

        attrs['storage'] = storage
        return attrs

    def create(self, validated_data):
        user = self.context['request'].user
        if not user.is_authenticated:
            raise serializers.ValidationError("Пользователь не авторизован.")

        basket, _ = Basket.objects.get_or_create(user=user)
        quantity = validated_data.get('quantity', 1)
        storage = validated_data['storage']

        basket_item, created = BasketItems.objects.get_or_create(
            basket=basket,
            storage=storage,
            defaults={'quantity': quantity}
        )
        if not created:
            basket_item.quantity += quantity
            basket_item.save()

        return basket_item


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'cover', 'new_price']


class FavoriteSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = Favorite
        fields = ['id', 'product']


class CheckoutSerializer(serializers.Serializer):
    basket_id = serializers.IntegerField()

    def validate_basket_id(self, value):
        user = self.context['request'].user
        from .models import Basket
        basket = Basket.objects.filter(id=value, user=user).first()
        if not basket:
            raise serializers.ValidationError("Корзина не найдена.")
        if not basket.items.exists():
            raise serializers.ValidationError("Корзина пуста.")
        return value


class OrderItemsSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItems
        fields = ['id', 'storage', 'quantity']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemsSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'total_price', 'status', 'created_at', 'items']