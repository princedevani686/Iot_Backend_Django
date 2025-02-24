from django.urls import path 
from .views import RegisterView, LoginView ,forgot_password, reset_password, DeviceListView, DeviceDetailView  ,DeviceDataView,DeviceStatusUpdateView ,GetUserView
from django.views.generic import RedirectView
from rest_framework_simplejwt.views import TokenRefreshView
from . import views

urlpatterns = [
    path("", RedirectView.as_view(url="/register/"),), 
    path('register/', RegisterView.as_view(), name='register'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('login/', LoginView.as_view(), name='login'),
    path('user/', GetUserView.as_view(), name='get_user'),
    path('api/forgot-password/', forgot_password, name='forgot-password'),
    path('api/reset-password/<uidb64>/<token>/', reset_password, name='reset_password'),

    path('devices/', DeviceListView.as_view(), name='device-list'),
    path('devices/<int:pk>/', DeviceDetailView.as_view(), name='device-detail'),
    
    path('devices/<int:pk>/status/', DeviceStatusUpdateView.as_view(), name='device-status-update'),
    path('device_data/', DeviceDataView.as_view(), name='simulate-data'),

    path('api/devices/', views.get_devices, name='get_devices'),
    path('api/devices/filter/', views.filter_device_data, name='filter_device_data'),
    path('api/devices/chart-data/', views.get_chart_data, name='get_chart_data'),

    
]