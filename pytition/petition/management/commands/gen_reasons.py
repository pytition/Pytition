from django.core.management.base import BaseCommand
from petition.models import ModerationReason, MonitoringReason
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    """Generate moderation and monitoring reasons

    ./manage.py gen_reasons
    """
    help = 'Generate moderation and monitoring reasons'

    def handle(self, *args, **options):
        mod_created = False
        mon_created = False

        # The keys are the constants linked to texts that detail moderation and monitoring reasons in base.py. This is done to allow traduction of the texts.
        keys = ["owner_petition_number", "owner_monpetition_number", "owner_signature_number", "petition_inappropriate", "petition_spam", "signature_number", "signature_variation", "signature_unconfirmed", "signature_creation", "manual_moderation"]

        # The other keys correspond to moderation and monitoring reasons we don't want to involve the user in. This only concerns the admin therefore visible = False.
        for key in keys:
            # Creation or update of moderation reasons
            if not(key == "petition_inappropriate") and not(key == "petition_spam"):
                try:
                    mod_reason = ModerationReason.objects.get(msg=key)
                    if mod_reason.visible:
                        mod_reason.visible = False

                except:
                    mod_reason = ModerationReason.objects.create(msg=key, visible=False)
                    mod_created = True
                mod_reason.save()

             # Inappropriate or spam content is the only moderation reason we want to be visible when a user reports a petition to moderation.            
            else:
                    try:
                        mod_reason = ModerationReason.objects.get(msg=key)
                        if not(mod_reason.visible):
                                mod_reason.visible = True

                    except:
                        mod_reason = ModerationReason.objects.create(msg=key)
                        mod_created = True
                    
                    mod_reason.save()
                
            if mod_created:
                    logger.info("%s Moderation reason created", mod_reason)
            else:
                logger.info("%s Moderation reason already created", mod_reason)

            # Creation or update of monitoring reasons.
            try:
                mon_reason = MonitoringReason.objects.get(msg=key)
                if mon_reason.visible:
                    mon_reason.visible = False
          
            except:
                mon_reason = MonitoringReason.objects.create(msg=key, visible=False)
                mon_created = True
            mon_reason.save()

            if mon_created:
                logger.info("%s Monitoring reason created", mon_reason)
            else:
                logger.info("%s Monitoring reason already created", mon_reason)
