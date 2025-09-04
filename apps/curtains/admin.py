from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Count
from django.urls import reverse
from django.utils.safestring import mark_safe
from apps.curtains.models import Category, Color, Curtain, CurtainImage


class CurtainImageInline(admin.TabularInline):
    model = CurtainImage
    extra = 1
    fields = ('image', 'alt_text', 'is_main', 'order', 'image_preview')
    readonly_fields = ('image_preview',)
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.image.url
            )
        return "Rasm yo'q"
    image_preview.short_description = 'Oldindan ko\'rish'


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'curtains_count', 'created_date')
    list_display_links = ('id', 'title')
    list_filter = ('created_date',)
    search_fields = ('title',)
    date_hierarchy = 'created_date'
    list_per_page = 25
    ordering = ('-created_date',)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _curtains_count=Count("curtains", distinct=True)
        )
        return queryset

    def curtains_count(self, obj):
        count = obj._curtains_count
        url = (
            reverse("admin:curtains_curtain_changelist")
            + "?"
            + f"category__id__exact={obj.id}"
        )
        return format_html('<a href="{}">{} ta parda</a>', url, count)
    curtains_count.short_description = 'Pardalar soni'
    curtains_count.admin_order_field = '_curtains_count'


@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'color_preview', 'curtains_count', 'created_date')
    list_display_links = ('id', 'title')
    list_filter = ('created_date',)
    search_fields = ('title', 'hex_code')
    date_hierarchy = 'created_date'
    list_per_page = 25
    ordering = ('title',)
    fields = ('title', 'hex_code', 'created_date')
    readonly_fields = ('created_date',)
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(
            _curtains_count=Count("curtains", distinct=True)
        )
        return queryset
    
    def color_preview(self, obj):
        if obj.hex_code:
            return format_html(
                '<div style="width: 30px; height: 30px; background-color: {}; border: 1px solid #ccc; border-radius: 3px;"></div>',
                obj.hex_code
            )
        return "Rang kodi yo'q"
    color_preview.short_description = 'Rang'
    
    def curtains_count(self, obj):
        count = obj._curtains_count
        url = (
            reverse("admin:curtains_curtain_changelist")
            + "?"
            + f"colors__id__exact={obj.id}"
        )
        return format_html('<a href="{}">{} ta parda</a>', url, count)
    curtains_count.short_description = 'Pardalar soni'
    curtains_count.admin_order_field = '_curtains_count'


@admin.register(Curtain)
class CurtainAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'title', 'category', 'price_display', 'status', 
        'is_featured', 'is_active', 'views', 'stock_quantity', 'created_date'
    )
    list_display_links = ('id', 'title')
    list_filter = (
        'status', 'is_featured', 'is_active', 'fabric_type', 
        'category', 'created_date', 'modified_date'
    )
    list_editable = ('is_featured', 'is_active', 'status', 'stock_quantity')
    search_fields = ('title', 'content', 'category__title')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'created_date'
    list_per_page = 25
    ordering = ('-created_date',)
    save_on_top = True
    actions = ['make_featured', 'remove_featured', 'make_active', 'make_inactive', 'mark_available']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('title', 'slug', 'content', 'category')
        }),
        ('Narx va chegirma', {
            'fields': ('price', 'discount_price', 'stock_quantity')
        }),
        ('Xususiyatlar', {
            'fields': ('colors', 'fabric_type', 'width', 'height')
        }),
        ('Holat va ko\'rsatish', {
            'fields': ('status', 'is_featured', 'is_active')
        }),
        ('Statistika', {
            'fields': ('views', 'created_date', 'modified_date'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('views', 'created_date', 'modified_date')
    filter_horizontal = ('colors',)
    inlines = [CurtainImageInline]
    
    def price_display(self, obj):
        if obj.is_on_sale:
            return format_html(
                '<span style="text-decoration: line-through; color: #999;">{} so\'m</span> '
                '<span style="color: #e74c3c; font-weight: bold;">{} so\'m</span>',
                f'{obj.price:,}', f'{obj.discount_price:,}'
            )
        return format_html('{} so\'m', f'{obj.price:,}')
    price_display.short_description = 'Narx'
    
    def make_featured(self, request, queryset):
        count = queryset.update(is_featured=True)
        self.message_user(request, f'{count} ta parda asosiyga qo\'shildi.')
    make_featured.short_description = 'Tanlangan pardalarni asosiyga qo\'shish'
    
    def remove_featured(self, request, queryset):
        count = queryset.update(is_featured=False)
        self.message_user(request, f'{count} ta parda asosiydan olib tashlandi.')
    remove_featured.short_description = 'Tanlangan pardalarni asosiydan olib tashlash'
    
    def make_active(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} ta parda faollashtirildi.')
    make_active.short_description = 'Tanlangan pardalarni faollashtirish'
    
    def make_inactive(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} ta parda nofaol qilindi.')
    make_inactive.short_description = 'Tanlangan pardalarni nofaol qilish'
    
    def mark_available(self, request, queryset):
        count = queryset.update(status='available')
        self.message_user(request, f'{count} ta parda mavjud deb belgilandi.')
    mark_available.short_description = 'Tanlangan pardalarni mavjud deb belgilash'


@admin.register(CurtainImage)
class CurtainImageAdmin(admin.ModelAdmin):
    list_display = ('id', 'curtain', 'image_preview', 'is_main', 'order', 'created_date')
    list_display_links = ('id', 'curtain')
    list_filter = ('is_main', 'created_date', 'curtain__category')
    list_editable = ('is_main', 'order')
    search_fields = ('curtain__title', 'alt_text')
    date_hierarchy = 'created_date'
    list_per_page = 25
    ordering = ('curtain', 'order')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover;" />',
                obj.image.url
            )
        return "Rasm yo'q"
    image_preview.short_description = 'Oldindan ko\'rish'
