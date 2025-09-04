from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Mijoz uchun URL'lar
    path('quick-order/<int:curtain_id>/', views.quick_order_view, name='quick_order'),
    path('success/<str:order_number>/', views.order_success_view, name='order_success'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    path('order/<str:order_number>/', views.order_detail_view, name='order_detail'),
    path('cancel/<str:order_number>/', views.cancel_order_view, name='cancel_order'),
    
    # Staff/Admin uchun URL'lar
    path('management/', views.orders_management_view, name='orders_management'),
    path('update-status/<int:order_id>/', views.update_order_status_view, name='update_status'),
    path('api/stats/', views.order_stats_api_view, name='order_stats_api'),
]