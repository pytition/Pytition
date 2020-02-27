"""
Django settings for pytition project.

Generated by 'django-admin startproject' using Django 1.11.5.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os
import django.conf.locale
from django.contrib.messages import constants as messages
from django.urls import reverse_lazy
from django.conf import global_settings
from django.utils.translation import gettext_lazy

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'lbkzn($sn*oi!azcw022%=o+av8+iqjl&^q3gy)$j&r68qh^-4'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['0.0.0.0', '127.0.0.1', 'localhost', '[::1]']


# Application definition

INSTALLED_APPS = [
    'tinymce',
    'colorfield',
    'petition.apps.PetitionConfig',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'widget_tweaks',
    'formtools',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
    'django.contrib.auth.hashers.Argon2PasswordHasher',
]

ROOT_URLCONF = 'pytition.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'petition.helpers.footer_content_processor',
                'petition.helpers.settings_context_processor',
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',

            ],
        },
    },
]

WSGI_APPLICATION = 'pytition.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '/home/petition/www/my.cnf',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

if os.environ.get('USE_POSTGRESQL'):
    from .pgsql import DATABASES

# Set USE_MAIL_QUEUE to True if you want email sending to retry upon failure
# email transmition naturally have retries *if the first SMTP server accepts it*
# If your smtp server refuses to handle the email (anti-flood throttle?) then it
# is up to you to retry, and this is what the mail queue does for you.
# This is especially needed if you don't own the first-hop SMTP server
# and cannot configure it to always accept your emails regardless of the sending
# frequency.
USE_MAIL_QUEUE = False

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

# set it to True if you use the 'mailer' backend, and a external Crontab has been set
MAIL_EXTERNAL_CRON_SET = False

# number of seconds to wait before sending emails. This will be usefull only if USE_MAIL_QUEUE=True and uwsgi is used
UWSGI_WAIT_FOR_MAIL_SEND_IN_S=10
# number of seconds to wait before retrying emails. This will be usefull only if USE_MAIL_QUEUE=True and uwsgi is used
UWSGI_WAIT_FOR_RETRY_IN_S=1 * 60
# number of seconds to wait before purging emails. This will be usefull only if USE_MAIL_QUEUE=True and uwsgi is used
UWSGI_WAIT_FOR_PURGE_IN_S=1 * 24 * 60 * 60
UWSGI_NB_DAYS_TO_KEEP=3

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Europe/Paris'

USE_I18N = True

USE_L10N = True

USE_TZ = True
X_FRAME_OPTIONS = "SAMEORIGIN"
LOCALE_PATHS = (os.path.join(BASE_DIR, "locale"), )

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.environ.get('STATIC_ROOT')
LOGIN_URL = '/petition/login/'

TINYMCE_JS_URL = '/static/vendor/tinymce/js/tinymce/tinymce.min.js'
TINYMCE_DEFAULT_CONFIG = {
    'plugins': 'print preview fullpage searchreplace autolink directionality visualblocks visualchars fullscreen image link media template codesample table charmap hr pagebreak nonbreaking anchor toc insertdatetime advlist lists textcolor wordcount imagetools contextmenu colorpicker textpattern help',
    'theme': "modern",
    'cleanup_on_startup': True,
    'custom_undo_redo_levels': 10,
    'toolbar1': 'formatselect | bold italic strikethrough forecolor backcolor | link | alignleft aligncenter alignright alignjustify  | numlist bullist outdent indent  | removeformat | fontselect | fontsizeselect',
    'insert_toolbar': 'forecolor backcolor',
    'fontsize_formats': '8pt 10pt 12pt 14pt 18pt 24pt 36pt',
    'entity_encoding': 'raw',
    'relative_urls' : False,
    'convert_urls': True,
    'setup': """function(ed) {
       ed.on('change', function(e) {
            set_mce_changed(ed);
       });}""",
}
TINYMCE_INCLUDE_JQUERY = True

SITE_NAME = "Pytition"
ALLOW_REGISTER = True
LOGIN_REDIRECT_URL = reverse_lazy("user_dashboard")
DEFAULT_INDEX_THUMBNAIL = "/img/petition_icon.svg"

# Leave it set to None for no footer
# This should contain the relative path to your footer template
# That would be the location for any "legal mention" / "GDPR" / "TOS" link.
#FOOTER_TEMPLATE = 'layouts/footer.html.example'
FOOTER_TEMPLATE = None

#INDEX_PAGE_ORGA = "RAP"
#INDEX_PAGE_USER = "admin"
INDEX_PAGE = "HOME"
#INDEX_PAGE = "ALL_PETITIONS"
#INDEX_PAGE = "ORGA_PROFILE"
#INDEX_PAGE = "USER_PROFILE"
#INDEX_PAGE = "LOGIN_REGISTER"

# Anti bot feature
SIGNATURE_THROTTLE = 5 # 5 signatures from same IP allowed
SIGNATURE_THROTTLE_TIMING = 60*60*24 # in a 1 day time frame

LANGUAGES = [
    ('en', gettext_lazy('English')),
    ('es', gettext_lazy('Spanish')),
    ('fr', gettext_lazy('French')),
    ('oc', gettext_lazy('Occitan')),
]

EXTRA_LANG_INFO = {
    'oc': {
        'code': 'oc',
        'name': 'Occitan',
    },
}
LANG_INFO = dict(django.conf.locale.LANG_INFO, **EXTRA_LANG_INFO)
django.conf.locale.LANG_INFO = LANG_INFO

MEDIA_ROOT = os.path.join(BASE_DIR, "mediaroot")
MEDIA_URL = "/mediaroot/"

if DEFAULT_INDEX_THUMBNAIL == "":
    print("Please set a default index thumbnail or your index page will not be very beautiful")
