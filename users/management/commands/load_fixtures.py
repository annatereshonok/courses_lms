from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command

ORDER = [
    "001_groups.json",
    "010_users.json",
    "100_courses.json",
    "110_lessons.json",
    "120_payments.json",
]


class Command(BaseCommand):
    help = "Загружает фикстуры из ./fixtures/ в БД."

    def handle(self, *args, **kwargs):
        base = Path("fixtures")
        if not base.exists():
            self.stderr.write("Папка ./fixtures не найдена.")
            return

        for name in ORDER:
            path = base / name
            if not path.exists():
                self.stdout.write(f"Пропускаю {name} (нет файла).")
                continue
            call_command("loaddata", str(path))
            self.stdout.write(f"Загружено: {name}")

        self.stdout.write(self.style.SUCCESS("Все доступные фикстуры загружены."))
