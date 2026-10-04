from pytition.settings.base import *

# 1/ The following settings MUST be set

#:| Enter a **random**, **unique** and **private** secret key.
#:| Pytition won't start without it.
#:| Never share it, don't commit in git.
#:| See https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-SECRET_KEY for more details from Django documentation
#:| To generate it, you can use the following command from your virtualenv with Django installed:
#:| ``$ python3 -c "from django.core.management.utils import get_random_secret_key as g; print(g())"``
#:
#: Example::
#:
#:   SECRET_KEY = 'my secret key here'
#:
SECRET_KEY = ''

#:| Enter the file system path to the directory that will be used to serve your static files.
#:| This must be an initially empty directory.
#:| You must also configure a web server (apache, nginx or other) to serve
#:| the content of this directory according to your *STATIC_URL* setting
#:| which default is ``'/static/'`` in the example config.
#:
#: For instance you can have this kind of setting::
#:
#:   STATIC_ROOT = '/home/pytition/www/static'
#:   STATIC_URL = '/static/'
#:
#: And then in your apache config::
#:
#:   Alias /static /home/pytition/www/static
#:
#: Or in your nginx config::
#:
#:   location /static {
#:       alias /home/pytition/www/static;
#:   }
#:
#: .. seealso:: https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-STATIC_ROOT for more details from Django Documentation
#:
STATIC_ROOT = None

#:| enter the prefix that will be used for the url to refer to static files.
#:| it must end with a forward slash '/'.
#:| you must also configure a web server (apache, nginx or other) to serve
#:| the content of the directory configured as STATIC_ROOT according to this setting
#:| it defaults to ``'/static/'`` in the example config.
#:
#: for instance you can have this kind of setting::
#:
#:   STATIC_ROOT = '/home/pytition/www/static'
#:   STATIC_URL = '/static/'
#:
#: and then in your apache config::
#:
#:   alias /static /home/pytition/www/static
#:
#: or in your nginx config::
#:
#:   location /static {
#:       alias /home/pytition/www/static;
#:   }
#:
#: .. seealso:: https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-static_url for more details from django documentation
#:
STATIC_URL = '/static/'

#:| enter the prefix that will be used for the url to refer to uploaded files.
#:| it must end with a forward slash '/'.
#:| you must also configure a web server (apache, nginx or other) to serve
#:| the content of the directory configured as MEDIA_ROOT according to this setting
#:| it defaults to ``'/mediaroot/'`` in the example config.
#:
#: for instance you can have this kind of setting::
#:
#:   MEDIA_ROOT = '/home/pytition/www/mediaroot'
#:   MEDIA_URL = '/mediaroot/'
#:
#: and then in your apache config::
#:
#:   alias /mediaroot /home/pytition/www/mediaroot
#:
#: or in your nginx config::
#:
#:   location /mediaroot {
#:       alias /home/pytition/www/mediaroot;
#:   }
#:
#: .. seealso:: https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-MEDIA_URL for more details from django documentation
#:
MEDIA_URL = '/mediaroot/'

#:| Enter the file system path to the directory that will be used to serve user uploaded files.
#:| This must be an initially empty directory.
#:| You must also configure a web server (apache, nginx or other) to serve
#:| the content of this directory according to your *MEDIA_URL* setting
#:| which default is ``'/mediaroot/'`` in the example config.
#:
#: For instance you can have this kind of setting::
#:
#:   MEDIA_ROOT = '/home/pytition/www/mediaroot'
#:   MEDIA_URL = '/mediaroot/'
#:
#: And then in your apache config::
#:
#:   Alias /mediaroot /home/pytition/www/mediaroot
#:
#: Or in your nginx config::
#:
#:   location /mediaroot {
#:       alias /home/pytition/www/mediaroot;
#:   }
#:
#: .. seealso:: https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-MEDIA_ROOT for more details from Django Documentation
#:
MEDIA_ROOT = ''

#:| Enter a database setting.
#:| This will tell Django what database engine you want to use (supported ones are listed there: https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-DATABASE-ENGINE)
#:| It will also give parameters like user/password credentials, server host/port etc.
#:
#: .. seealso:: Details on how to set this up are available in Django documentation: https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-DATABASES
#:
#: In the following example, credentials are in my.cnf file::
#:
#:   DATABASES = {
#:       'default': {
#:           'ENGINE': 'django.db.backends.mysql',
#:           'OPTIONS': {
#:               'read_default_file': '/home/pytition/my.cnf',
#:               'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#:           },
#:       }
#:   }
DATABASES = {}

#:| Enter the hostname(s) (aka VirtualHost(s)) Django should accept.
#:| For instance mydomain.tld or petition.mydomain.tld
#:
#: .. seealso:: Details on how to set this up are available in Django documentation: :django:setting:`ALLOWED_HOSTS`
#:
#: Example::
#:
#:  ALLOWED_HOSTS = ['www.mysuperpetition.org', 'mysuperpetition.org']
ALLOWED_HOSTS = ['127.0.0.1', 'localhost', '[::1]']

