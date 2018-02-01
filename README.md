# Pytition

## Installing

### Setup virtualenv and clone the code

```bash
$ mkdir -p www/static
$ virtualenv -p python3 pytition_venv
$ source pytition_venv/bin/activate
(pytition_venv) $ pip3 install django==1.11.9 pillow django-tinymce django-colorfield requests
(pytition_venv) $ cd www
(pytition_venv) $ git clone https://github.com/fallen/pytition
(pytition_venv) $ cd pytition
```

### Configure pytition/pytition/pytition/settings.py:

In a production environment you should modify the following settings:
* SECRET_KEY => put YOUR value, it's important for security.
* DEBUG => False
* ALLOWED_HOSTS => your DNS
* DATABASES => use mysql backend instead of sqlite3
* STATIC_ROOT => /home/your_user/www/static

### Setup your customization
For your own usage of Pytition you should customize the following variables in settings.py:

* ORG_NAME => your organization name
* ORG_TWITTER_HANDLE => your organization's twitter handle

You can also customize the TinyMCE variables:

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
(pytition_venv) $ python3 manage.py makemigrations
(pytition_venv) $ python3 manage.py migrate
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


## Dependencies

* Python 3
* Django
* Pillow
* django-tinymce
* django-colorfield
* requests
