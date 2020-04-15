from .base import *

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
#:| which be default is ``'/static/'``.
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
STATIC_URL = '/static/'

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
# - [default] no mailer backend, emails are sent synchronously with no retry if sending fails
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
