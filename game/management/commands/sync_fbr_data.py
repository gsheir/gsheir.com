from django.conf import settings
from django.core.management.base import BaseCommand

from game.services.fbr_api import FBRAPIService


class Command(BaseCommand):
    help = "Sync data from FBR API"

    def add_arguments(self, parser):
        parser.add_argument(
            "--competition",
            type=int,
            default=162,
            help="Competition ID to sync",
        )

    def handle(self, *args, **options):
        competition_id = options["competition"]

        self.stdout.write(f"Database connection: {settings.DATABASES['default']}")
        self.stdout.write(f"Starting sync for competition: {competition_id}")

        fbr_service = FBRAPIService()
        fbr_service.sync_all_data(competition_id)

        self.stdout.write(
            self.style.SUCCESS(f"Successfully synced data for {competition_id}")
        )
