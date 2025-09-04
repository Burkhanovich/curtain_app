from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView, DeleteView, DetailView
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.core.paginator import Paginator
from .forms import (
    CustomUserCreationForm, CustomAuthenticationForm, UserProfileForm,
    UserProfileDetailForm, UserAddressForm, PasswordChangeForm
)
from .models import User, UserProfile, UserAddress


class CustomLoginView(LoginView):
    """Maxsus kirish sahifasi"""
    form_class = CustomAuthenticationForm
    template_name = 'accounts/login.html'
    success_url = reverse_lazy('curtains:index')
    redirect_authenticated_user = True
    
    def form_valid(self, form):
        remember_me = form.cleaned_data.get('remember_me')
        if not remember_me:
            self.request.session.set_expiry(0)
        return super().form_valid(form)
    
    def get_success_url(self):
        next_url = self.request.GET.get('next')
        if next_url:
            return next_url
        return reverse('curtains:index')


def register_view(request):
    """Ro'yxatdan o'tish sahifasi"""
    if request.user.is_authenticated:
        return redirect('curtains:index')
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Salom {username}! Hisobingiz muvaffaqiyatli yaratildi.')
            
            # Foydalanuvchini avtomatik kirish
            login(request, user)
            return redirect('curtains:index')
        else:
            messages.error(request, 'Ro\'yxatdan o\'tishda xatolik yuz berdi. Iltimos, ma\'lumotlarni tekshiring.')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


class CustomLogoutView(LogoutView):
    """Maxsus chiqish sahifasi"""
    next_page = reverse_lazy('curtains:index')
    
    def dispatch(self, request, *args, **kwargs):
        messages.success(request, 'Siz tizimdan muvaffaqiyatli chiqdingiz.')
        return super().dispatch(request, *args, **kwargs)


@login_required
def profile_view(request):
    """Foydalanuvchi profili sahifasi"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    addresses = UserAddress.objects.filter(user=user)
    
    context = {
        'user': user,
        'profile': profile,
        'addresses': addresses,
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def profile_edit_view(request):
    """Foydalanuvchi profilini tahrirlash"""
    user = request.user
    profile, created = UserProfile.objects.get_or_create(user=user)
    
    if request.method == 'POST':
        user_form = UserProfileForm(request.POST, request.FILES, instance=user)
        profile_form = UserProfileDetailForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profilingiz muvaffaqiyatli yangilandi.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Profilni yangilashda xatolik yuz berdi.')
    else:
        user_form = UserProfileForm(instance=user)
        profile_form = UserProfileDetailForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/profile_edit.html', context)


@login_required
def change_password_view(request):
    """Parolni o'zgartirish"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Parolingiz muvaffaqiyatli o\'zgartirildi.')
            return redirect('accounts:profile')
        else:
            messages.error(request, 'Parolni o\'zgartirishda xatolik yuz berdi.')
    else:
        form = PasswordChangeForm(request.user)
    
    return render(request, 'accounts/change_password.html', {'form': form})


@login_required
def address_list_view(request):
    """Foydalanuvchi manzillari ro'yxati"""
    addresses = UserAddress.objects.filter(user=request.user)
    return render(request, 'accounts/address_list.html', {'addresses': addresses})


@login_required
def address_create_view(request):
    """Yangi manzil qo'shish"""
    if request.method == 'POST':
        form = UserAddressForm(request.POST)
        if form.is_valid():
            address = form.save(commit=False)
            address.user = request.user
            address.save()
            messages.success(request, 'Manzil muvaffaqiyatli qo\'shildi.')
            return redirect('accounts:address_list')
        else:
            messages.error(request, 'Manzil qo\'shishda xatolik yuz berdi.')
    else:
        form = UserAddressForm()
    
    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Yangi Manzil Qo\'shish'})


@login_required
def address_edit_view(request, pk):
    """Manzilni tahrirlash"""
    address = get_object_or_404(UserAddress, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = UserAddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            messages.success(request, 'Manzil muvaffaqiyatli yangilandi.')
            return redirect('accounts:address_list')
        else:
            messages.error(request, 'Manzilni yangilashda xatolik yuz berdi.')
    else:
        form = UserAddressForm(instance=address)
    
    return render(request, 'accounts/address_form.html', {'form': form, 'title': 'Manzilni Tahrirlash'})


@login_required
def address_delete_view(request, pk):
    """Manzilni o'chirish"""
    address = get_object_or_404(UserAddress, pk=pk, user=request.user)
    
    if request.method == 'POST':
        address.delete()
        messages.success(request, 'Manzil muvaffaqiyatli o\'chirildi.')
        return redirect('accounts:address_list')
    
    return render(request, 'accounts/address_confirm_delete.html', {'address': address})


@login_required
def set_default_address_view(request, pk):
    """Asosiy manzilni belgilash"""
    address = get_object_or_404(UserAddress, pk=pk, user=request.user)
    
    # Boshqa barcha manzillarni asosiy emas deb belgilash
    UserAddress.objects.filter(user=request.user, is_default=True).update(is_default=False)
    
    # Bu manzilni asosiy deb belgilash
    address.is_default = True
    address.save()
    
    messages.success(request, f'"{address.title}" asosiy manzil sifatida belgilandi.')
    return redirect('accounts:address_list')


@login_required
def dashboard_view(request):
    """Foydalanuvchi boshqaruv paneli"""
    user = request.user
    profile = getattr(user, 'profile', None)
    
    # Statistika
    stats = {
        'addresses_count': UserAddress.objects.filter(user=user).count(),
        'default_address': UserAddress.objects.filter(user=user, is_default=True).first(),
        'last_login': user.last_login,
        'date_joined': user.date_joined,
    }
    
    context = {
        'user': user,
        'profile': profile,
        'stats': stats,
    }
    return render(request, 'accounts/dashboard.html', context)


def user_profile_public_view(request, username):
    """Foydalanuvchining ommaviy profili"""
    user = get_object_or_404(User, username=username, is_active=True)
    profile = getattr(user, 'profile', None)
    
    context = {
        'profile_user': user,
        'profile': profile,
    }
    return render(request, 'accounts/profile_public.html', context)


@require_http_methods(["POST"])
def check_username_availability(request):
    """Foydalanuvchi nomi mavjudligini tekshirish (AJAX)"""
    username = request.POST.get('username', '')
    
    if len(username) < 3:
        return JsonResponse({'available': False, 'message': 'Foydalanuvchi nomi kamida 3 ta belgidan iborat bo\'lishi kerak.'})
    
    if User.objects.filter(username=username).exists():
        return JsonResponse({'available': False, 'message': 'Bu foydalanuvchi nomi allaqachon ishlatilgan.'})
    
    return JsonResponse({'available': True, 'message': 'Foydalanuvchi nomi mavjud.'})


@require_http_methods(["POST"])
def check_email_availability(request):
    """Email mavjudligini tekshirish (AJAX)"""
    email = request.POST.get('email', '')
    
    if not email:
        return JsonResponse({'available': False, 'message': 'Email manzilni kiriting.'})
    
    if User.objects.filter(email=email).exists():
        return JsonResponse({'available': False, 'message': 'Bu email manzil allaqachon ishlatilgan.'})
    
    return JsonResponse({'available': True, 'message': 'Email manzil mavjud.'})
