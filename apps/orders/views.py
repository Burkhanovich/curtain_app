from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator
from django.db.models import Q, Count, Sum
from django.utils import timezone
from apps.curtains.models import Curtain
from .models import Order, OrderItem
from .forms import QuickOrderForm, OrderForm, OrderSearchForm


def quick_order_view(request, curtain_id):
    """Tez buyurtma berish - bitta mahsulot uchun"""
    curtain = get_object_or_404(Curtain, id=curtain_id, is_active=True)
    
    if request.method == 'POST':
        form = QuickOrderForm(request.POST)
        if form.is_valid():
            # Buyurtma yaratish
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                customer_name=form.cleaned_data['customer_name'],
                customer_phone=form.cleaned_data['customer_phone'],
                customer_address=form.cleaned_data['customer_address'],
                notes=form.cleaned_data['notes']
            )
            
            # Buyurtma elementi yaratish
            OrderItem.objects.create(
                order=order,
                curtain=curtain,
                quantity=form.cleaned_data['quantity'],
                unit_price=curtain.final_price,
                custom_width=form.cleaned_data.get('custom_width'),
                custom_height=form.cleaned_data.get('custom_height'),
                custom_notes=form.cleaned_data.get('custom_notes')
            )
            
            messages.success(
                request, 
                f'Buyurtmangiz qabul qilindi! Buyurtma raqami: #{order.order_number}. '
                'Tez orada sotuvchilarimiz siz bilan bog\'lanishadi.'
            )
            return redirect('orders:order_success', order_number=order.order_number)
        else:
            messages.error(request, 'Formada xatoliklar mavjud. Iltimos, to\'g\'rilang.')
    else:
        initial_data = {'curtain_id': curtain.id}
        if request.user.is_authenticated:
            initial_data.update({
                'customer_name': request.user.get_full_name(),
                'customer_phone': request.user.phone or '',
            })
        form = QuickOrderForm(initial=initial_data)
    
    context = {
        'curtain': curtain,
        'form': form,
    }
    return render(request, 'orders/quick_order.html', context)


def order_success_view(request, order_number):
    """Buyurtma muvaffaqiyatli yaratilganini ko'rsatish"""
    order = get_object_or_404(Order, order_number=order_number)
    
    context = {
        'order': order,
    }
    return render(request, 'orders/order_success.html', context)


@login_required
def my_orders_view(request):
    """Foydalanuvchining buyurtmalari"""
    orders = Order.objects.filter(
        user=request.user
    ).prefetch_related('items__curtain').order_by('-created_date')
    
    # Sahifalash
    paginator = Paginator(orders, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
    }
    return render(request, 'orders/my_orders.html', context)


@login_required
def order_detail_view(request, order_number):
    """Buyurtma tafsilotlari"""
    order = get_object_or_404(
        Order, 
        order_number=order_number,
        user=request.user
    )
    
    context = {
        'order': order,
    }
    return render(request, 'orders/order_detail.html', context)


@require_POST
def cancel_order_view(request, order_number):
    """Buyurtmani bekor qilish"""
    order = get_object_or_404(Order, order_number=order_number)
    
    # Foydalanuvchi tekshiruvi (faqat o'zining buyurtmasini bekor qila oladi yoki admin)
    if not (request.user.is_authenticated and 
            (order.user == request.user or request.user.is_staff)):
        messages.error(request, 'Sizda bu buyurtmani bekor qilish huquqi yo\'q.')
        return redirect('curtains:index')
    
    # Faqat "kutilmoqda" va "tasdiqlangan" holatdagi buyurtmalarni bekor qilish mumkin
    if order.status in ['pending', 'confirmed']:
        order.status = 'cancelled'
        order.save()
        
        # Status tarixi yaratish
        from .models import OrderStatusHistory
        OrderStatusHistory.objects.create(
            order=order,
            old_status=order.status,
            new_status='cancelled',
            changed_by=request.user,
            comment='Mijoz tomonidan bekor qilindi'
        )
        
        messages.success(request, f'Buyurtma #{order.order_number} bekor qilindi.')
    else:
        messages.error(request, 'Bu buyurtmani bekor qilib bo\'lmaydi.')
    
    if request.user.is_authenticated and order.user == request.user:
        return redirect('orders:my_orders')
    else:
        return redirect('curtains:index')


