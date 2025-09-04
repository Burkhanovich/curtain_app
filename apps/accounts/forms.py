from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm, UserChangeForm
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User, UserProfile, UserAddress


class CustomUserCreationForm(UserCreationForm):
    """Maxsus ro'yxatdan o'tish formasi"""
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ismingiz'
        }),
        label='Ism'
    )
    
    last_name = forms.CharField(
        max_length=30,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Familiyangiz'
        }),
        label='Familiya'
    )
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'email@example.com'
        }),
        label='Email manzil'
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+998 90 123 45 67'
        }),
        label='Telefon raqami'
    )
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'foydalanuvchi_nomi'
        }),
        label='Foydalanuvchi nomi'
    )
    
    password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parolni kiriting'
        }),
        label='Parol'
    )
    
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parolni takrorlang'
        }),
        label='Parolni tasdiqlash'
    )
    
    terms_agreement = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Foydalanish shartlarini qabul qilaman'
    )
    
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'phone', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Bu email manzil allaqachon ishlatilgan.')
        return email
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Bu foydalanuvchi nomi allaqachon ishlatilgan.')
        return username
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone')
        if commit:
            user.save()
            # UserProfile yaratish
            UserProfile.objects.create(user=user)
        return user


class CustomAuthenticationForm(AuthenticationForm):
    """Maxsus kirish formasi"""
    
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Foydalanuvchi nomi yoki email',
            'autofocus': True
        }),
        label='Foydalanuvchi nomi yoki Email'
    )
    
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parol'
        }),
        label='Parol'
    )
    
    remember_me = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Meni eslab qol'
    )
    
    def clean_username(self):
        username_or_email = self.cleaned_data.get('username')
        
        # Email bo'lsa, username ga o'tkazish
        if '@' in username_or_email:
            try:
                user = User.objects.get(email=username_or_email)
                return user.username
            except User.DoesNotExist:
                pass
        
        return username_or_email


class UserProfileForm(forms.ModelForm):
    """Foydalanuvchi profili tahrirlash formasi"""
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone', 'avatar', 'birth_date']
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ismingiz'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Familiyangiz'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'email@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+998 90 123 45 67'
            }),
            'avatar': forms.FileInput(attrs={
                'class': 'form-control',
                'accept': 'image/*'
            }),
            'birth_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        labels = {
            'first_name': 'Ism',
            'last_name': 'Familiya',
            'email': 'Email manzil',
            'phone': 'Telefon raqami',
            'avatar': 'Profil rasmi',
            'birth_date': 'Tug\'ilgan sana',
        }


class UserProfileDetailForm(forms.ModelForm):
    """Foydalanuvchi profili qo'shimcha ma'lumotlar formasi"""
    
    class Meta:
        model = UserProfile
        fields = ['gender', 'bio', 'website', 'facebook', 'instagram', 'telegram', 
                 'is_business', 'company_name', 'tax_id']
        widgets = {
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'O\'zingiz haqingizda qisqacha ma\'lumot...'
            }),
            'website': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
            'facebook': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://facebook.com/username'
            }),
            'instagram': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://instagram.com/username'
            }),
            'telegram': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '@username'
            }),
            'is_business': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'company_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Kompaniya nomi'
            }),
            'tax_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '123456789'
            }),
        }
        labels = {
            'gender': 'Jinsi',
            'bio': 'Haqida',
            'website': 'Veb-sayt',
            'facebook': 'Facebook',
            'instagram': 'Instagram',
            'telegram': 'Telegram',
            'is_business': 'Biznes foydalanuvchi',
            'company_name': 'Kompaniya nomi',
            'tax_id': 'Soliq ID',
        }


class UserAddressForm(forms.ModelForm):
    """Foydalanuvchi manzili formasi"""
    
    class Meta:
        model = UserAddress
        fields = ['type', 'title', 'address_line_1', 'address_line_2', 'city', 'region', 
                 'postal_code', 'country', 'is_default']
        widgets = {
            'type': forms.Select(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Manzil nomi (masalan: Uy, Ish)'
            }),
            'address_line_1': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ko\'cha, uy raqami'
            }),
            'address_line_2': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Kvartira, ofis raqami (ixtiyoriy)'
            }),
            'city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Shahar'
            }),
            'region': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Viloyat'
            }),
            'postal_code': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '100000'
            }),
            'country': forms.TextInput(attrs={
                'class': 'form-control',
                'value': 'Uzbekistan'
            }),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
        labels = {
            'type': 'Manzil turi',
            'title': 'Manzil nomi',
            'address_line_1': 'Manzil (1-qator)',
            'address_line_2': 'Manzil (2-qator)',
            'city': 'Shahar',
            'region': 'Viloyat',
            'postal_code': 'Pochta indeksi',
            'country': 'Mamlakat',
            'is_default': 'Asosiy manzil',
        }


class PasswordChangeForm(forms.Form):
    """Parolni o'zgartirish formasi"""
    
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Hozirgi parol'
        }),
        label='Hozirgi parol'
    )
    
    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Yangi parol'
        }),
        label='Yangi parol',
        min_length=8
    )
    
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Yangi parolni tasdiqlash'
        }),
        label='Yangi parolni tasdiqlash'
    )
    
    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)
    
    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        if not self.user.check_password(old_password):
            raise ValidationError('Hozirgi parol noto\'g\'ri.')
        return old_password
    
    def clean(self):
        cleaned_data = super().clean()
        new_password1 = cleaned_data.get('new_password1')
        new_password2 = cleaned_data.get('new_password2')
        
        if new_password1 and new_password2:
            if new_password1 != new_password2:
                raise ValidationError('Yangi parollar mos kelmadi.')
        
        return cleaned_data
    
    def save(self):
        new_password = self.cleaned_data['new_password1']
        self.user.set_password(new_password)
        self.user.save()
        return self.user