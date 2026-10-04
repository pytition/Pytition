from petition.models import PytitionUser, Organization, Petition, Moderation, ModerationReason, Monitoring, MonitoringReason, Signature
from petition.helpers import send_mail_to_moderation, send_mail_to_moderation_monitor, send_monitoring_mail, send_moderation_mail
from django.conf import settings
from django.db.models import Q
from django.contrib import messages
from django.utils.translation import gettext as _

"""
Anti bot tests for users and organizations: check the number of petitions in a day, the number of monitored or moderated petitions and the total niuùber of signatures.
Four types of monitoring are defined:
    - critical: the user or orga is moderated, emails are sent to admin and user
    - strong: the user or orga is monitored with a strong priority, emails are sent to admin and user, display in admin and dashboard
    - average: the user or orga is monitored with an average priority, display in admin and dashboard
    - low: the user or orga is monitored with a low priority, display in admin
"""


# Check number of petitions in 24h
def check_petition_number_day(user, orga, request):
    moderation_reason, _ = ModerationReason.objects.get_or_create(msg="owner_petition_number")
    monitoring_reason, _ = MonitoringReason.objects.get_or_create(msg="owner_petition_number")

    # if tests are done on a user
    if orga == None:
        day_petition_number = user.get_day_petition_number()
        
        # Automatic moderation
        if day_petition_number >= settings.DAY_PETITION_CRITICAL and settings.DAY_PETITION_CRITICAL > 0:
            if not(user.moderated):
                user.moderate()
                user.monitor(False)
                    
                mod_petitions = Petition.objects.filter(user = user)
                for petition in mod_petitions:
                    if not(petition.moderated):
                        petition.moderate()
                        petition.monitor(False)

                        # We create a Moderation object associated to each petition of the user
                        moderation = Moderation.objects.create(petition=petition, reason=moderation_reason)
                   

                # We create a Moderation object associated to the user
                moderation = Moderation.objects.create(user=user, reason=moderation_reason)

                # We send moderation emails and an error message
                owner_type = "user"
                User = user.user
                send_moderation_mail(User.email, User.username, moderation.reason.text, "user", user)
                send_mail_to_moderation(settings.MODERATION_EMAIL, User.username, moderation.reason.text, owner_type)
                messages.error(request, _("Too many petitions were created in one day"))

        # strong monitoring
        elif day_petition_number >= settings.DAY_PETITION_STRONG and settings.DAY_PETITION_STRONG > 0:
            if user.moderated or (user.monitored and user.monitoring.last().priority == "strong"):
                pass
            else:
                user.monitor()
                monitoring = Monitoring.objects.create(user=user, reason=monitoring_reason, priority="strong")
                send_mail_to_moderation_monitor(settings.MODERATION_EMAIL, user, monitoring.reason.text, "user", "strong") 
                send_monitoring_mail(user.user.email, user.user.username, "user", user, monitoring.reason.text)

        # average monitoring
        elif day_petition_number >= settings.DAY_PETITION_AVERAGE and settings.DAY_PETITION_AVERAGE > 0:
            if (user.monitored and (user.monitoring.last().priority == "strong" or user.monitoring.last().priority == "average")) or user.moderated:
                pass
            else:
                user.monitor()
                monitoring = Monitoring.objects.create(user=user, reason=monitoring_reason, priority="average")

        # low monitoring
        elif day_petition_number >= settings.DAY_PETITION_LOW and settings.DAY_PETITION_LOW > 0:
            if user.monitored or user.moderated:
                pass
            else:
                user.monitor()
                monitoring = Monitoring.objects.create(user=user, reason=monitoring_reason, priority="low")
    
    # if tests are done on an organization
    else:
        day_petition_number = orga.get_day_petition_number_org()
        # automatic moderation
        if day_petition_number >= settings.DAY_PETITION_CRITICAL and settings.DAY_PETITION_CRITICAL > 0:
            if not(orga.moderated):
                orga.moderate()
                orga.monitor(False)
                User = user.user
                    
                mod_petitions = Petition.objects.filter(org = orga)
                for petition in mod_petitions:
                    if not(petition.moderated):
                        petition.moderate()
                        petition.monitor(False)

                        # We create a Moderation object associated to each petition of the organization
                        moderation = Moderation.objects.create(petition=petition, reason=moderation_reason)
                    
                # We create a Moderation object associated to the user
                moderation = Moderation.objects.create(org=orga, reason=moderation_reason)
                
                # We send moderation emails and an error message
                send_moderation_mail(User.email, User.username, moderation.reason.text, "organization", orga)
                send_mail_to_moderation(settings.MODERATION_EMAIL, User.username, moderation.reason.text, "organization")
                messages.error(request, _("Too many petitions were created in one day"))

        # strong monitoring
        elif day_petition_number >= settings.DAY_PETITION_STRONG and settings.DAY_PETITION_STRONG > 0:
            if orga.moderated or (orga.monitored and orga.monitoring.last().priority == "strong"):
                pass
            else:
                orga.monitor()
                monitoring = Monitoring.objects.create(org=orga, reason=monitoring_reason, priority="strong")
                send_mail_to_moderation_monitor(settings.MODERATION_EMAIL, user, monitoring.reason.text, "organization", "strong") 
                send_monitoring_mail(user.user.email, user.user.username, "organization", orga, monitoring.reason.text)

        # average monitoring
        elif day_petition_number >= settings.DAY_PETITION_AVERAGE and settings.DAY_PETITION_AVERAGE > 0:
            if (orga.monitored and (orga.monitoring.last().priority == "strong" or orga.monitoring.last().priority == "average")) or orga.moderated:
                pass
            else:
                user.monitor()
                monitoring = Monitoring.objects.create(org=orga, reason=monitoring_reason, priority="average")

        # low monitoring
        elif day_petition_number >= settings.DAY_PETITION_LOW and settings.DAY_PETITION_LOW > 0:
            if orga.monitored or orga.moderated:
                pass
            else:
                orga.monitor()
                monitoring = Monitoring.objects.create(org=orga, reason=monitoring_reason, priority="low")
            
