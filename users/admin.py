from django.contrib import admin
from .models import Payment, CustomUser


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "amount",
        "method",
        "status",
        "paid_at",
        "course",
        "lesson",
        "stripe_session_id",
    )
    list_filter = ("method", "status", "paid_at")
    search_fields = ("user__email", "course__name", "lesson__name")


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("id", "email", "phone", "city", "group_list")

    @admin.display(description="Groups")
    def group_list(self, obj):
        return ", ".join(obj.groups.values_list("name", flat=True))
