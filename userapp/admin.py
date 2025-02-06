from django.contrib import admin
from userapp.models import User
from .models import Device, DeviceData
# Register your models here.

class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email']

class DeviceAdmin(admin.ModelAdmin):
    list_display = ('user_id', 'name', 'type', 'status', 'last_reading','created_at')

class DeviceDataAdmin(admin.ModelAdmin):
    list_display = ('device', 'type', 'value', 'timestamp')

admin.site.register(User,UserAdmin)
admin.site.register(Device, DeviceAdmin)
admin.site.register(DeviceData, DeviceDataAdmin)