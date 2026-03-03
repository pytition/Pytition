from petition.models import Petition, Moderation, ModerationReason, Monitoring, MonitoringReason, Permission, Signature
from petition.helpers import send_mail_to_moderation, send_mail_to_moderation_monitor, send_monitoring_mail, send_moderation_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)

"""
Check the number of signatures and the variation of this number in an interval of a day or a week to moderate or monitor petitions.
Four types of monitoring are defined:
    - critical: the petition is moderated, emails are sent to admin and owner
    - strong: the petition is monitored with a strong priority, emails are sent to admin and user, display in admin and owner dashboard
    - average: the petition is monitored with an average priority, display in admin and owner dashboard
    - low: the petition is monitored with a low priority, display in admin
"""

# check the total number of signatures
def check_signature_number(petition):
    logger.debug(f"Checking signature number for petition {petition.id}.")
    moderation_reason, _ = ModerationReason.objects.get_or_create(msg="signature_number")
    monitoring_reason, _ = MonitoringReason.objects.get_or_create(msg="signature_number")

    # check if the number of signatures requires critical monitoring
    signature_number = petition.get_signature_number()

    if signature_number > settings.SIGNATURE_NUMBER_CRITICAL and settings.SIGNATURE_NUMBER_CRITICAL > 0:
        if petition.moderated:
            logger.debug(f"Ignoring petition {petition.id} moderation due to critical signature number {signature_number} as petition is already moderated.")
            pass
        else:
            logger.info(f"Moderating petition {petition.id} due to critical signature number {signature_number}.")
            petition.moderate()
            petition.monitor(False)
            moderation = Moderation.objects.create(petition=petition, reason=moderation_reason)
            send_mail_to_moderation(settings.MODERATION_EMAIL, petition, moderation.reason.text, "petition") 
            
            if petition.user:
                send_moderation_mail(petition.user.user.email, petition.user.user.username, moderation.reason.text, "petition", petition)
            elif petition.org:
                for member in petition.org.members.all():
                    permissions = Permission.objects.get(organization=petition.org, user=member)
                    if permissions:
                        if permissions.can_modify_permissions:
                            send_moderation_mail(member.user.email, member.user.username, moderation.reason.text, "petition", petition)
        return True

    # check if the number of signatures requires strong monitoring
    elif signature_number > settings.SIGNATURE_NUMBER_STRONG and settings.SIGNATURE_NUMBER_STRONG > 0:
        if petition.moderated or (petition.monitored and petition.monitoring.last().priority == "strong"):
            logger.debug(f"Ignoring petition {petition.id} strong monitoring due to strong signature number {signature_number} as petition is already moderated or already has a strong monitoring priority.")
            pass
        else:
            logger.info(f"Creating strong monitoring for petition {petition.id} due to strong signature number {signature_number}.")
            petition.monitor()
            monitoring = Monitoring.objects.create(petition=petition, reason=monitoring_reason, priority="strong")
            send_mail_to_moderation_monitor(settings.MODERATION_EMAIL, petition, monitoring.reason.text, "petition", "strong") 
            
            if petition.user:
                send_monitoring_mail(petition.user.user.email, petition.user.user.username, "petition", petition, monitoring.reason.text)
            elif petition.org:
                for member in petition.org.members.all():
                    permissions = Permission.objects.get(organization=petition.org, user=member)
                    if permissions:
                        if permissions.can_modify_permissions:
                            send_monitoring_mail(member.user.email, member.user.username, "petition", petition, monitoring.reason.text)
        return False

    # check if the number of signatures requires average monitoring
    elif signature_number > settings.SIGNATURE_NUMBER_AVERAGE and settings.SIGNATURE_NUMBER_AVERAGE > 0:
        if (petition.monitored and (petition.monitoring.last().priority == "strong" or petition.monitoring.last().priority == "average")) or petition.moderated:
                logger.debug(f"Ignoring petition {petition.id} average monitoring due to average signature number {signature_number} as petition is already moderated or already has a average monitoring priority.")
                return False
        else:
            logger.info(f"Creating average monitoring for petition {petition.id} due to average signature number {signature_number}.")
            petition.monitor()
            monitoring = Monitoring.objects.create(petition=petition, reason=monitoring_reason, priority="average")
            return False

    # check if the number of signatures requires low monitoring
    elif signature_number > settings.SIGNATURE_NUMBER_LOW and settings.SIGNATURE_NUMBER_LOW > 0:
        if petition.monitored or petition.moderated:
                logger.debug(f"Ignoring petition {petition.id} low monitoring due to signature number {signature_number} as petition is already moderated or already has a low monitoring priority.")
                return False
        else:
            logger.info(f"Creating low monitoring for petition {petition.id} due to average signature number {signature_number}.")
            petition.monitor()
            monitoring = Monitoring.objects.create(petition=petition, reason=monitoring_reason, priority="low")
            return False

    else:
        return False

