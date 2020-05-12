import logging
import random
import string
from django.core.management import BaseCommand

from petition.models import Petition, Signature


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Generate signatures for petitions

    ./manage.py gen_sig 1
    > Generate a random signature for Petition:1
    ./manage.py gen_sig "Petition Test" -n 10
    > Generate 10 signatures for Petition:Petition Test if unique
    """
    def add_arguments(self, parser):
        parser.add_argument('petition', type=str)
        parser.add_argument('--number', '-n', type=int, default=1)

    def handle(self, *args, **options):
        try:
            petition = Petition.objects.get(id=int(options['petition']))
        except Petition.DoesNotExist:
            logger.warning("%s petition id not found.", options['petition'])
            return
        except ValueError:
            petitions = Petition.objects.filter(title=options['petition'])
            if petitions.count() > 1:
                logger.warning(
                    "Many petition match this title: %s, choose it by id: %s",
                    options['petition'], petitions.values_list('id')
                )
                return
            if petitions.count() < 1:
                logger.warning("%s petition id not found.", options['petition'])
                return
            petition = petitions.first()

        for _ in range(options['number']):
            Signature.objects.create(
                first_name=''\
                    .join([random.choice(string.ascii_letters) for n in range(7)])\
                    .capitalize(),
                last_name=''\
                    .join([random.choice(string.ascii_letters) for n in range(7)])\
                    .capitalize(),
                email='u@test.net',
                petition=petition,
                confirmed=True
            )
        logger.info("%d signatures created.", options['number'])
