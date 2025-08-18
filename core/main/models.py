from django.db import models
from .choices import *
from django.contrib.auth import get_user_model

MyUser = get_user_model()


class Category(models.Model):
    title = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.title


class Brand(models.Model):
    title = models.CharField(max_length=100)
    logo = models.ImageField(upload_to='media/brand_logos/')

    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

    def __str__(self):
        return self.title


class Product(models.Model):
    title = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    brands = models.ManyToManyField(Brand)
    description = models.TextField(null=True, blank=True)
    cover = models.ImageField(upload_to='media/product_covers/')
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    new_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Товар"
        verbose_name_plural = "Товары"

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    file = models.ImageField(upload_to='product_images/')

    class Meta:
        verbose_name = "Изображение товара"
        verbose_name_plural = "Изображения товаров"

    def __str__(self):
        return f"Фото {self.product}"


class Basket(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="baskets")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def update_total(self):
        self.total_price = sum(item.quantity * item.storage.product.new_price for item in self.items.all())
        self.save()
        
    class Meta:
        verbose_name = "Корзина"
        verbose_name_plural = "Корзины"

    def __str__(self):
        return f"{self.user}"


class Banner(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField(null=True, blank=True)
    cover = models.ImageField(upload_to='media/banner_covers/')
    location = models.CharField(max_length=100, choices=BannerLocationEnum.choices)
    is_active = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"

    def __str__(self):
        return self.title


class Size(models.Model):
    title = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Размер"
        verbose_name_plural = "Размеры"

    def __str__(self):
        return self.title


class Storage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="storages")
    size = models.ForeignKey(Size, on_delete=models.CASCADE, related_name="storages")
    quantity = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name = "Склад"
        verbose_name_plural = "Склады"

    def __str__(self):
        return f"{self.product} ({self.size}) — {self.quantity}"


class BasketItems(models.Model):
    basket = models.ForeignKey(Basket, on_delete=models.CASCADE, related_name="items")
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Товар в корзине"
        verbose_name_plural = "Товары в корзине"

    def __str__(self):
        return f"{self.basket} — {self.storage} x {self.quantity}"


class Order(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="orders")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    update_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=50)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ #{self.id}"


class OrderItems(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    storage = models.ForeignKey(Storage, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        verbose_name = "Товар в заказе"
        verbose_name_plural = "Товары в заказе"

    def __str__(self):
        return f"{self.order} — {self.storage} x {self.quantity}"


class Favorite(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name="favorites")
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="favorited_by")

    class Meta:
        verbose_name = "Избранное"
        verbose_name_plural = "Избранные товары"

    def __str__(self):
        return f"❤️ {self.product}"
