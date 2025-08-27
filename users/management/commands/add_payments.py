from decimal import Decimal
import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import Payment
from lms.models import Course, Lesson


class Command(BaseCommand):
    help = "Создаёт тестовые платежи для курсов/уроков (ровно один таргет: курс ИЛИ урок)."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Удалить все платежи перед созданием",
        )
        parser.add_argument(
            "--count",
            type=int,
            default=6,
            help="Сколько платежей создать (по умолчанию 6)",
        )
        parser.add_argument(
            "--user",
            type=str,
            default="admin@mail.ru",
            help="Email пользователя, на которого будут оформлены платежи (создастся при отсутствии)",
        )

    def handle(self, *args, **options):
        # 1) Чистим старые платежи
        if options["flush"]:
            Payment.objects.all().delete()
            self.stdout.write(self.style.WARNING("🧹 Все платежи удалены."))

        # 2) Пользователь-владелец платежей
        User = get_user_model()
        owner, created = User.objects.get_or_create(
            email=options["user"],
            defaults={"is_staff": True, "is_superuser": True},
        )
        if created:
            owner.set_password("admin123")
            owner.save()
            self.stdout.write(self.style.SUCCESS(f"👤 Создан пользователь {owner.email}"))
        else:
            self.stdout.write(self.style.SUCCESS(f"👤 Используем пользователя {owner.email}"))

        courses = list(Course.objects.all())
        lessons = list(Lesson.objects.all())

        if not courses:
            demo_course = Course.objects.create(
                name="Demo Backend",
                description="Временный курс для демо-платежей",
            )
            courses.append(demo_course)
            self.stdout.write(self.style.WARNING("⚠️ Курсов не было — создан демо-курс."))

        if not lessons:
            base_course = courses[0]
            demo_lesson = Lesson.objects.create(
                name="Введение",
                description="Демо-урок",
                video_url="https://example.com/intro",
                course=base_course,
            )
            lessons.append(demo_lesson)
            self.stdout.write(self.style.WARNING("⚠️ Уроков не было — создан демо-урок."))

        # 4) Генерация платежей
        amounts = [Decimal("990.00"), Decimal("1490.00"), Decimal("1990.00"), Decimal("2490.00")]
        methods = [code for code, _ in Payment.PAYMENT_CHOICE]

        created_count = 0
        for i in range(options["count"]):
            # Выбираем цель: курс ИЛИ урок (ровно одно)
            pick_course = random.choice([True, False]) if (courses and lessons) else bool(courses)
            if pick_course:
                course = random.choice(courses)
                lesson = None
                target_label = f"Курс: {course.name}"
            else:
                course = None
                lesson = random.choice(lessons)
                target_label = f"Урок: {lesson.name}"

            paid_at = timezone.now() - timezone.timedelta(
                days=random.randint(0, 30),
                hours=random.randint(0, 23),
                minutes=random.randint(0, 59),
            )

            p = Payment.objects.create(
                user=owner,
                paid_at=paid_at,
                course=course,
                lesson=lesson,
                amount=random.choice(amounts),
                method=random.choice(methods),
            )
            created_count += 1
            self.stdout.write(self.style.SUCCESS(
                f"💳 Платёж #{p.id}: {target_label} — {p.amount} ({p.get_method_display()})"
            ))

        self.stdout.write(self.style.SUCCESS(f"🎉 Готово! Создано платежей: {created_count}"))
