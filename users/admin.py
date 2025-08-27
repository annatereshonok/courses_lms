from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount', 'method', 'paid_at', 'course', 'lesson')
    list_filter = ('method', 'paid_at')
    search_fields = ('user__email', 'course__name', 'lesson__name')
