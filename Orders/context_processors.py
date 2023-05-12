from .models import FoodCart


def food_cart_items_count(request):
    if request.user.is_authenticated:
        try:
            selected_cart = FoodCart.objects.filter(user=request.user.customer, is_checked_out=False).first()
            cart_total = selected_cart.ordered_food.all().count()
            return {"cart_total": cart_total}
        except:
            return {"cart_total": 0}
    else:
        try:
            selected_cart = FoodCart.objects.filter(ip_address=request.META.get("REMOTE_ADDRS"),
                                                    is_checked_out=False).first()
            cart_total = selected_cart.ordered_products.all().count()
            return {"cart_total": cart_total}
        except:
            return {"cart_total": 0}
