from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = (
        "Выгружает фикстуры (groups, users, courses, lessons, payments) в ./fixtures/"
    )

    def handle(self, *args, **kwargs):
        out = Path("fixtures")
        out.mkdir(exist_ok=True)
        User = get_user_model()
        user_label = f"{User._meta.app_label}.{User._meta.object_name}"

        call_command(
            "dumpdata",
            "auth.group",
            natural_foreign=True,
            natural_primary=True,
            indent=2,
            output=str(out / "001_groups.json"),
        )
        call_command(
            "dumpdata", user_label, indent=2, output=str(out / "010_users.json")
        )
        call_command(
            "dumpdata", "lms.Course", indent=2, output=str(out / "100_courses.json")
        )
        call_command(
            "dumpdata", "lms.Lesson", indent=2, output=str(out / "110_lessons.json")
        )
        call_command(
            "dumpdata", "users.Payment", indent=2, output=str(out / "120_payments.json")
        )

        self.stdout.write(self.style.SUCCESS("Фикстуры выгружены в ./fixtures/"))
