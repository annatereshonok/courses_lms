from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta

from .models import Course, Subscription

User = get_user_model()


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def notify_course_updated(self, course_id: int, updated_by_id: int):
    try:
        course = Course.objects.get(pk=course_id)
    except Course.DoesNotExist:
        return "course deleted"

    subscriptions = Subscription.objects.filter(course=course).select_related("user")
    recipients = [sub.user.email for sub in subscriptions]
    if not recipients:
        return "no recipients"

    updated_by = User.objects.filter(pk=updated_by_id).values_list("email", flat=True).first()

    subject = f"Обновление материалов курса: {course.name} (инициатор: {updated_by})" if updated_by else ""
    message = "Курс обновлен. Посмотрите на изменения!"
    send_mail(
        subject=subject,
        message=message,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", "no-reply@example.com"),
        recipient_list=recipients,
        fail_silently=False,
    )
    return f"sent to {len(recipients)}"


@shared_task
def deactivate_inactive_users():
    threshold = timezone.now() - timedelta(days=30)
    qs = User.objects.filter(is_active=True, last_login__lt=threshold)
    updated = qs.update(is_active=False)
    return f"deactivated {updated} users"






