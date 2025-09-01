from django.contrib import admin
from apps.curtains.models import Category, Color, Curtain

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_date')
    date_hierarchy = 'created_date'
    search_fields = ('title', )

@admin.register(Color)
class ColorAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'created_date')
    date_hierarchy = 'created_date'
    search_fields = ('title', )

@admin.register(Curtain)
class CurtainAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'price', )
    date_hierarchy = 'created_date'
    search_fields = ('title', 'category')
    readonly_fields = ('created_date', 'modified_date')
