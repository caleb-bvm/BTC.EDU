from .cart import cart_summary


def cart_context(request):
    return cart_summary(request)
