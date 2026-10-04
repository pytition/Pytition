from django.core.management.base import BaseCommand
from petition.models import Petition
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

### Command to launch with cron to delete petitions after 3 months in the bin ###
class Command(BaseCommand):
    help = "launch cron script to delete petitions in the bin permanently after expiration."

    def handle(self, *args, **options):
        petitions_in_bin = Petition.objects.all().filter(in_bin_date__isnull=False)

        for petition in petitions_in_bin:
            limit_date = timezone.now() - timedelta(days=settings.NUMBER_OF_DAYS_FOR_EXPIRATION)
            if petition.in_bin_date <= limit_date:
                petition.delete()