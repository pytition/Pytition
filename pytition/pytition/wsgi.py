"""
WSGI config for pytition project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pytition.settings")

application = get_wsgi_application()

if os.environ.get('EMAIL_BACKEND') == 'mailer':
    try:
        import uwsgidecorators
        from django.core.management import call_command

        @uwsgidecorators.timer(10)
        def send_queued_mail(num):
            """Send queued mail every 10 seconds"""
            call_command('send_mail')

        @uwsgidecorators.timer(1 * 60)
        def retry_deferred(num):
            """Retry deferred emails"""
            call_command('retry_deferred')

        @uwsgidecorators.timer(1 * 24 * 60 * 60)
        def purge_mail_log(num):
            """purge 2 days old mails"""
            call_command('purge_mail_log', '2')

    except ImportError:
        print("""uwsgidecorators not found. Cron are disabled,
If you want some mails, you should setup the cron yourself with something like:
*       * * * * (/path/to/your/python /path/to/your/manage.py send_mail)
0,20,40 * * * * (/path/to/your/python /path/to/your/manage.py retry_deferred)
0       0 * * * (/path/to/your/python /path/to/your/manage.py purge_mail_log 2)

""")