# Staff foydalanuvchilar uchun view'lar
@login_required
def orders_management_view(request):
    """Buyurtmalarni boshqarish (staff uchun)"""
    if not request.user.is_staff:
        messages.error(request, 'Bu sahifaga kirish huquqingiz yo\'q.')
        return redirect('curtains:index')
    
    form = OrderSearchForm(request.GET)
    orders = Order.objects.all().prefetch_related('items__curtain').order_by('-created_date')
    
    # Filtrlar
    if form.is_valid():
        search = form.cleaned_data.get('search')
        status = form.cleaned_data.get('status')
        date_from = form.cleaned_data.get('date_from')
        date_to = form.cleaned_data.get('date_to')
        
        if search:
            orders = orders.filter(
                Q(order_number__icontains=search) |
                Q(customer_name__icontains=search) |
                Q(customer_phone__icontains=search)
            )
        
        if status:
            orders = orders.filter(status=status)
        
        if date_from:
            orders = orders.filter(created_date__date__gte=date_from)
        
        if date_to:
            orders = orders.filter(created_date__date__lte=date_to)
    
    # Sahifalash
    paginator = Paginator(orders, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistika
    stats = {
        'total_orders': Order.objects.count(),
        'pending_orders': Order.objects.filter(status='pending').count(),
        'confirmed_orders': Order.objects.filter(status='confirmed').count(),
        'completed_orders': Order.objects.filter(status='delivered').count(),
        'today_orders': Order.objects.filter(created_date__date=timezone.now().date()).count(),
    }
    
    context = {
        'page_obj': page_obj,
        'form': form,
        'stats': stats,
    }
    return render(request, 'orders/orders_management.html', context)


@login_required
@require_POST
def update_order_status_view(request, order_id):
    """Buyurtma holatini o'zgartirish (staff uchun)"""
    if not request.user.is_staff:
        return JsonResponse({'success': False, 'message': 'Ruxsat yo\'q'})
    
    order = get_object_or_404(Order, id=order_id)
    new_status = request.POST.get('status')
    comment = request.POST.get('comment', '')
    
    if new_status in dict(Order.STATUS_CHOICES):
        old_status = order.status
        order.status = new_status
        order.processed_by = request.user
        
        if new_status == 'confirmed':
            from django.utils import timezone
            order.confirmed_date = timezone.now()
        
        order.save()
        
        # Status tarixi yaratish
        from .models import OrderStatusHistory
        OrderStatusHistory.objects.create(
            order=order,
            old_status=old_status,
            new_status=new_status,
            changed_by=request.user,
            comment=comment
        )
        
        return JsonResponse({
            'success': True, 
            'message': f'Buyurtma holati {order.get_status_display()} ga o\'zgartirildi.'
        })
    
    return JsonResponse({'success': False, 'message': 'Noto\'g\'ri holat'})


def order_stats_api_view(request):
    """Buyurtma statistikasi (AJAX uchun)"""
    if not request.user.is_staff:
        return JsonResponse({'error': 'Ruxsat yo\'q'}, status=403)
    
    from django.utils import timezone
    from datetime import timedelta
    
    today = timezone.now().date()
    week_ago = today - timedelta(days=7)
    
    stats = {
        'total': Order.objects.count(),
        'pending': Order.objects.filter(status='pending').count(),
        'confirmed': Order.objects.filter(status='confirmed').count(),
        'in_progress': Order.objects.filter(status='in_progress').count(),
        'ready': Order.objects.filter(status='ready').count(),
        'delivered': Order.objects.filter(status='delivered').count(),
        'cancelled': Order.objects.filter(status='cancelled').count(),
        'today': Order.objects.filter(created_date__date=today).count(),
        'this_week': Order.objects.filter(created_date__date__gte=week_ago).count(),
    }
    
    return JsonResponse(stats)