# check the variation in the number of signatures in an interval
def check_signature_variation(petition, interval):
    logger.debug(f"Checking signature number variation for petition {petition.id} with interval {interval}.")
    moderation_reason, _ = ModerationReason.objects.get_or_create(msg="signature_variation")
    monitoring_reason, _ = MonitoringReason.objects.get_or_create(msg="signature_variation")

    # We define to which number of signatures we're going to compare today's number of signatures
    if interval == "yesterday":
        number_to_compare = petition.get_day_before_signature_number()
    elif interval == "last week":
        number_to_compare =  petition.get_week_signature_number()
    else:
        return


    petition_day_signature_number = petition.get_day_signature_number()

    # check if the variation requires critical monitoring
    if petition_day_signature_number > settings.SIGNATURE_VARIATION_CRITICAL*number_to_compare and number_to_compare != 0 and settings.SIGNATURE_VARIATION_CRITICAL > 0:
        if petition.moderated:
            logger.debug(f"Ignoring petition {petition.id} moderation due to signature number variation {petition_day_signature_number} as petition is already moderated.")
            pass
        else:
            logger.info(f"Moderating petition {petition.id} due to critical variation of signature number {petition_day_signature_number}.")
            petition.moderate()
            petition.monitor(False)
            moderation = Moderation.objects.create(petition=petition, reason=moderation_reason)
            send_mail_to_moderation(settings.MODERATION_EMAIL, petition, moderation.reason.text, "petition")
            if petition.user:
                send_moderation_mail(petition.user.user.email, petition.user.user.username, moderation.reason.text, "petition", petition)
            elif petition.org:
                for member in petition.org.members.all():
                    permissions = Permission.objects.get(organization=petition.org, user=member)
                    if permissions:
                        if permissions.can_modify_permissions:
                            send_moderation_mail(member.user.email, member.user.username, moderation.reason.text, "petition", petition)
        return True

    # check if the variation requires strong monitoring
    elif petition_day_signature_number > settings.SIGNATURE_VARIATION_STRONG*number_to_compare and number_to_compare != 0 and settings.SIGNATURE_VARIATION_STRONG > 0:
        if petition.moderated or (petition.monitored and petition.monitoring.last().priority == "strong"):
            logger.debug(f"Ignoring petition {petition.id} strong monitoring due to signature number variation {petition_day_signature_number} as petition is already moderated or already has a strong monitoring priority.")
            pass
        else:
            logger.info(f"Monitoring petition {petition.id} due to strong variation of signature number {petition_day_signature_number}.")
            petition.monitor()
            monitoring = Monitoring.objects.create(petition=petition, reason=monitoring_reason, priority="strong")
            send_mail_to_moderation_monitor(settings.MODERATION_EMAIL, petition, monitoring.reason.text, "petition", "strong") 

            if petition.user:
                send_monitoring_mail(petition.user.user.email, petition.user.user.username, "petition", petition, monitoring.reason.text)
            elif petition.org:
                for member in petition.org.members.all():
                    permissions = Permission.objects.get(organization=petition.org, user=member)
                    if permissions:
                        if permissions.can_modify_permissions:
                            send_monitoring_mail(member.user.email, member.user.username, "petition", petition, monitoring.reason.text)
        return False

    # check if the variation requires average monitoring
    elif petition_day_signature_number > settings.SIGNATURE_VARIATION_AVERAGE*number_to_compare and number_to_compare != 0 and settings.SIGNATURE_VARIATION_AVERAGE > 0:
        if (petition.monitored and (petition.monitoring.last().priority == "strong" or petition.monitoring.last().priority == "average")) or petition.moderated:
                logger.debug(f"Ignoring petition {petition.id} average monitoring due to signature number variation {petition_day_signature_number} as petition is already moderated or already has a average monitoring priority.")
                return False
        else:
            logger.info(f"Monitoring petition {petition.id} due to average variation of signature number {petition_day_signature_number}.")
            petition.monitor()
            monitoring = Monitoring.objects.create(petition=petition, reason=monitoring_reason, priority="average")
            return False
    
    # check if the variation requires low monitoring
    elif petition_day_signature_number > settings.SIGNATURE_VARIATION_LOW*number_to_compare and number_to_compare != 0 and settings.SIGNATURE_VARIATION_LOW > 0:
        if petition.monitored or petition.moderated:
                logger.debug(f"Ignoring petition {petition.id} low monitoring due to signature number variation {petition_day_signature_number} as petition is already moderated or already has a low monitoring priority.")
                return False
        else:
            logger.info(f"Monitoring petition {petition.id} due to low variation of signature number {petition_day_signature_number}.")
            petition.monitor()
            monitoring = Monitoring.objects.create(petition=petition, reason=monitoring_reason, priority="low")
            return False

    else:
        return False