#:| Spam detection systems to activate.
#:| Defaults are:
#:
#: * ``petition.spam_management.detectors.keywords_detector.KeywordSpamDetector``
#:    (uses a list of keywords, see `below <#pytition.settings.base.FORBIDDEN_WORDS>`__)
#: * ``petition.spam_management.detectors.akismet_detector.AkismetSpamDetector``
#:    (uses `Akismet service <https://akismet.com>`__, need configuration, see `below <#pytition.settings.base.AKISMET_KEY>`__)
#: * ``petition.spam_management.detectors.alt_profanity_check_detector.ProfanitySpamDetector``
#:    (uses `alt-profanity-check <https://pypi.org/project/alt-profanity-check/>`__)
#:
#: To deactivate a detection system, list only those you want to keep::
#:
#:    SPAM_DETECTORS = [
#:      'petition.spam_management.detectors.keywords_detector.KeywordSpamDetector',
#:    ]
#:
#SPAM_DETECTORS = [
#    'petition.spam_management.detectors.keywords_detector.KeywordSpamDetector',
#    'petition.spam_management.detectors.akismet_detector.AkismetSpamDetector',
#    'petition.spam_management.detectors.alt_profanity_check_detector.ProfanitySpamDetector',
#]

#:| Keywords that trigger monitoring.
#:| Add as many as you need.
#FORBIDDEN_WORDS = ["viagra", "casino"]

# Akismet variables
#:| Your Akismet’s API key.
#:| See https://akismet.com/support/getting-started/api-key/ to know how to get one.
#AKISMET_KEY = ""
#:| The URL of your Pytition installation.
#:| Must begin with https:// or http://
#AKISMET_URL = ""

#:| If set to True, the petitions are automatically moderated if Akismet returns 2.
#:| If set to False, the petitions will just be monitored if Akismet returns 2.
#:| We recommend to set to False if the administrator notices a lot of false positives.
#AKISMET_MODERATION_AUTO = True

#:| If set to True, send mail to petition’s owner if petition is being monitored.
#SEND_MONITORING_MAIL_TO_USER = True

#:| The email address which moderation / monitoring reports will be sent to.
#MODERATION_EMAIL = "admin@test.fr"

#:| Number of days a petition in the bin will wait before being permanently deleted.
#NUMBER_OF_DAYS_FOR_EXPIRATION = 90

### Auto moderation and monitoring settings ###
# Please note that the defaults values needs to be battle-tested
# and may not be the best values.
#
# Set variable to 0 if you want to disable a test

## Signatures variation from one day to the next
#: If there is SIGNATURE_VARIATION_CRITICAL times more signatures today
#: than a fixed period of time, we moderate the petition automatically.
#SIGNATURE_VARIATION_CRITICAL = 10000
#: If there is SIGNATURE_VARIATION_STRONG times more signatures today
#: than a fixed period of time, we monitor the petition with a strong priority.
#SIGNATURE_VARIATION_STRONG = 1000
#: If there is SIGNATURE_VARIATION_AVERAGE times more signatures today
#: than a fixed period of time, we monitor the petition with an average priority.
#SIGNATURE_VARIATION_AVERAGE = 100
#: If there is SIGNATURE_VARIATION_LOW times more signatures today
#: than a fixed period of time, we monitor the petition with a low priority.
#SIGNATURE_VARIATION_LOW = 10

## Total signature numbers according to monitoring priorities
#: If there are more than SIGNATURE_NUMBER_CRITICAL signatures in a petition,
#: we moderate it automatically.
#SIGNATURE_NUMBER_CRITICAL = 1000000
#: If there are more than SIGNATURE_NUMBER_STRONG signatures in a petition,
#: we monitor it with a strong priority.
#SIGNATURE_NUMBER_STRONG = 100000
#: If there are more than SIGNATURE_NUMBER_AVERAGE signatures in a petition,
#: we monitor it with an average priority
#SIGNATURE_NUMBER_AVERAGE = 10000
#: If there are more than SIGNATURE_NUMBER_LOW signatures in a petition,
#: we monitor it with a low priority
#SIGNATURE_NUMBER_LOW = 1000

## Number of unconfirmed signatures in the last 6h according to monitoring priorities
#: If there are more than UNCONFIRMED_NUMBER_CRITICAL unconfirmed signatures in 6h,
#: we moderate the petition automatically
#UNCONFIRMED_NUMBER_CRITICAL = 500
#: If there are more than UNCONFIRMED_NUMBER_STRONG unconfirmed signatures in 6h,
#: we monitor the petition with a strong priority
#UNCONFIRMED_NUMBER_STRONG = 300
#: If there are more than UNCONFIRMED_NUMBER_AVERAGE unconfirmed signatures in 6h,
#: we monitor the petition with an average priority
#UNCONFIRMED_NUMBER_AVERAGE = 200
#: If there are more than UNCONFIRMED_NUMBER_AVERAGE unconfirmed signatures in 6h,
#: we monitor the petition with a low priority
#UNCONFIRMED_NUMBER_LOW = 100

