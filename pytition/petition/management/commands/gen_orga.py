import logging
from django.core.management.base import LabelCommand

from petition.models import Organization

logger = logging.getLogger(__name__)


class Command(LabelCommand):
    """Generate orgs by name

    ./manage.py gen_orga org1 org2 "org test"
    > Generate 3 orgs with given names
    """
    label = "Organization name"

    def handle_label(self, label, **options):
        """
        Handle the label of the given label.

        Args:
            self: (todo): write your description
            label: (str): write your description
            options: (dict): write your description
        """
        org, created = Organization.objects.get_or_create(name=label)
        if created:
            logger.info("%s organization created.", org)
        else:
            logger.info("%s organization already created.", org)
