from django.urls import path
from . import views
from .views import CustomLoginView, CustomLogoutView

app_name = 'accounts'

urlpatterns = [
    # Authentication URLs
    path('login/', CustomLoginView.as_view(), name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    
    # Profile URLs
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/password/', views.change_password_view, name='change_password'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    
    # Address Management URLs
    path('addresses/', views.address_list_view, name='address_list'),
    path('addresses/create/', views.address_create_view, name='address_create'),
    path('addresses/<int:pk>/edit/', views.address_edit_view, name='address_edit'),
    path('addresses/<int:pk>/delete/', views.address_delete_view, name='address_delete'),
    path('addresses/<int:pk>/set-default/', views.set_default_address_view, name='set_default_address'),
    
    # Public Profile URLs
    path('user/<str:username>/', views.user_profile_public_view, name='profile_public'),
    
    # AJAX URLs
    path('check-username/', views.check_username_availability, name='check_username'),
    path('check-email/', views.check_email_availability, name='check_email'),
]