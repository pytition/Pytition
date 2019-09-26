[![Build Status](http://jenkins.sionneau.net:8080/buildStatus/icon?job=Pytition/master)](http://jenkins.sionneau.net:8080/job/Pytition/job/master/) [![Coverage status](https://img.shields.io/jenkins/coverage/cobertura/http/jenkins.sionneau.net:8080/job/Pytition/job/master.svg)](http://jenkins.sionneau.net:8080/job/Pytition/job/master/lastBuild/cobertura/)

# Pytition

## Why using Pytition?

* Because it allows you to host petitions without compromising the privacy of your signatories.
* No tracking, ever: CSS, JS and all resources are self-hosted. Pytition does not use CDN.
* Nice UI: Bootstrap 4 + JQuery 3.
* Based on solid backend technology: Django.
* Responsive UI: works well on phones/tablets/laptops/desktops.
* If you host an instance of Pytition, you can guarantee your signatories that their informations won't leak to third parties.
* It is Open Source and Free Software.

## Features

* [x] Multi-lingual UI with i18n. For now only English and French translations available but you can send a Pull Request :)
* [x] You can pre-visualize petitions before publishing them.
* [x] Easy to use: petition content is typed-in via TinyMCE editors (like WordPress).
* [x] You can setup real SMTP account for the confirmation e-mail so that it is less likely considered as SPAM.
* [x] Supports Open Graph tags to provide description and image to allow nice cards to be shown when people post the petition link on social networks.
* [x] You can propose your signatories to subscribe to a newsletter/mailinglist (via HTTP GET/POST or EMAIL methods).
* [x] You can export signatures in CSV format.
* [x] Support for several organizations on the same Pytition instance [v2.0](https://github.com/pytition/Pytition/milestone/2)
  * Fine grain per-user per-organization permissions
* [x] Email retry support through the use of a mail queue middleware
* [x] Nice (multiple) permlink support for each petition

## Future features

* [ ] Support for multi-lingual petition content: [v3.0](https://github.com/pytition/Pytition/milestone/3)
* [ ] Support for adding several petition templates: [v4.0](https://github.com/pytition/Pytition/milestone/4)
* [ ] Add optional Mastodon/Diaspora share-icons

## Install development environment

See [dev/CONTRIBUTE.md](dev/CONTRIBUTE.md)

## Installing in production

### Setup virtualenv and clone the code

```bash
$ mkdir -p www/static
$ virtualenv -p python3 pytition_venv
$ source pytition_venv/bin/activate
(pytition_venv) $ cd www
(pytition_venv) $ git clone https://github.com/pytition/pytition
(pytition_venv) $ cd pytition
(pytition_venv) $ pip3 install -r requirements.txt
```

### Configure pytition/pytition/pytition/settings.py:

In a production environment you should modify the following settings:
* SECRET_KEY => put YOUR value, it's important for security.
* DEBUG => False
* ALLOWED_HOSTS => your DNS
* DATABASES => use mysql backend instead of sqlite3
* STATIC_ROOT => /home/your_user/www/static

### Setup your customization

You can customize the TinyMCE variables:

* TINYMCE_JS_URL
* TINYMCE_DEFAULT_CONFIG

### Setup mysql credentials

```bash
~/www/pytition$ cat ~/www/my.cnf
[client]
database = DATABASENAME
user = USERNAME
password = A_PASSWORD
default-character-set = utf8
```

Then tell Django to use those credentials on settings.py:

```python
~/www/pytition$ grep -A 8 DATABASE ./pytition/pytition/settings.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '/home/YOUR_USER/www/my.cnf',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
    }
}

```

### Initialize the Django project

Beware to still be in the virtual environment, if not please re-do the ```source pytition_venv/bin/activate``` command.

```bash
(pytition_venv) $ cd www/pytition/pytition
(pytition_venv) $ python3 manage.py migrate
(pytition_venv) $ python3 manage.py collectstatic
(pytition_venv) $ python3 manage.py createsuperuser
```

### Configure Apache

```
~/www/pytition$ cat /etc/apache2/sites-enabled/petition.conf
WSGIPythonHome /home/YOUR_USER/pytition_venv
WSGIPythonPath /home/YOUR_USER/www/pytition/pytition

<VirtualHost *:80>
ServerName petition.yourdomain.tld
WSGIScriptAlias / /home/YOUR_USER/www/pytition/pytition/pytition/wsgi.py

Alias /static /home/YOUR_USER/www/static

<Directory /home/YOUR_USER/www/static>
Require all granted
</Directory>

<Directory /home/YOUR_USER/www/pytition/pytition/pytition>
<Files wsgi.py>
Require all granted
</Files>
</Directory>
</VirtualHost>
```

I won't explain how to setup HTTPS and let's encrypt TLS certificate, but you should use and force use of HTTPS for security reasons.

For more information about how to deploy a Django app, please see: https://docs.djangoproject.com/en/1.11/howto/deployment/ and https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Deployment

### Test connecting to the application

When Apache is setup and running and your database is created and populated with Django models (migrations commands) and the superuser is created, you can try accessing your petition application: http://petition.yourdomain.tld/admin

You should be able to log-in and create your first petition.

Then when the petition is created, you can access it via http://petition.yourdomain.tld/ which will always redirect to the last created petition.

If you try this URL before creating a petition you will get an error.

## Included dependencies

Those are external projects that are needed and used by Pytition, but included in Pytition source tree:

* Bootstrap 4.2.1
* JQuery 3.3.1
* Popper 1.14.6
* Open Iconic 1.1.1
* TinyMCE 4.9.2
* jQuery Smart Wizard 4

## Dependencies

* Python 3
* Django 2.2.x
* django-tinymce 2.8.0
* django-colorfield 0.1.15
* requests 2.20.x
* mysqlclient 1.3.13
* beautifulsoup4 4.6.3
* django-formtools 2.1
* bcrypt