# check number of monitored or moderated petitions
def check_mon_petition_number(user, orga, request):
    moderation_reason, created = ModerationReason.objects.get_or_create(msg="owner_monpetition_number")
    monitoring_reason, created = MonitoringReason.objects.get_or_create(msg="owner_monpetition_number")

    # if tests are done on a user
    if orga == None:
        petitions = user.petition_set.all()
        petitions = petitions.filter(Q(moderated=True) | Q(monitored=True))
        nb_monitored_petitions = petitions.count()
        
        # automatic moderation
        if nb_monitored_petitions >= settings.MONITORED_PETITIONS_CRITICAL and settings.MONITORED_PETITIONS_CRITICAL > 0:
            if not(user.moderated):
                user.moderate()
                user.monitor(False)

                mod_petitions = Petition.objects.filter(user = user)
                for petition in mod_petitions:
                    if not(petition.moderated):
                        petition.moderate()
                        petition.monitor(False)

                        # We create a Moderation object associated to each petition of the user
                        moderation = Moderation.objects.create(petition=petition, reason=moderation_reason)

                moderation = Moderation.objects.create(user=user, reason=moderation_reason)
                send_mail_to_moderation(settings.MODERATION_EMAIL, user, moderation.reason.text, "user") 
                send_moderation_mail(user.user.email, user.user.username, moderation.reason.text, "user", user)
                messages.error(request, _("You have too many moderated or monitored petitions."))
        
        # strong monitoring
        elif nb_monitored_petitions >= settings.MONITORED_PETITIONS_STRONG and settings.MONITORED_PETITIONS_STRONG > 0:
            if user.moderated or (user.monitored and user.monitoring.last().priority == "strong"):
                pass
            else:
                user.monitor()
                monitoring = Monitoring.objects.create(user=user, reason=monitoring_reason, priority="strong")
                send_mail_to_moderation_monitor(settings.MODERATION_EMAIL, user, monitoring.reason.text, "user", "strong") 
                send_monitoring_mail(user.user.email, user.user.username, "user", user, monitoring.reason.text)

        # average monitoring
        elif nb_monitored_petitions >= settings.MONITORED_PETITIONS_AVERAGE and settings.MONITORED_PETITIONS_AVERAGE > 0:
            if (user.monitored and (user.monitoring.last().priority == "strong" or user.monitoring.last().priority == "average")) or user.moderated:
                pass
            else:
                user.monitor()
                monitoring = Monitoring.objects.create(user=user, reason=monitoring_reason, priority="average")

        # low monitoring
        elif nb_monitored_petitions >= settings.MONITORED_PETITIONS_LOW and settings.MONITORED_PETITIONS_LOW > 0:
            if user.monitored or user.moderated:
                pass
            else:
                user.monitor()
                monitoring = Monitoring.objects.create(user=user, reason=monitoring_reason, priority="low")

    # if tests are done on an orga
    else:
        petitions = orga.petition_set.all()
        petitions = petitions.filter(Q(moderated=True) | Q(monitored=True))
        nb_monitored_petitions = petitions.count()

        # automatic moderation
        if nb_monitored_petitions > settings.MONITORED_PETITIONS_CRITICAL and settings.MONITORED_PETITIONS_CRITICAL > 0:
            if not(orga.moderated):
                orga.moderate()
                orga.monitor(False)

                mod_petitions = Petition.objects.filter(org = orga)
                for petition in mod_petitions:
                    if not(petition.moderated):
                        petition.moderate()
                        petition.monitor(False)

                        # We create a Moderation object associated to each petition of the organization
                        moderation = Moderation.objects.create(petition=petition, reason=moderation_reason)
                    
                moderation = Moderation.objects.create(org=orga, reason=moderation_reason)
                send_mail_to_moderation(settings.MODERATION_EMAIL, orga, moderation.reason.text, "organization") 
                send_moderation_mail(user.user.email, user.user.username, moderation.reason.text,  "organization", orga)
                messages.error(request, _("This organization has too many moderated or monitored petitions."))
        
        # strong monitoring
        elif nb_monitored_petitions > settings.MONITORED_PETITIONS_STRONG and settings.MONITORED_PETITIONS_STRONG > 0:
            if orga.moderated or (orga.monitored and orga.monitoring.last().priority == "strong"):
                pass
            else:
                orga.monitor()
                monitoring = Monitoring.objects.create(org=orga, reason=monitoring_reason, priority="strong")
                send_mail_to_moderation_monitor(settings.MODERATION_EMAIL, orga, monitoring.reason.text, "organization", "strong")
                send_monitoring_mail(user.user.email, user.user.username, "organization", orga, monitoring.reason.text)

        # average monitoring
        elif nb_monitored_petitions > settings.MONITORED_PETITIONS_AVERAGE and settings.MONITORED_PETITIONS_AVERAGE > 0:
            if (orga.monitored and (orga.monitoring.last().priority == "strong" or orga.monitoring.last().priority == "average")) or orga.moderated:
                pass
            else:
                orga.monitor()
                monitoring = Monitoring.objects.create(org=orga, reason=monitoring_reason, priority="average")

        # low monitoring
        elif nb_monitored_petitions > settings.MONITORED_PETITIONS_LOW and settings.MONITORED_PETITIONS_LOW > 0:
            if orga.monitored or orga.moderated:
                pass
            else:
                orga.monitor()
                monitoring = Monitoring.objects.create(org=orga, reason=monitoring_reason, priority="low")

