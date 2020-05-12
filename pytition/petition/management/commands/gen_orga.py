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
        org, created = Organization.objects.get_or_create(name=label)
        if created:
            logger.info("%s organization created.", org)
        else:
            logger.info("%s organization already created.", org)
