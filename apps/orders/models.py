from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from apps.curtains.models import Curtain

User = get_user_model()


class Order(models.Model):
    """Buyurtma modeli"""
    
    STATUS_CHOICES = [
        ('pending', _('Kutilmoqda')),
        ('confirmed', _('Tasdiqlandi')),
        ('in_progress', _('Tayyorlanmoqda')),
        ('ready', _('Tayyor')),
        ('delivered', _('Yetkazildi')),
        ('cancelled', _('Bekor qilindi')),
    ]
    
    # Buyurtma ma'lumotlari
    order_number = models.CharField(_('Buyurtma raqami'), max_length=20, unique=True, blank=True)
    status = models.CharField(_('Holati'), max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Mijoz ma'lumotlari (foydalanuvchi bo'lmasa ham buyurtma berishi mumkin)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                           verbose_name=_('Foydalanuvchi'), related_name='orders')
    
    # Majburiy mijoz ma'lumotlari
    customer_name = models.CharField(_('Mijoz ismi'), max_length=100)
    customer_phone = models.CharField(_('Telefon raqami'), max_length=20)
    customer_address = models.TextField(_('Manzil'))
    
    # Qo'shimcha ma'lumotlar
    notes = models.TextField(_('Qo\'shimcha ma\'lumot'), blank=True, 
                           help_text='Mijoz tomonidan qoldirilgan qo\'shimcha ma\'lumotlar')
    
    # Vaqt ma'lumotlari
    created_date = models.DateTimeField(_('Yaratilgan vaqt'), auto_now_add=True)
    updated_date = models.DateTimeField(_('Yangilangan vaqt'), auto_now=True)
    confirmed_date = models.DateTimeField(_('Tasdiqlangan vaqt'), null=True, blank=True)
    
    # Sotuvchi ma'lumotlari
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                   related_name='processed_orders', 
                                   verbose_name=_('Kim tomonidan qaralgan'))
    
    class Meta:
        verbose_name = _('Buyurtma')
        verbose_name_plural = _('Buyurtmalar')
        db_table = 'orders_order'
        ordering = ['-created_date']
        indexes = [
            models.Index(fields=['status', 'created_date']),
            models.Index(fields=['customer_phone']),
            models.Index(fields=['order_number']),
        ]
    
    def __str__(self):
        return f"#{self.order_number} - {self.customer_name}"
    
    def save(self, *args, **kwargs):
        if not self.order_number:
            # Buyurtma raqamini avtomatik yaratish
            from datetime import datetime
            now = datetime.now()
            last_order = Order.objects.filter(
                created_date__date=now.date()
            ).order_by('-id').first()
            
            if last_order and last_order.order_number:
                # Bugungi oxirgi buyurtma raqamidan keyingisini yaratish
                try:
                    last_num = int(last_order.order_number.split('-')[-1])
                    new_num = last_num + 1
                except (ValueError, IndexError):
                    new_num = 1
            else:
                new_num = 1
            
            self.order_number = f"NC-{now.strftime('%Y%m%d')}-{new_num:03d}"
        
        super().save(*args, **kwargs)
    
    def get_total_items_count(self):
        """Jami mahsulotlar soni"""
        return self.items.aggregate(
            total=models.Sum('quantity')
        )['total'] or 0
    
    def get_total_amount(self):
        """Jami summa (taxminiy)"""
        total = 0
        for item in self.items.all():
            total += item.quantity * item.unit_price
        return total
    
    def get_status_display_color(self):
        """Status rangi admin panelda ko'rsatish uchun"""
        colors = {
            'pending': '#f39c12',      # Sariq
            'confirmed': '#3498db',    # Ko'k
            'in_progress': '#9b59b6',  # Binafsha
            'ready': '#27ae60',        # Yashil
            'delivered': '#2ecc71',    # To'q yashil
            'cancelled': '#e74c3c',    # Qizil
        }
        return colors.get(self.status, '#95a5a6')


class OrderItem(models.Model):
    """Buyurtma elementlari"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items', 
                            verbose_name=_('Buyurtma'))
    curtain = models.ForeignKey(Curtain, on_delete=models.CASCADE, verbose_name=_('Parda'))
    quantity = models.PositiveIntegerField(_('Miqdori'), default=1)
    unit_price = models.PositiveIntegerField(_('Birlik narxi'), 
                                           help_text='Buyurtma berish vaqtidagi narx')
    
    # Maxsus o'lchamlar (agar mijoz maxsus o'lcham so'rasa)
    custom_width = models.PositiveIntegerField(_('Maxsus eni (sm)'), null=True, blank=True)
    custom_height = models.PositiveIntegerField(_('Maxsus balandligi (sm)'), null=True, blank=True)
    custom_notes = models.TextField(_('Maxsus talablar'), blank=True)
    
    created_date = models.DateTimeField(_('Qo\'shilgan vaqt'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Buyurtma elementi')
        verbose_name_plural = _('Buyurtma elementlari')
        db_table = 'orders_order_item'
        unique_together = ['order', 'curtain']
    
    def __str__(self):
        return f"{self.curtain.title} x {self.quantity}"
    
    def get_total_price(self):
        """Bu elementning jami narxi"""
        return self.quantity * self.unit_price
    
    def save(self, *args, **kwargs):
        if not self.unit_price:
            # Agar narx kiritilmagan bo'lsa, pardaning hozirgi narxini olish
            self.unit_price = self.curtain.final_price
        super().save(*args, **kwargs)


class OrderStatusHistory(models.Model):
    """Buyurtma holati tarixi"""
    
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='status_history',
                            verbose_name=_('Buyurtma'))
    old_status = models.CharField(_('Oldingi holat'), max_length=20, choices=Order.STATUS_CHOICES)
    new_status = models.CharField(_('Yangi holat'), max_length=20, choices=Order.STATUS_CHOICES)
    changed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name=_('O\'zgartirgan'))
    comment = models.TextField(_('Izoh'), blank=True)
    created_date = models.DateTimeField(_('O\'zgartirilgan vaqt'), auto_now_add=True)
    
    class Meta:
        verbose_name = _('Buyurtma holati tarixi')
        verbose_name_plural = _('Buyurtma holati tarixi')
        db_table = 'orders_status_history'
        ordering = ['-created_date']
    
    def __str__(self):
        return f"#{self.order.order_number}: {self.old_status} → {self.new_status}"
