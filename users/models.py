from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.conf import settings
from django.db import models
from django.db.models import Q
from django.core.exceptions import ValidationError
from django.utils import timezone

from lms.models import Lesson, Course


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        if not password:
            raise ValueError("Superuser must have a password.")
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True, verbose_name="Email")

    avatar = models.ImageField(
        upload_to="users_image/", verbose_name="Аватар", blank=True, null=True
    )
    phone = models.CharField(
        max_length=20, verbose_name="Телефон", blank=True, null=True
    )
    city = models.CharField(max_length=100, verbose_name="Город", blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


class Payment(models.Model):
    PAYMENT_CHOICE = [
        ("cash", "Наличные"),
        ("transfer", "Перевод на счёт"),
        ("stripe", "Stripe Checkout"),
    ]
    PAYMENT_STATUS = [
        ("pending", "Ожидает"),
        ("paid", "Оплачен"),
        ("canceled", "Отменён"),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="Пользователь",
        db_index=True,
    )
    paid_at = models.DateTimeField(
        default=timezone.now,
        verbose_name="Дата операции",
        db_index=True,
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="Курс",
        null=True,
        blank=True,
    )
    lesson = models.ForeignKey(
        Lesson,
        on_delete=models.PROTECT,
        related_name="payments",
        verbose_name="Урок",
        null=True,
        blank=True,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Сумма оплаты",
    )
    method = models.CharField(
        max_length=16,
        choices=PAYMENT_CHOICE,
        verbose_name="Способ оплаты",
    )
    status = models.CharField(
        max_length=16,
        choices=PAYMENT_STATUS,
        default="pending",
        db_index=True,
    )
    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)

    def clean(self):
        super().clean()
        if (self.course is None) == (self.lesson is None):
            raise ValidationError("Укажите либо курс, либо урок.")

    class Meta:
        verbose_name = "Платёж"
        verbose_name_plural = "Платежи"
        constraints = [
            models.CheckConstraint(
                name="payment_exactly_one_target",
                check=(
                    (Q(course__isnull=False) & Q(lesson__isnull=True))
                    | (Q(course__isnull=True) & Q(lesson__isnull=False))
                ),
            ),
        ]

    def __str__(self):
        target = self.course or self.lesson
        return f"Платёж {self.user} → {target} на {self.amount}"
