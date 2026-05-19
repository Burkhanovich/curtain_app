from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Curtain, Category, Color
from .cart import Cart


def index(request):
    """Bosh sahifa - asosiy pardalar va kategoriyalarni ko'rsatish"""
    # Faol va asosiy pardalar
    featured_curtains = Curtain.objects.filter(
        is_active=True, is_featured=True
    ).select_related('category').prefetch_related('images', 'colors')[:8]
    
    # Yangi pardalar
    new_curtains = Curtain.objects.filter(
        is_active=True
    ).select_related('category').prefetch_related('images', 'colors').order_by('-created_date')[:6]
    
    # Chegirmadagi pardalar
    sale_curtains = Curtain.objects.filter(
        is_active=True, discount_price__isnull=False
    ).select_related('category').prefetch_related('images', 'colors')[:6]
    
    # Kategoriyalar
    categories = Category.objects.annotate(
        curtains_count=Count('curtains', filter=Q(curtains__is_active=True))
    ).order_by('title')
    
    context = {
        'featured_curtains': featured_curtains,
        'new_curtains': new_curtains,
        'sale_curtains': sale_curtains,
        'categories': categories,
    }
    return render(request, 'index.html', context)


def products(request):
    """Barcha pardalarni sahifalab ko'rsatish"""
    curtains = Curtain.objects.filter(is_active=True).select_related('category').prefetch_related('images', 'colors')
    
    # Filtrlar
    category_id = request.GET.get('category')
    color_id = request.GET.get('color')
    fabric_type = request.GET.get('fabric')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    search = request.GET.get('search')
    sort_by = request.GET.get('sort', 'created_date')
    
    if category_id:
        # Try to convert to integer first, if fails, try to find by title
        try:
            curtains = curtains.filter(category_id=int(category_id))
        except (ValueError, TypeError):
            # If not a number, try to find category by title (case-insensitive)
            curtains = curtains.filter(category__title__icontains=category_id)
    
    if color_id:
        # Try to convert to integer first, if fails, try to find by title
        try:
            curtains = curtains.filter(colors__id=int(color_id))
        except (ValueError, TypeError):
            # If not a number, try to find color by title (case-insensitive)
            curtains = curtains.filter(colors__title__icontains=color_id)
    
    if fabric_type:
        curtains = curtains.filter(fabric_type=fabric_type)
    
    if min_price:
        curtains = curtains.filter(price__gte=min_price)
    
    if max_price:
        curtains = curtains.filter(price__lte=max_price)
    
    if search:
        curtains = curtains.filter(
            Q(title__icontains=search) | 
            Q(content__icontains=search) |
            Q(category__title__icontains=search)
        )
    
    # Saralash
    if sort_by == 'price_low':
        curtains = curtains.order_by('price')
    elif sort_by == 'price_high':
        curtains = curtains.order_by('-price')
    elif sort_by == 'name':
        curtains = curtains.order_by('title')
    elif sort_by == 'views':
        curtains = curtains.order_by('-views')
    else:
        curtains = curtains.order_by('-created_date')
    
    # Sahifalash
    paginator = Paginator(curtains, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Filtr uchun ma'lumotlar
    categories = Category.objects.all()
    colors = Color.objects.all()
    fabric_choices = Curtain.FABRIC_CHOICES
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'colors': colors,
        'fabric_choices': fabric_choices,
        'current_category': category_id,
        'current_color': color_id,
        'current_fabric': fabric_type,
        'current_search': search,
        'current_sort': sort_by,
    }
    return render(request, 'products.html', context)


def product_detail(request, slug):
    """Parda tafsilotlari"""
    curtain = get_object_or_404(
        Curtain.objects.select_related('category').prefetch_related('images', 'colors'),
        slug=slug, is_active=True
    )
    
    # Ko'rishlar sonini oshirish
    curtain.increment_views()
    
    # O'xshash pardalar
    similar_curtains = Curtain.objects.filter(
        category=curtain.category,
        is_active=True
    ).exclude(id=curtain.id).select_related('category').prefetch_related('images')[:4]
    
    context = {
        'curtain': curtain,
        'similar_curtains': similar_curtains,
    }
    return render(request, 'product-detail.html', context)


