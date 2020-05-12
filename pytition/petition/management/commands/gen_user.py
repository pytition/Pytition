import logging
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """Generate a user

    ./manage.py gen_user username password -fn User -ln James
    > Generate user:username with password as password, and named User James
    """
    help = 'Create a new user'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str)
        parser.add_argument('password', type=str)
        parser.add_argument('--first-name', '-fn', dest='first_name', type=str)
        parser.add_argument('--last-name', '-ln', dest='last_name', type=str)

    def handle(self, *args, **options):
        created = False
        try:
            user = User.objects.get(username=options['username'])
            user.set_password(options['password'])
        except User.DoesNotExist:
            user = User.objects.create_user(options['username'], password=options['password'])
            created = True
        user.is_staff = True
        if options['first_name']:
            user.first_name = options['first_name']
        if options['last_name']:
            user.last_name = options['last_name']
        user.save()
        if created:
            logger.info("%s user created", user)
        else:
            logger.info("%s user already created", user)
