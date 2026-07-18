from django.core.management.base import BaseCommand
from django.utils import timezone

class Command(BaseCommand):
    help = (
        "Send daily digest. Use --force to bypass the hour check (for local testing)!"
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--force", action="store_true", help="Send immediatly notifications"
        )

    def handle(self, *args, **options):
        from users.email_digest import send_daily_notifications

        self.stdout.write(f"[{timezone.now().isoformat()}] Running digest...")
        count = send_daily_notifications(force=options["force"])
        self.stdout.write(f"Done - send to {count} user(s).")