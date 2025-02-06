from django.urls import path
from . import views

urlpatterns = [
    path('adminpanel/', views.adminindex, name='adminindex'),
]