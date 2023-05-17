from .models import FoodCart
from .session import unauthenticated_user_session_id


def food_cart_items_count(request):
    cart_total = 0

    if request.user.is_authenticated:
        selected_cart = FoodCart.objects.filter(user=request.user.customer, is_checked_out=False).first()
        if selected_cart is not None:
            cart_total = selected_cart.ordered_food.count()

    else:
        session_id = request.session.session_key
        selected_cart = FoodCart.objects.filter(session_id=unauthenticated_user_session_id(request),
                                                is_checked_out=False).first()
        if selected_cart is not None:
            cart_total = selected_cart.ordered_food.count()

    return {"cart_total": cart_total}
