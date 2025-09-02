from django.db import models
from django.conf import settings


class Course(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название")
    preview = models.ImageField(
        upload_to="images/", verbose_name="Превью", blank=True, null=True
    )
    description = models.TextField(verbose_name="Описание", blank=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="courses",
        on_delete=models.CASCADE,
        verbose_name="Создатель",
        db_index=True,
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Цена",
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Дата последнего изменения"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Курс"
        verbose_name_plural = "Курсы"


class Lesson(models.Model):
    name = models.CharField(max_length=150, verbose_name="Название")
    description = models.TextField(verbose_name="Описание", blank=True)
    preview = models.ImageField(
        upload_to="images/", verbose_name="Превью", blank=True, null=True
    )
    video_url = models.URLField(verbose_name="Ссылка на видео")
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="lessons",
        verbose_name="Курс",
        db_index=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="lessons",
        on_delete=models.CASCADE,
        verbose_name="Создатель",
        db_index=True,
    )

    def __str__(self):
        return f"{self.name} — {self.course.name}"

    class Meta:
        verbose_name = "Урок"
        verbose_name_plural = "Уроки"
        ordering = ["id"]


class Subscription(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name="subscriptions",
        on_delete=models.CASCADE,
        verbose_name="Пользователь",
        db_index=True,
    )
    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name="subscriptions",
        verbose_name="Курс",
        db_index=True,
    )

    def __str__(self):
        return f"{self.user} → {self.course}"

    class Meta:
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
