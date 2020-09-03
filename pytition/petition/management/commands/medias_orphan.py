from petition.models import Petition
from django.core.management.base import BaseCommand
from django.conf import settings
from pathlib import Path


class Command(BaseCommand):
    """find orphans medias in mediaroot
    """
    def handle(self, *args, **options):
        mediaroot = Path(settings.MEDIA_ROOT)
        all_petition = list(Petition.objects.all())
        if all_petition:
            last_petition = all_petition[-1]

        for media in mediaroot.glob('**/*.*'):
            media = str(media)
            if all_petition:
                for petition in all_petition:
                    if media in petition.text or media in petition.twitter_image:
                        break
                    if petition == last_petition:
                        print(media)
            else:
                print(media)
            
