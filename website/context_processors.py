from .models import Cart

def cart_count(request):
    cart_id = request.COOKIES.get('cart_id')
    total_items = 0

    if cart_id:
        try:
            cart = Cart.objects.get(cart_id=cart_id)
            total_items = sum(item.quantity for item in cart.items.all())
        except Cart.DoesNotExist:
            pass

    return {'cart_item_count': total_items}