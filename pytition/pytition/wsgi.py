"""
WSGI config for pytition project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pytition.settings")
from django.conf import settings

if settings.USE_MAIL_QUEUE:
    try:
        import uwsgidecorators
        from django.core.management import call_command

        @uwsgidecorators.timer(settings.UWSGI_WAIT_FOR_MAIL_SEND_IN_S)
        def send_queued_mail(num):
            """Send queued mail every 10 seconds"""
            call_command('send_mail')

        @uwsgidecorators.timer(settings.UWSGI_WAIT_FOR_RETRY_IN_S)
        def retry_deferred(num):
            """Retry deferred emails"""
            call_command('retry_deferred')

        @uwsgidecorators.timer(settings.UWSGI_WAIT_FOR_PURGE_IN_S)
        def purge_mail(num):
            """purge 2 days old mails"""
            call_command('purge_mail_log', settings.UWSGI_NB_DAYS_TO_KEEP)

    except ImportError:
        if settings.MAIL_EXTERNAL_CRON_SET:
            print("info: uwsgi not found, the external cron job will be in charge of sending emails")
        else:
            print("""Error: uwsgi not found and no external cron job have been set.
With this setup, no email will be ever sent.
If you want some mails, you should set MAIL_EXTERNAL_CRON_SET=True and setup the cron yourself with something like:
*       * * * * (/path/to/your/python /path/to/your/manage.py send_mail)
0,20,40 * * * * (/path/to/your/python /path/to/your/manage.py retry_deferred)
0       0 * * * (/path/to/your/python /path/to/your/manage.py purge_mail_log 2)

""")
            sys.exit(1)

application = get_wsgi_application()