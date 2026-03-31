from .models import Cart, Category

def cart_count(request):
    """Контекстный процессор для количества товаров в корзине"""
    cart_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = cart.items.count()
    else:
        session_id = request.session.session_key
        if session_id:
            cart = Cart.objects.filter(session_id=session_id).first()
            if cart:
                cart_count = cart.items.count()
    return {'cart_count': cart_count}


def categories(request):
    """Контекстный процессор для списка категорий (для меню)"""
    categories_list = Category.objects.all()
    return {'categories': categories_list}