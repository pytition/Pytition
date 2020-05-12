import logging
from django.core.management import BaseCommand

from petition.models import PytitionUser, Organization, Petition

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Generate petitions for a user or an org

    ./manage.py gen_pet --user username
    > Generate a petition for user:username
    ./manage.py gen_pet --orga orgname -n 10
    > Generate 10 petitions for org:orgname
    """
    def add_arguments(self, parser):
        parser.add_argument('--user', type=str)
        parser.add_argument('--orga', type=str)
        parser.add_argument('--number', '-n', type=int, default=1)

    def handle(self, *args, **options):
        if not options['orga'] and not options['user']:
            logger.warning("You must either specify --orga or --user")
            return
        data = {
            'title': "Petition",
            'text': 'content',
            'org_twitter_handle': "@RAP_Asso",
            'published': True,
        }
        if options['orga']:
            try:
                orga = Organization.objects.get(name=options['orga'])
                data.update({'org': orga})
            except Organization.DoesNotExist:
                logger.warning("%s org not found.", options['orga'])
                return
        elif options['user']:
            try:
                user = PytitionUser.objects.get(user__username=options['user'])
                data.update({'user': user})
            except PytitionUser.DoesNotExist:
                logger.warning("%s user not found.", options['user'])
                return
        for i in range(options['number']):
            data['title'] = "Petition %d" % i
            Petition.objects.create(**data)
        logger.info("%d petitions created", options['number'])