# check the total signature number for a user or an organization
def check_user_signature_number(user, orga, request):
    moderation_reason, created = ModerationReason.objects.get_or_create(msg="owner_signature_number")
    monitoring_reason, created = MonitoringReason.objects.get_or_create(msg="owner_signature_number")

    # if tests are done on a user
    if orga == None:
        nb_signatures = user.get_total_signature_number()

        # automatic moderation
        if nb_signatures > settings.SIGNATURES_TOTAL_CRITICAL and settings.SIGNATURES_TOTAL_CRITICAL > 0:
            if not(user.moderated):
                user.moderate()
                user.monitor(False)

                mod_petitions = Petition.objects.filter(user = user)
                for petition in mod_petitions:
                    if not(petition.moderated):
                        petition.moderate()
                        petition.monitor(False)

                        # We create a Moderation object associated to each petition of the user
                        moderation = Moderation.objects.create(petition=petition, reason=moderation_reason)

                moderation = Moderation.objects.create(user=user, reason=moderation_reason)
                send_mail_to_moderation(settings.MODERATION_EMAIL, user, moderation.reason.text, "user") 
                send_moderation_mail(user.user.email, user.user.username, moderation.reason.text, "user", user)
                messages.error(request, _("You have too many signatures in your petitions."))

        # strong monitoring
        elif nb_signatures > settings.SIGNATURES_TOTAL_STRONG and settings.SIGNATURES_TOTAL_STRONG > 0:
            if user.moderated or (user.monitored and user.monitoring.last().priority == "strong"):
                pass
            else:
                user.monitor()
                monitoring = Monitoring.objects.create(user=user, reason=monitoring_reason, priority="strong")
                send_mail_to_moderation_monitor(settings.MODERATION_EMAIL, user, monitoring.reason.text, "user", "strong")
                send_monitoring_mail(user.user.email, user.user.username, "user", user, monitoring.reason.text)

        # average monitoring
        elif nb_signatures > settings.SIGNATURES_TOTAL_AVERAGE and settings.SIGNATURES_TOTAL_AVERAGE > 0:
            if (user.monitored and (user.monitoring.last().priority == "strong" or user.monitoring.last().priority == "average")) or user.moderated:
                pass
            else:
                user.monitor()
                monitoring = Monitoring.objects.create(user=user, reason=monitoring_reason, priority="average")

        # low monitoring
        elif nb_signatures > settings.SIGNATURES_TOTAL_LOW and settings.SIGNATURES_TOTAL_LOW > 0:
            if user.monitored or user.moderated:
                pass
            else:
                user.monitor()
                monitoring = Monitoring.objects.create(user=user, reason=monitoring_reason, priority="low")

    # if tests are done on an organization
    else:
        nb_signatures = orga.get_total_signature_number()

        # automatic moderation
        if nb_signatures > settings.SIGNATURES_TOTAL_CRITICAL and settings.SIGNATURES_TOTAL_CRITICAL > 0:
            if not(orga.moderated):
                orga.moderate()
                orga.monitor(False)

                mod_petitions = Petition.objects.filter(org = orga)
                for petition in mod_petitions:
                    if not(petition.moderated):
                        petition.moderate()
                        petition.monitor(False)

                        # We create a Moderation object associated each petition of the organization
                        moderation = Moderation.objects.create(petition=petition, reason=moderation_reason)

                moderation = Moderation.objects.create(org=orga, reason=moderation_reason)
                send_mail_to_moderation(settings.MODERATION_EMAIL, orga, moderation.reason.text, "organization") 
                send_moderation_mail(user.user.email, user.user.username, moderation.reason.text, "organization", orga)
                messages.error(request, _("This organization has too many signatures in its petitions."))

        # strong monitoring
        elif nb_signatures > settings.SIGNATURES_TOTAL_STRONG and settings.SIGNATURES_TOTAL_STRONG > 0:
            if orga.moderated or (orga.monitored and orga.monitoring.last().priority == "strong"):
                pass
            else:
                orga.monitor()
                monitoring = Monitoring.objects.create(org=orga, reason=monitoring_reason, priority="strong")
                send_mail_to_moderation_monitor(settings.MODERATION_EMAIL, orga, monitoring.reason.text, "organization", "strong")
                send_monitoring_mail(user.user.email, user.user.username, "organization", orga, monitoring.reason.text)

        # average monitoring
        elif nb_signatures > settings.SIGNATURES_TOTAL_AVERAGE and settings.SIGNATURES_TOTAL_AVERAGE > 0:
            if (orga.monitored and (orga.monitoring.last().priority == "strong" or orga.monitoring.last().priority == "average")) or orga.moderated:
                pass
            else:
                orga.monitor()
                monitoring = Monitoring.objects.create(org=orga, reason=monitoring_reason, priority="average")

        # low monitoring
        elif nb_signatures > settings.SIGNATURES_TOTAL_LOW and settings.SIGNATURES_TOTAL_LOW > 0:
            if orga.monitored or orga.moderated:
                pass
            else:
                orga.monitor()
                monitoring = Monitoring.objects.create(org=orga, reason=monitoring_reason, priority="low")

