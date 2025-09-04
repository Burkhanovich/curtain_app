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
    path('checkout/', views.checkout, name='checkout'),
    path('contact/', views.contact, name='contact'),
]