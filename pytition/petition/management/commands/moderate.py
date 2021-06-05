import logging
from django.core.management import BaseCommand
from django.db.models import Count

from petition.models import Petition, Moderation, ModerationReason, PytitionUser

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """Make a user join an orga

    ./manage.py moderate [-a | -l]
    > -r "some text" : adds some text as a new moderation reason
    > -l : list petitions in decreasing order of moderation demands
    > -m id : moderate a petition
    > -M username : moderate a user or Organization account
    > -d id : delete a petition
    > -D username : delete a user or Organization account
    """
    def add_arguments(self, parser):
        parser.add_argument('-r', '--add-reason', type=str)
        parser.add_argument('-R', '--delete-reason', type=str)
        parser.add_argument('-l', '--list', action='store_true')
        parser.add_argument('-p', '--moderate-petition', type=int)
        parser.add_argument('-u', '--moderate-user', type=str)
        parser.add_argument('-d', '--delete-petition', type=int)
        parser.add_argument('-D', '--delete-user', type=str)
        parser.add_argument('-P', '--unmoderate-petition', type=int)
        parser.add_argument('-U', '--unmoderate-user', type=str)

    def handle(self, *args, **options):
        if options['list']:
            petitions = Moderation.objects.values('petition').annotate(count=Count('petition')).filter(petition__moderated=False).order_by('-count')
            if len(petitions) == 0:
                return
            print("Number of moderation request: title [id : url]")
            for petition in petitions:
                p = Petition.objects.get(pk=petition['petition'])
                print("{count}: {title} [{id} : {url}]".format(count=petition['count'], title=p.title, id=p.id, url=p.url))

        if options['add_reason']:
            msg = options['add_reason']
            ModerationReason.objects.create(msg=msg)
            print("Created reason: \'{msg}\'".format(msg=msg))

        if options['delete_reason']:
            msg = options['delete_reason']
            r = ModerationReason.objects.get(msg=msg)
            r.delete()
            print("Deleted reason: \'{msg}\'".format(msg=msg))

        if options['moderate_petition']:
            id = options['moderate_petition']
            petition = Petition.objects.get(pk=id)
            title = petition.title
            petition.moderate()
            petition.save()
            print("Petition \'{title}\' moderated".format(title=title))

        if options['moderate_user']:
            username = options['moderate_user']
            user = PytitionUser.objects.get(user__username=username)
            user.moderate()
            user.save()
            print("User \'{name}\' moderated".format(name=username))

        if options['unmoderate_petition']:
            id = options['unmoderate_petition']
            petition = Petition.objects.get(pk=id)
            title = petition.title
            petition.moderate(False)
            petition.save()
            print("Petition \'{title}\' un-moderated".format(title=title))

        if options['unmoderate_user']:
            username = options['unmoderate_user']
            user = PytitionUser.objects.get(user__username=username)
            user.moderate(False)
            user.save()
            print("User \'{name}\' un-moderated".format(name=username))

        if options['delete_petition']:
            id = options['delete_petition']
            petition = Petition.objects.get(pk=id)
            title = petition.title
            petition.delete()
            print("Petition \'{title}\' deleted".format(title=title))

        if options['delete_user']:
            username = options['delete_user']
            user = PytitionUser.objects.get(user__username=username)
            user.delete()
            print("User \'{name}\' deleted".format(name=username))