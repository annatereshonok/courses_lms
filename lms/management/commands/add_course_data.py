from django.core.management.base import BaseCommand
from lms.models import Lesson, Course
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = "Заполняет базу тестовыми курсами и уроками"

    def handle(self, *args, **kwargs):
        # Чистим данные
        Lesson.objects.all().delete()
        Course.objects.all().delete()
        self.stdout.write(self.style.WARNING("Все уроки и курсы удалены."))

        # Создаём суперпользователя
        owner, created = User.objects.get_or_create(email="admin@mail.ru")
        if created:
            owner.set_password("admin123")
            owner.is_staff = True
            owner.is_superuser = True
            owner.save()
            self.stdout.write(self.style.SUCCESS("👤 Пользователь admin@mail.ru создан"))
        else:
            self.stdout.write(self.style.SUCCESS("👤 Пользователь admin@mail.ru уже существует"))

        # --- Курсы ---
        course_data = [
            {
                "name": "Backend",
                "description": "Основы серверной разработки: Django, DRF, БД, тесты, деплой.",
                "preview": "images/backend.png"
            },
            {
                "name": "Frontend",
                "description": "Современный фронтенд: HTML/CSS, JS/TS, React, сборка, SPA.",
                "preview": "images/frontend.png"
            },
            {
                "name": "Data Science",
                "description": "Аналитика и ML: Python, NumPy/Pandas, визуализация, модели.",
                "preview": "images/ds.png"
            },
        ]

        courses = {}
        for c in course_data:
            course = Course.objects.create(**c)
            courses[course.name] = course
            self.stdout.write(self.style.SUCCESS(f"✅ Курс создан: {course.name}"))

        # --- Уроки ---
        lessons_data = [
            # Backend
            {
                "name": "Введение в Django",
                "description": "Структура проекта, приложения, настройки, модели и миграции.",
                "video_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
                "course": courses["Backend"],
            },
            {
                "name": "Django REST Framework",
                "description": "Сериализаторы, ViewSets, роутеры, аутентификация, permissions.",
                "video_url": "https://www.youtube.com/watch?v=4D3N2Wb2G9U",
                "course": courses["Backend"],
            },
            {
                "name": "Тестирование и деплой",
                "description": "pytest, coverage, CI, контейнеризация и деплой на сервер.",
                "video_url": "https://www.youtube.com/watch?v=9bZkp7q19f0",
                "course": courses["Backend"],
            },

            # Frontend
            {
                "name": "HTML/CSS базово",
                "description": "Семантика HTML, современный CSS, адаптивность и сетки.",
                "video_url": "https://www.youtube.com/watch?v=UB1O30fR-EE",
                "course": courses["Frontend"],
            },
            {
                "name": "JavaScript основы",
                "description": "Типы, функции, замыкания, DOM, события, fetch.",
                "video_url": "https://www.youtube.com/watch?v=W6NZfCO5SIk",
                "course": courses["Frontend"],
            },
            {
                "name": "React и SPA",
                "description": "Компоненты, состояние, роутинг, хуки, сборка проекта.",
                "video_url": "https://www.youtube.com/watch?v=Ke90Tje7VS0",
                "course": courses["Frontend"],
            },

            # Data Science
            {
                "name": "Python для анализа данных",
                "description": "NumPy, Pandas, загрузка/очистка данных, базовые операции.",
                "video_url": "https://www.youtube.com/watch?v=vmEHCJofslg",
                "course": courses["Data Science"],
            },
            {
                "name": "Визуализация",
                "description": "Matplotlib, Plotly: линейные графики, гистограммы, боксплоты.",
                "video_url": "https://www.youtube.com/watch?v=3Xc3CA655Y4",
                "course": courses["Data Science"],
            },
            {
                "name": "Введение в ML",
                "description": "Train/test split, метрики, линейные модели, деревья решений.",
                "video_url": "https://www.youtube.com/watch?v=GJo-4FfR2VU",
                "course": courses["Data Science"],
            },
        ]

        for data in lessons_data:
            lesson = Lesson.objects.create(**data)
            self.stdout.write(self.style.SUCCESS(f"✅ Урок создан: {lesson.name} → {lesson.course.name}"))

        self.stdout.write(self.style.SUCCESS("🎉 База успешно заполнена!"))
