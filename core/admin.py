from django.contrib import admin
from .models import *

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['fio', 'spec', 'email', 'phone_number']

@admin.register(Diler)
class DilerAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'warehouse_address', 'region', 'practice']

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'product_address', 'contact_phone', 'service_email']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'price', 'shape', 'implement', 'address']

@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ['data']

@admin.register(Shape)
class ShapeAdmin(admin.ModelAdmin):
    list_display = ['data']

@admin.register(Implement)
class ImplementAdmin(admin.ModelAdmin):
    list_display = ['data']