# check the number of unconfirmed signatures in the last 6h
def check_unconfirmed_signatures(petition):
    logger.debug(f"Checking unconfirmed signature number for petition {petition.id}.")
    moderation_reason, _ = ModerationReason.objects.get_or_create(msg="signature_unconfirmed")
    monitoring_reason, _ = MonitoringReason.objects.get_or_create(msg="signature_unconfirmed")

    # get the number of unconfirmed signatures for the petition
    unconfirmed_signatures = Signature.objects.filter(petition = petition, confirmed=False, date__gte = timezone.now() - timedelta(hours=6))
    unconfirmed_numb = unconfirmed_signatures.count()

    # check if the number of unconfirmed signatures requires critical monitoring (=automatic moderation)
    if unconfirmed_numb > settings.UNCONFIRMED_NUMBER_CRITICAL and settings.UNCONFIRMED_NUMBER_CRITICAL > 0:
        if petition.moderated:
            logger.debug(f"Ignoring petition {petition.id} moderation due to critical number of unconfirmed signatures {unconfirmed_numb} as petition is already moderated.")
            pass
        else:
            logger.info(f"Moderating petition {petition.id} due to critical number of unconfirmed signatures {unconfirmed_numb}.")
            petition.moderate()
            petition.monitor(False)
            moderation = Moderation.objects.create(petition=petition, reason=moderation_reason)
            send_mail_to_moderation(settings.MODERATION_EMAIL, petition, moderation.reason.text, "petition") 
            
            if petition.user:
                send_moderation_mail(petition.user.user.email, petition.user.user.username, moderation.reason.text, "petition", petition)
            elif petition.org:
                for member in petition.org.members.all():
                    permissions = Permission.objects.get(organization=petition.org, user=member)
                    if permissions:
                        if permissions.can_modify_permissions:
                            send_moderation_mail(member.user.email, member.user.username, moderation.reason.text, "petition", petition)
        return True

    # check if the number of unconfirmed signatures requires strong monitoring
    elif unconfirmed_numb > settings.UNCONFIRMED_NUMBER_STRONG and settings.UNCONFIRMED_NUMBER_STRONG > 0:
        if petition.moderated or (petition.monitored and petition.monitoring.last().priority == "strong"):
            logger.debug(f"Ignoring petition {petition.id} strong monitoring due to strong number of unconfirmed signatures {unconfirmed_numb} as petition is already moderated or already has a strong monitoring priority.")
            pass
        else:
            logger.info(f"Monitoring petition {petition.id} due to strong number of unconfirmed signatures {unconfirmed_numb}.")
            petition.monitor()
            monitoring = Monitoring.objects.create(petition=petition, reason=monitoring_reason, priority="strong")
            send_mail_to_moderation_monitor(settings.MODERATION_EMAIL, petition, monitoring.reason.text, "petition", "strong") 
            
            if petition.user:
                send_monitoring_mail(petition.user.user.email, petition.user.user.username,  "petition", petition, monitoring.reason.text)
            elif petition.org:
                for member in petition.org.members.all():
                    permissions = Permission.objects.get(organization=petition.org, user=member)
                    if permissions:
                        if permissions.can_modify_permissions:
                            send_monitoring_mail(member.user.email, member.user.username, "petition", petition, monitoring.reason.text)
        return False

    # check if the number of unconfirmed signatures requires average monitoring
    elif unconfirmed_numb > settings.UNCONFIRMED_NUMBER_AVERAGE and settings.UNCONFIRMED_NUMBER_AVERAGE > 0:
        # average monitoring doesn't replace strong monitoring
        if (petition.monitored and (petition.monitoring.last().priority == "strong" or petition.monitoring.last().priority == "average")) or petition.moderated:
                logger.debug(f"Ignoring petition {petition.id} average monitoring due to strong number of unconfirmed signatures {unconfirmed_numb} as petition is already moderated or already has a average monitoring priority.")
                return False
        else:
            logger.info(f"Monitoring petition {petition.id} due to average number of unconfirmed signatures {unconfirmed_numb}.")
            petition.monitor()
            monitoring = Monitoring.objects.create(petition=petition, reason=monitoring_reason, priority="average")
            return False
    
    # check if the number of unconfirmed signatures requires low monitoring
    elif unconfirmed_numb > settings.UNCONFIRMED_NUMBER_LOW and settings.UNCONFIRMED_NUMBER_LOW > 0:
        # low monitoring doesn't replace strong or average monitoring
        if petition.monitored or petition.moderated:
                logger.debug(f"Ignoring petition {petition.id} low monitoring due to strong number of unconfirmed signatures {unconfirmed_numb} as petition is already moderated or already has a low monitoring priority.")
                return False
        else:
            logger.info(f"Monitoring petition {petition.id} due to low number of unconfirmed signatures {unconfirmed_numb}.")
            petition.monitor()
            monitoring = Monitoring.objects.create(petition=petition, reason=monitoring_reason, priority="low")
            return False

    else:
        return False

