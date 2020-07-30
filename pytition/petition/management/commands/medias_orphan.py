from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings

from petition.models import Petition



class Command(BaseCommand):
    """find orphans medias in mediaroot
    """
    def handle(self, *args, **options):
        mediaroot = Path(settings.MEDIA_ROOT)
        all_petition = Petition.objects.all()
        last_petition = all_petition[len(all_petition)-1]
        for media in mediaroot.glob('**/*.*'):
            media = str(media)
            for petition in all_petition:
                if media in petition.text or media in petition.twitter_image:
                    break
                if petition == last_petition:
                    print(media)
