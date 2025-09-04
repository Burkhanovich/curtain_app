from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import Order, OrderItem, OrderStatusHistory


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['created_date', 'get_total_price']
    fields = ['curtain', 'quantity', 'unit_price', 'custom_width', 'custom_height', 
             'custom_notes', 'get_total_price', 'created_date']
    
    def get_total_price(self, obj):
        if obj.id:
            return format_html(
                '<strong>{} so\'m</strong>',
                f'{obj.get_total_price():,}'
            )
        return '-'
    get_total_price.short_description = 'Jami narx'


class OrderStatusHistoryInline(admin.TabularInline):
    model = OrderStatusHistory
    extra = 0
    readonly_fields = ['old_status', 'new_status', 'changed_by', 'created_date']
    fields = ['old_status', 'new_status', 'changed_by', 'comment', 'created_date']
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    inlines = [OrderItemInline, OrderStatusHistoryInline]
    
    list_display = ['order_number', 'customer_name', 'customer_phone', 'get_status_badge', 
                   'get_total_amount_display', 'get_items_count', 'created_date', 'processed_by']
    
    list_filter = ['status', 'created_date', 'confirmed_date', 'processed_by']
    
    search_fields = ['order_number', 'customer_name', 'customer_phone', 'customer_address']
    
    readonly_fields = ['order_number', 'created_date', 'updated_date', 'get_total_amount_display', 
                      'get_items_count']
    
    fieldsets = (
        ('Buyurtma Ma\'lumotlari', {
            'fields': ('order_number', 'status', 'processed_by')
        }),
        ('Mijoz Ma\'lumotlari', {
            'fields': ('user', 'customer_name', 'customer_phone', 'customer_address')
        }),
        ('Qo\'shimcha Ma\'lumotlar', {
            'fields': ('notes',)
        }),
        ('Statistika', {
            'fields': ('get_total_amount_display', 'get_items_count'),
            'classes': ('collapse',)
        }),
        ('Vaqt Ma\'lumotlari', {
            'fields': ('created_date', 'updated_date', 'confirmed_date'),
            'classes': ('collapse',)
        }),
    )
    
    date_hierarchy = 'created_date'
    ordering = ['-created_date']
    
    actions = ['mark_as_confirmed', 'mark_as_in_progress', 'mark_as_ready', 'mark_as_delivered']
    
    def get_status_badge(self, obj):
        color = obj.get_status_display_color()
        return format_html(
            '<span style="background: {}; color: white; padding: 4px 8px; '
            'border-radius: 12px; font-size: 11px; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    get_status_badge.short_description = 'Holat'
    get_status_badge.admin_order_field = 'status'
    
    def get_total_amount_display(self, obj):
        total = obj.get_total_amount()
        return format_html('<strong>{} so\'m</strong>', f'{total:,}')
    get_total_amount_display.short_description = 'Jami summa'
    
    def get_items_count(self, obj):
        count = obj.get_total_items_count()
        return f'{count} ta'
    get_items_count.short_description = 'Mahsulotlar soni'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'processed_by'
        ).prefetch_related('items__curtain')
    
    # Bulk actions
    def mark_as_confirmed(self, request, queryset):
        updated = queryset.filter(status='pending').update(status='confirmed')
        self.message_user(request, f'{updated} ta buyurtma tasdiqlandi.')
    mark_as_confirmed.short_description = 'Tanlangan buyurtmalarni tasdiqlash'
    
    def mark_as_in_progress(self, request, queryset):
        updated = queryset.filter(status='confirmed').update(status='in_progress')
        self.message_user(request, f'{updated} ta buyurtma ishga tushirildi.')
    mark_as_in_progress.short_description = 'Tanlangan buyurtmalarni ishga tushirish'
    
    def mark_as_ready(self, request, queryset):
        updated = queryset.filter(status='in_progress').update(status='ready')
        self.message_user(request, f'{updated} ta buyurtma tayyor deb belgilandi.')
    mark_as_ready.short_description = 'Tanlangan buyurtmalarni tayyor deb belgilash'
    
    def mark_as_delivered(self, request, queryset):
        updated = queryset.filter(status='ready').update(status='delivered')
        self.message_user(request, f'{updated} ta buyurtma yetkazildi deb belgilandi.')
    mark_as_delivered.short_description = 'Tanlangan buyurtmalarni yetkazilgan deb belgilash'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'curtain', 'quantity', 'unit_price', 'get_total_price', 
                   'get_custom_size', 'created_date']
    
    list_filter = ['created_date', 'curtain__category']
    
    search_fields = ['order__order_number', 'order__customer_name', 'curtain__title']
    
    readonly_fields = ['created_date', 'get_total_price']
    
    fieldsets = (
        ('Asosiy Ma\'lumotlar', {
            'fields': ('order', 'curtain', 'quantity', 'unit_price', 'get_total_price')
        }),
        ('Maxsus O\'lchamlar', {
            'fields': ('custom_width', 'custom_height', 'custom_notes'),
            'classes': ('collapse',)
        }),
        ('Vaqt Ma\'lumotlari', {
            'fields': ('created_date',),
            'classes': ('collapse',)
        }),
    )
    
    def get_total_price(self, obj):
        return format_html('<strong>{} so\'m</strong>', f'{obj.get_total_price():,}')
    get_total_price.short_description = 'Jami narx'
    
    def get_custom_size(self, obj):
        if obj.custom_width or obj.custom_height:
            return f"{obj.custom_width or '?'} x {obj.custom_height or '?'} sm"
        return 'Standart'
    get_custom_size.short_description = 'O\'lcham'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'order', 'curtain'
        )


@admin.register(OrderStatusHistory)
class OrderStatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['order', 'old_status', 'new_status', 'changed_by', 'created_date']
    
    list_filter = ['old_status', 'new_status', 'created_date', 'changed_by']
    
    search_fields = ['order__order_number', 'order__customer_name', 'comment']
    
    readonly_fields = ['created_date']
    
    date_hierarchy = 'created_date'
    
    ordering = ['-created_date']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'order', 'changed_by'
        )
    
    def has_add_permission(self, request):
        # Faqat order o'zgartirilganda avtomatik yaratilsin
        return False