# check the number of signatures 24h after the creation of the petition. Monitor or moderate.
def check_creation_signatures(petition):
    # TODO: do we really need to run this check after the 24h have passed?
    logger.debug(f"Checking signatures created 24h after the creation of petition {petition.id}.")
    moderation_reason, _ = ModerationReason.objects.get_or_create(msg="signature_creation")
    monitoring_reason, _ = MonitoringReason.objects.get_or_create(msg="signature_creation")

    creation_signature_number = petition.get_creation_signature_number()

    # check if the number of signatures 24h after creation requires critical monitoring (=automatic moderation)
    if creation_signature_number > settings.CREATION_NUMBER_CRITICAL and settings.CREATION_NUMBER_CRITICAL > 0:
        if petition.moderated:
            logger.debug(f"Ignoring petition {petition.id} moderation due to critical number of signatures after 24h {creation_signature_number} as petition is already moderated.")
            pass
        else:
            logger.info(f"Moderating petition {petition.id} due to critical number of signatures after 24h {creation_signature_number}.")
            petition.moderate()
            petition.monitor(False)
            moderation = Moderation.objects.create(petition=petition, reason=moderation_reason)
            send_mail_to_moderation(settings.MODERATION_EMAIL, petition, moderation.reason.text, "petition") 
            
            if petition.user:
                send_moderation_mail(petition.user.user.email, petition.user.user.username, moderation.reason.text, "petition", petition)
            elif petition.org:
                for member in petition.org.members.all():
                    permissions = Permission.objects.get(organization=petition.org, user=member)
                    if permissions:
                        if permissions.can_modify_permissions:
                            send_moderation_mail(member.user.email, member.user.username, moderation.reason.text, "petition", petition)
        return True

    # check if the number of signatures 24h after creation requires strong monitoring
    elif creation_signature_number > settings.CREATION_NUMBER_STRONG and settings.CREATION_NUMBER_STRONG > 0:
        if petition.moderated or (petition.monitored and petition.monitoring.last().priority == "strong"):
            logger.debug(f"Ignoring petition {petition.id} strong monitoring due to number of signatures after 24h {creation_signature_number} as petition is already moderated or already has a strong monitoring priority.")
            pass
        else:
            logger.info(f"Monitoring petition {petition.id} due to strong number of signatures after 24h {creation_signature_number}.")
            petition.monitor()
            monitoring = Monitoring.objects.create(petition=petition, reason=monitoring_reason, priority="strong")
            send_mail_to_moderation_monitor(settings.MODERATION_EMAIL, petition, monitoring.reason.text, "petition", "strong") 
            
            if petition.user:
                send_monitoring_mail(petition.user.user.email, petition.user.user.username, "petition", petition, monitoring.reason.text)
            elif petition.org:
                for member in petition.org.members.all():
                    permissions = Permission.objects.get(organization=petition.org, user=member)
                    if permissions:
                        if permissions.can_modify_permissions:
                            send_monitoring_mail(member.user.email, member.user.username, "petition", petition, monitoring.reason.text)
        return False

    # check if the number of signatures 24h after creation requires average monitoring
    elif creation_signature_number > settings.CREATION_NUMBER_AVERAGE and settings.CREATION_NUMBER_AVERAGE > 0:
        # average monitoring doesn't replace strong monitoring
        if (petition.monitored and (petition.monitoring.last().priority == "strong" or petition.monitoring.last().priority == "average")) or petition.moderated:
                logger.debug(f"Ignoring petition {petition.id} average monitoring due to number of signatures after 24h {creation_signature_number} as petition is already moderated or already has a average monitoring priority.")
                return False
        else:
            logger.info(f"Monitoring petition {petition.id} due to average number of signatures after 24h {creation_signature_number}.")
            petition.monitor()
            monitoring = Monitoring.objects.create(petition=petition, reason=monitoring_reason, priority="average")
            return False

    # check if the number of signatures 24h after creation requires low monitoring
    elif creation_signature_number > settings.CREATION_NUMBER_LOW and settings.CREATION_NUMBER_LOW > 0:
        # low monitoring doesn't replace strong or average monitoring
        if petition.monitored or petition.moderated:
                logger.debug(f"Ignoring petition {petition.id} low monitoring due to number of signatures after 24h {creation_signature_number} as petition is already moderated or already has a low monitoring priority.")
                return False
        else:
            logger.info(f"Monitoring petition {petition.id} due to low number of signatures after 24h {creation_signature_number}.")
            petition.monitor()
            monitoring = Monitoring.objects.create(petition=petition, reason=monitoring_reason, priority="low")
            return False

    else:
        return False