## Number of signatures in 24h after the creation of the petition according to monitoring priorities
#: If there are more than CREATION_NUMBER_CRITICAL signatures 24h after the creation of a petition,
#: we moderate it automatically
#CREATION_NUMBER_CRITICAL = 1000000
#: If there are more than CREATION_NUMBER_STRONG signatures 24h after the creation of a petition,
#: we monitor it with a strong priority
#CREATION_NUMBER_STRONG = 100000
#: If there are more than CREATION_NUMBER_AVERAGE signatures 24h after the creation of a petition,
#: we monitor it with an average priority
#CREATION_NUMBER_AVERAGE = 10000
#: If there are more than CREATION_NUMBER_LOW signatures 24h after the creation of a petition,
#: we monitor it with a low priority
#CREATION_NUMBER_LOW = 1000

## Maximum numbers of petitions created in one day by a user or an organization
#: More than DAY_PETITION_CRITICAL petitions from the same user or orga in one day
#: trigger automatic moderation
#DAY_PETITION_CRITICAL = 10
#: More than DAY_PETITION_STRONG petitions from the same user or orga in one day
#: trigger strong monitoring
#DAY_PETITION_STRONG = 7
#: More than DAY_PETITION_AVERAGE petitions from the same user or orga in one day
#: trigger average monitoring
#DAY_PETITION_AVERAGE = 6
#: More than DAY_PETITION_LOW petitions from the same user or orga in one day
#: trigger low monitoring
#DAY_PETITION_LOW = 5

## Maximum numbers of monitored or moderated petitions for a user or an organization.
# Checked at the creation of a petition in views.py
#: If a user or an organization has more than MONITORED_PETITIONS_CRITICAL moderated
#: or monitored petitions, it is automatically moderated.
#MONITORED_PETITIONS_CRITICAL = 10
#: If a user or an organization has more than MONITORED_PETITIONS_STRONG moderated
#: or monitored petitions, it is monitored with a strong priority.
#MONITORED_PETITIONS_STRONG = 7
#: If a user or an organization has more than MONITORED_PETITIONS_AVERAGE moderated
#: or monitored petitions, it is monitored with an average priority.
#MONITORED_PETITIONS_AVERAGE = 5
#: If a user or an organization has more than MONITORED_PETITIONS_LOW moderated
#: or monitored petitions, it is monitored with a low priority.
#MONITORED_PETITIONS_LOW = 3

## Maximum total numbers of signatures for a user's or an organization's petitions.
#: If a user or an organization has more than SIGNATURES_TOTAL_CRITICAL signatures
#: in all their petitions, they are automatically moderated.
#SIGNATURES_TOTAL_CRITICAL = 1000000
#: If a user or an organization has more than SIGNATURES_TOTAL_STRONG signatures
#: in all their petitions, they are monitored with a strong priority.
#SIGNATURES_TOTAL_STRONG = 100000
#: If a user or an organization has more than SIGNATURES_TOTAL_AVERAGE signatures
#: in all their petitions, they are monitored with an average priority.
#SIGNATURES_TOTAL_AVERAGE = 10000
#: If a user or an organization has more than SIGNATURES_TOTAL_LOW signatures
#: in all their petitions, they are monitored with a low priority.
#SIGNATURES_TOTAL_LOW = 1000

#################################
#                               #
# DO NOT EDIT AFTER THIS BANNER #
#                               #
#################################

import os

if DEFAULT_INDEX_THUMBNAIL == "":
    print("Please set a default index thumbnail or your index page will not be very beautiful")

# email backend
# Only supported configurations:
# - [default] no mailer backend, emails are sent synchronously with no retry if sending fails (USE_MAIL_QUEUE=False)
# - mailer backend used with uwsgi without cron jobs (USE_MAIL_QUEUE=True)
# - mailer backend used without uwsgi with cron jobs (USE_MAIL_QUEUE=True, MAIL_EXTERNAL_CRON_SET=True)
# Note: if MAIL_EXTERNAL_CRON_SET is set, the responsability to setup external cron job to send mail is up to the administrator.
# If none are set, the emails will never be send!
if USE_MAIL_QUEUE:
    INSTALLED_APPS += ('mailer',)
    # this enable mailer by default in django.send_email
    EMAIL_BACKEND = "mailer.backend.DbBackend"

if os.environ.get('DEBUG'):
    DEBUG = True
