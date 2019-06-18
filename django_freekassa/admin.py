from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Refill, FundsOut


@admin.register(Refill)
class RefillsAdmin(admin.ModelAdmin):
    list_display = ['id', 'date', 'user', 'sum', 'success']
    ordering = ['date']
    readonly_fields = ['id', 'date', 'user', 'sum']


@admin.register(FundsOut)
class WithdrawalAdmin(admin.ModelAdmin):
    list_display = ['created', 'user', 'amount', 'card_type', 'card_number', 'status']
    list_filter = ['status', 'card_type']

#     actions = ['make_active', 'make_inactive']
#
#     def make_active(modeladmin, request, queryset):
#         queryset.update(active=True)
#     make_active.short_description = "Make visible."
#
#     def make_inactive(modeladmin, request, queryset):
#         queryset.update(active=False)
#     make_active.short_description = "Make inactive."
