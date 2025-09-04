from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Maxsus foydalanuvchi modeli"""
    
    # Qo'shimcha maydonlar
    phone = models.CharField(_('Telefon raqami'), max_length=20, blank=True, null=True)
    address = models.TextField(_('Manzil'), blank=True, null=True)
    birth_date = models.DateField(_('Tug\'ilgan sana'), blank=True, null=True)
    avatar = models.ImageField(_('Profil rasmi'), upload_to='avatars/', blank=True, null=True)
    
    # Sozlamalar
    email_notifications = models.BooleanField(_('Email xabarnomalar'), default=True)
    sms_notifications = models.BooleanField(_('SMS xabarnomalar'), default=False)
    
    # Metadata
    created_at = models.DateTimeField(_('Yaratilgan vaqt'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Yangilangan vaqt'), auto_now=True)
    
    class Meta:
        verbose_name = _('Foydalanuvchi')
        verbose_name_plural = _('Foydalanuvchilar')
        db_table = 'accounts_user'
        ordering = ['-date_joined']
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        """To'liq ismni qaytarish"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def get_short_name(self):
        """Qisqa ismni qaytarish"""
        return self.first_name or self.username


class UserProfile(models.Model):
    """Foydalanuvchi profili qo'shimcha ma'lumotlari"""
    
    GENDER_CHOICES = [
        ('M', _('Erkak')),
        ('F', _('Ayol')),
        ('O', _('Boshqa')),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    gender = models.CharField(_('Jinsi'), max_length=1, choices=GENDER_CHOICES, blank=True)
    bio = models.TextField(_('Haqida'), max_length=500, blank=True)
    website = models.URLField(_('Veb-sayt'), blank=True)
    facebook = models.URLField(_('Facebook'), blank=True)
    instagram = models.URLField(_('Instagram'), blank=True)
    telegram = models.CharField(_('Telegram'), max_length=100, blank=True)
    
    # Biznes ma'lumotlari
    is_business = models.BooleanField(_('Biznes foydalanuvchi'), default=False)
    company_name = models.CharField(_('Kompaniya nomi'), max_length=200, blank=True)
    tax_id = models.CharField(_('Soliq ID'), max_length=50, blank=True)
    
    class Meta:
        verbose_name = _('Foydalanuvchi profili')
        verbose_name_plural = _('Foydalanuvchi profillari')
        db_table = 'accounts_user_profile'
    
    def __str__(self):
        return f"{self.user.username} - Profile"


class UserAddress(models.Model):
    """Foydalanuvchi manzillari"""
    
    ADDRESS_TYPES = [
        ('home', _('Uy manzili')),
        ('work', _('Ish manzili')),
        ('other', _('Boshqa')),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    type = models.CharField(_('Manzil turi'), max_length=10, choices=ADDRESS_TYPES, default='home')
    title = models.CharField(_('Manzil nomi'), max_length=100)
    address_line_1 = models.CharField(_('Manzil 1-qator'), max_length=255)
    address_line_2 = models.CharField(_('Manzil 2-qator'), max_length=255, blank=True)
    city = models.CharField(_('Shahar'), max_length=100)
    region = models.CharField(_('Viloyat'), max_length=100)
    postal_code = models.CharField(_('Pochta indeksi'), max_length=20, blank=True)
    country = models.CharField(_('Mamlakat'), max_length=100, default='Uzbekistan')
    
    is_default = models.BooleanField(_('Asosiy manzil'), default=False)
    created_at = models.DateTimeField(_('Yaratilgan vaqt'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Foydalanuvchi manzili')
        verbose_name_plural = _('Foydalanuvchi manzillari')
        db_table = 'accounts_user_address'
        ordering = ['-is_default', '-created_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"
    
    def save(self, *args, **kwargs):
        # Agar bu manzil asosiy deb belgilansa, boshqalarini asosiy emas deb belgilash
        if self.is_default:
            UserAddress.objects.filter(
                user=self.user, 
                is_default=True
            ).exclude(id=self.id).update(is_default=False)
        super().save(*args, **kwargs)
