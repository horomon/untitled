from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _

from .models import *


@admin.register(InvestPlan)
class PlansAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['plan_name', 'min_lim', 'max_lim', 'period', 'rate']}),
        ('Active', {'fields':['active']})

    ]
    list_display = ['plan_name', 'period', 'rate', 'active']
    ordering = ['period']
    actions = ['make_active', 'make_inactive']

    def make_active(modeladmin, request, queryset):
        queryset.update(active=True)
    make_active.short_description = _("Make visible.")

    def make_inactive(modeladmin, request, queryset):
        queryset.update(active=False)
    make_inactive.short_description = _("Make inactive.")


@admin.register(InvestActive)
class ActivesAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'start_date', 'invested')


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, )
    list_display = ('username', 'email', 'get_balance', 'is_staff')
    list_select_related = ('profile',)

    def get_balance(self, instance):
        return instance.profile.balance

    get_balance.short_description = 'balance'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)

@admin.register(Contacts)
class ContactsAdmin(admin.ModelAdmin):
    list_display = ('element', 'data')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)
