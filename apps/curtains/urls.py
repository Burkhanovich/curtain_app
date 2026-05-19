from django.urls import path
from . import views

app_name = 'curtains'

urlpatterns = [
    path('', views.index, name='index'),
    path('products/', views.products, name='products'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),
    path('category/<int:pk>/', views.category_detail_view, name='category_detail'),
    path('search/autocomplete/', views.search_autocomplete, name='search_autocomplete'),
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:curtain_id>/', views.cart_add, name='cart_add'),
    path('cart/remove/<int:curtain_id>/', views.cart_remove, name='cart_remove'),
    path('cart/update/<int:curtain_id>/', views.cart_update, name='cart_update'),
    path('cart/count/', views.cart_count, name='cart_count'),
    path('checkout/', views.checkout, name='checkout'),
    path('contact/', views.contact, name='contact'),
]