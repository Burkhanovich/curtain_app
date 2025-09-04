from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import User, UserProfile, UserAddress


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('gender', 'bio', 'website', 'facebook', 'instagram', 'telegram', 
             'is_business', 'company_name', 'tax_id')


class UserAddressInline(admin.TabularInline):
    model = UserAddress
    extra = 0
    fields = ('type', 'title', 'city', 'region', 'is_default')
    readonly_fields = ('created_at',)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline, UserAddressInline)
    
    list_display = ('username', 'email', 'first_name', 'last_name', 'phone', 
                   'is_active', 'is_staff', 'date_joined', 'last_login')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'date_joined', 'last_login',
                  'email_notifications', 'sms_notifications')
    search_fields = ('username', 'first_name', 'last_name', 'email', 'phone')
    ordering = ('-date_joined',)
    
    fieldsets = UserAdmin.fieldsets + (
        ('Qo\'shimcha Ma\'lumotlar', {
            'fields': ('phone', 'address', 'birth_date', 'avatar')
        }),
        ('Xabarnoma Sozlamalari', {
            'fields': ('email_notifications', 'sms_notifications')
        }),
        ('Vaqt Ma\'lumotlari', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at', 'updated_at', 'date_joined', 'last_login')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('profile')


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'gender', 'is_business', 'company_name', 'get_social_links')
    list_filter = ('gender', 'is_business')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 
                    'bio', 'company_name', 'tax_id')
    
    fieldsets = (
        ('Asosiy Ma\'lumotlar', {
            'fields': ('user', 'gender', 'bio')
        }),
        ('Ijtimoiy Tarmoqlar', {
            'fields': ('website', 'facebook', 'instagram', 'telegram'),
            'classes': ('collapse',)
        }),
        ('Biznes Ma\'lumotlari', {
            'fields': ('is_business', 'company_name', 'tax_id'),
            'classes': ('collapse',)
        }),
    )
    
    def get_social_links(self, obj):
        links = []
        if obj.website:
            links.append('Website')
        if obj.facebook:
            links.append('Facebook')
        if obj.instagram:
            links.append('Instagram')
        if obj.telegram:
            links.append('Telegram')
        return ', '.join(links) if links else 'Yo\'q'
    
    get_social_links.short_description = 'Ijtimoiy tarmoqlar'


@admin.register(UserAddress)
class UserAddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'type', 'city', 'region', 'is_default', 'created_at')
    list_filter = ('type', 'is_default', 'city', 'region', 'country', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 
                    'title', 'address_line_1', 'city', 'region')
    ordering = ('-is_default', '-created_at')
    
    fieldsets = (
        ('Asosiy Ma\'lumotlar', {
            'fields': ('user', 'type', 'title', 'is_default')
        }),
        ('Manzil Ma\'lumotlari', {
            'fields': ('address_line_1', 'address_line_2', 'city', 'region', 
                      'postal_code', 'country')
        }),
        ('Vaqt Ma\'lumotlari', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Admin sahifasida ko'rsatish uchun sarlavhalarni o'zgartirish
admin.site.site_header = "Navoi Curtain Admin Panel"
admin.site.site_title = "Navoi Curtain Admin"
admin.site.index_title = "Boshqaruv Paneli"
