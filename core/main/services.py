from django.core.exceptions import ValidationError
from .models import Basket, Storage, BasketItems

def add_to_basket(basket: Basket, storage: Storage, quantity: int):
    if storage.quantity < quantity:
        raise ValidationError("Товар закончился на складе")
    basket_item, created = BasketItems.objects.get_or_create(
        basket=basket,
        storage=storage,
        defaults={"quantity": quantity}
    )
    if not created:
        if storage.quantity < basket_item.quantity + quantity:
            raise ValidationError("Товар закончился на складе")
        basket_item.quantity += quantity
        basket_item.save()
    basket.update_total()
    return basket_item
