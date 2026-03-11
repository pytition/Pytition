from .utils import get_spam_detectors
from petition.models import ModerationReason, Moderation, MonitoringReason, Monitoring
from petition.helpers import send_moderation_mail, send_mail_to_moderation, send_mail_to_moderation_monitor, send_monitoring_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# controller function that launches the detectors and defines a 'spam' value between 0 and 2
# 0: not spam, 1: possible spam, 2: definite spam.
# does moderation actions depending on the value of 'spam'
def check_for_spam(petition, pytitionuser) -> None:
    moderation_reason, _ = ModerationReason.objects.get_or_create(msg="petition_inappropriate")
    monitoring_reason, _ = MonitoringReason.objects.get_or_create(msg="petition_inappropriate")
    spam = 0

    spam_detectors = list(get_spam_detectors())

    if (len(spam_detectors) == 0):
        logger.debug("No spam detectors configured.")
        return

    for detector in spam_detectors:
        logger.debug(f"Testing if petition {petition.id} is spam with detector {detector.__class__.__name__}.")
        if detector.__class__.__name__== 'AkismetSpamDetector':
            if not(settings.AKISMET_MODERATION_AUTO):
                if detector.is_spam(petition, pytitionuser) == 2:
                    spam = 1
                else:
                    spam = detector.is_spam(petition, pytitionuser)
            else:
                spam = detector.is_spam(petition, pytitionuser)
        else:
            if detector.is_spam(petition, pytitionuser) > spam:
                spam = detector.is_spam(petition, pytitionuser)

    logger.debug(f"Spam detection result for petition {petition.id} with detector {detector.__class__.__name__}: {spam} (0: not spam, 1: possible spam, 2: definite spam.).")
    
    if spam == 2:
        if not(petition.moderated):
            petition.moderate()
            petition.monitor(False)

        Moderation.objects.create(petition=petition, reason=moderation_reason)
        send_mail_to_moderation(settings.MODERATION_EMAIL, petition, moderation_reason.text, "petition")
        send_moderation_mail(pytitionuser.user.email, pytitionuser.user.username, moderation_reason.text, "petition", petition)
        logger.warning(f"Petition {petition.id} flagged as spam by detector {detector.__class__.__name__} and moderated.")

    elif spam == 1:
        if not(petition.moderated):
            petition.monitor()
            Monitoring.objects.create(petition=petition, reason=monitoring_reason, priority="strong")
            send_mail_to_moderation_monitor(settings.MODERATION_EMAIL, petition, monitoring_reason.text, "petition", "strong")
            send_monitoring_mail(pytitionuser.user.email, pytitionuser.user.username, "petition", petition, monitoring_reason.text)
            logger.warning(f"Petition {petition.id} flagged as spam by detector {detector.__class__.__name__} and monitored.")
