import django_filters
from .models import Product

class ProductFilter(django_filters.FilterSet):
    category = django_filters.NumberFilter(field_name='category__id')
    brands = django_filters.NumberFilter(field_name='brands__id')

    class Meta:
        model = Product
        fields = ['category', 'brands']