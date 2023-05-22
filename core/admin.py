from django.contrib import admin
from .models import *
from django.contrib.admin.models import LogEntry
import json

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    search_fields = ("fio", "email")
    list_display = ['fio', 'spec', 'email', 'phone_number', 'date_joined']

    @admin.display(ordering='user__date_joined', description='Дата регистрации')
    def date_joined(self, obj):
        return obj.user.date_joined
    
class CommentDilerInline(admin.StackedInline):
    model = DilerComment
    extra = 1


class CommentProviderInline(admin.StackedInline):
    model = ProviderComment
    extra = 1

@admin.register(Diler)
class DilerAdmin(admin.ModelAdmin):
    inlines = [CommentDilerInline]
    list_display = ['user', 'organization', 'warehouse_address', 'region', 'practice', 'last_login', 'date_joined']

    @admin.display(ordering='user__user__last_login', description='Дата последнего входа')
    def last_login(self, obj):
        return obj.user.user.last_login


    @admin.display(ordering='user__user__date_joined', description='Дата регистрации')
    def date_joined(self, obj):
        return obj.user.user.date_joined

@admin.register(Provider)
class ProviderAdmin(admin.ModelAdmin):
    inlines = [CommentProviderInline]
    list_display = ['user', 'company', 'product_address', 'contact_phone', 'service_email', 'last_login', 'date_joined']

    @admin.display(ordering='user__user__last_login', description='Дата последнего входа')
    def last_login(self, obj):
        return obj.user.user.last_login


    @admin.display(ordering='user__user__date_joined', description='Дата регистрации')
    def date_joined(self, obj):
        return obj.user.user.date_joined


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

class QunatityInline(admin.StackedInline):
    model = Quantity

    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_filter = (OrderFilter,)
    list_display = ['user', 'date', 'price', 'shape', 'implement', 'address']
    inlines = [QunatityInline]

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


@admin.register(Quantity)
class QuantityAdmin(admin.ModelAdmin):
    list_display = ['order', 'author', 'date_create', 'date', 'shape', 'implement', 'price', 'comment']


@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    list_display = ['user', 'file']



@admin.register(LogEntry)
class LogAdmin(admin.ModelAdmin):
    list_display = ['action_time', 'user', 'content_type', 'object_repr', 'change_message_text']

    @admin.display(ordering='change_message', description='Сообщение')
    def change_message_text(self, obj):
        try:
            data = json.loads(obj.change_message)[0]
        except:
            return ""
        return "Добавлен " + str(data["added"]) if "added" in data else "Изменен " + str(data["changed"]["fields"])