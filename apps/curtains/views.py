from django.shortcuts import render

def index(request):
    """Bosh sahifa"""
    return render(request, 'index.html')

def products(request):
    """Mahsulotlar sahifasi"""
    return render(request, 'products.html')

def product_detail(request, product_id=None):
    """Mahsulot tafsiloti sahifasi"""
    context = {
        'product_id': product_id
    }
    return render(request, 'product-detail.html', context)

def cart(request):
    """Savat sahifasi"""
    return render(request, 'cart.html')

def checkout(request):
    """Buyurtma berish sahifasi"""
    return render(request, 'checkout.html')

def contact(request):
    """Aloqa sahifasi"""
    return render(request, 'contact.html')

def login_view(request):
    """Kirish sahifasi"""
    return render(request, 'login.html')

def register_view(request):
    """Ro'yxatdan o'tish sahifasi"""
    return render(request, 'register.html')
