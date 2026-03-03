from django.core.management.base import BaseCommand
from petition.models import Organization, Permission

### Command to launch with cron to remove permissions of moderated users in organizations ###
class Command(BaseCommand):
    help = "launch cron script to delete permissions of moderated users in the organizations."

    def handle(self, *args, **options):
        organizations = Organization.objects.all()
        for org in organizations:
            for member in org.members.all():
                # If a member is moderated, they lose all permissions in the organization
                if member.moderated:
                    perm = Permission.objects.get(
                    organization=org,
                    user=member
                    )
                    perm.set_all(False)

                else:
                    pass