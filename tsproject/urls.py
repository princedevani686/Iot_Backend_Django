from django.contrib import admin
from django.urls import path ,include

# Create the router

# Register the viewset for device metadata with the appropriate route

urlpatterns = [
    path('', include('userapp.urls')),  # Include the URLs from userapp
    path('admin/', admin.site.urls)
 # Admin URL
]