def category_detail_view(request, pk):
    """Kategoriya bo'yicha pardalar"""
    category = get_object_or_404(Category, pk=pk)
    curtains = Curtain.objects.filter(
        category=category, is_active=True
    ).select_related('category').prefetch_related('images', 'colors')
    
    # Sahifalash
    paginator = Paginator(curtains, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'category': category,
        'page_obj': page_obj,
    }
    return render(request, 'category.html', context)


def search_autocomplete(request):
    """Qidiruv uchun avtomatik to'ldirish"""
    query = request.GET.get('q', '')
    if len(query) < 2:
        return JsonResponse({'suggestions': []})
    
    curtains = Curtain.objects.filter(
        Q(title__icontains=query) | Q(category__title__icontains=query),
        is_active=True
    ).select_related('category')[:10]
    
    suggestions = []
    for curtain in curtains:
        main_image = curtain.images.filter(is_main=True).first()
        suggestions.append({
            'title': curtain.title,
            'category': curtain.category.title if curtain.category else '',
            'url': reverse('curtains:product_detail', kwargs={'slug': curtain.slug}),
            'image': main_image.image.url if main_image else ''
        })
    
    return JsonResponse({'suggestions': suggestions})


def cart(request):
    """Savat sahifasi"""
    cart_obj = Cart(request)
    cart_items = list(cart_obj)
    return render(request, 'cart.html', {'cart': cart_obj, 'cart_items': cart_items})


@require_POST
def cart_add(request, curtain_id):
    """Savatga mahsulot qo'shish"""
    curtain = get_object_or_404(Curtain, id=curtain_id, is_active=True)
    cart = Cart(request)
    try:
        quantity = int(request.POST.get('quantity', 1))
        quantity = max(1, min(quantity, 10))
    except (ValueError, TypeError):
        quantity = 1
    cart.add(curtain, quantity)
    messages.success(request, f'"{curtain.title}" savatga qo\'shildi.')
    return redirect('curtains:cart')


@require_POST
def cart_remove(request, curtain_id):
    """Savatdan mahsulot o'chirish"""
    cart = Cart(request)
    cart.remove(curtain_id)
    return redirect('curtains:cart')


@require_POST
def cart_update(request, curtain_id):
    """Savat mahsulot miqdorini yangilash"""
    cart = Cart(request)
    try:
        quantity = int(request.POST.get('quantity', 1))
    except (ValueError, TypeError):
        quantity = 1
    cart.update_quantity(curtain_id, quantity)
    return redirect('curtains:cart')


def cart_count(request):
    """Savat mahsulotlar soni (AJAX uchun)"""
    cart = Cart(request)
    return JsonResponse({'count': len(cart)})


def checkout(request):
    """Buyurtma berish sahifasi"""
    from apps.orders.forms import OrderForm
    from apps.orders.models import Order, OrderItem
    from apps.orders.telegram import send_order_notification

    cart_obj = Cart(request)
    cart_items = list(cart_obj)

    if not cart_items:
        messages.warning(request, "Savat bo'sh. Avval mahsulot qo'shing.")
        return redirect('curtains:products')

    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                customer_name=form.cleaned_data['customer_name'],
                customer_phone=form.cleaned_data['customer_phone'],
                customer_address=form.cleaned_data['customer_address'],
                notes=form.cleaned_data.get('notes', ''),
            )
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    curtain=item['curtain'],
                    quantity=item['quantity'],
                    unit_price=item['price'],
                )
            send_order_notification(order)
            cart_obj.clear()
            messages.success(
                request,
                f"Buyurtmangiz qabul qilindi! Buyurtma raqami: #{order.order_number}."
            )
            return redirect('orders:order_success', order_number=order.order_number)
        else:
            messages.error(request, "Formada xatoliklar mavjud. Iltimos, to'g'rilang.")
    else:
        initial = {}
        if request.user.is_authenticated:
            initial['customer_name'] = request.user.get_full_name()
        form = OrderForm(initial=initial)

    context = {
        'cart': cart_obj,
        'cart_items': cart_items,
        'form': form,
    }
    return render(request, 'checkout.html', context)


def contact(request):
    """Aloqa sahifasi"""
    return render(request, 'contact.html')


