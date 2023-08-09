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
