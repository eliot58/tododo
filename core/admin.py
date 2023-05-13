from django.contrib import admin
from .models import *

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    search_fields = ("fio", "email")
    list_display = ['fio', 'spec', 'email', 'phone_number', 'date_joined']

    @admin.display(ordering='user__date_joined', description='дата регистрации')
    def date_joined(self, obj):
        return obj.user.date_joined

@admin.register(Diler)
class DilerAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'warehouse_address', 'region', 'practice']

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    list_display = ['user', 'company', 'product_address', 'contact_phone', 'service_email']


class OrderFilter(admin.SimpleListFilter):
    title = ('status')

    parameter_name = 'status'

    def lookups(self, request, model_admin):
        return (
            ('active', ('active')),
            ('inactive', ('not active ')),
        )

    def queryset(self, request, queryset):

        if self.value() == 'active':
            return queryset.filter(
                isactive=True
            )
        if self.value() == 'inactive':
            return queryset.filter(
                isactive= False
            )


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_filter = (OrderFilter,)
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


@admin.register(Price)
class ImplementAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'description']


admin.site.register(Quantity)


@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    list_display = ['user', 'file']

