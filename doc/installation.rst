Installation
************

Manual installation (recommended)
=================================

Install system dependencies:

On Debian derivatives
---------------------

.. code-block:: bash

  $ sudo apt update
  $ sudo apt install git virtualenv libmariadbclient-dev python3-dev build-essential mariadb-server gettext

On Centos/Fedora derivatives
----------------------------

.. code-block:: bash

  $ sudo yum install MariaDB-server galera-4 MariaDB-client MariaDB-shared MariaDB-backup MariaDB-common git python3 python3-virtualenv make gcc gettext

On Arch Linux
-------------

.. code-block:: bash

  $ sudo pacman -S mariadb mariadb-libs python make gcc gettext

Get the source, configure and initialize Pytition
-------------------------------------------------

Get the latest release git tag:

.. code-block:: bash

  $ version=$(curl -s https://api.github.com/repos/pytition/pytition/releases/latest | grep "tag_name" | cut -d : -f2,3 | tr -d \" | tr -d ,)


Create a directory to host your Pytition instance and it's static files:

.. code-block:: bash

  $ mkdir -p www/static

Create a Python3 virtualenv to install Pytitiont's dependencies:

.. code-block:: bash

  $ virtualenv -p python3 pytition_venv

Clone Pytition git repository and checkout latest release:

.. code-block:: bash

  $ cd www
  $ git clone https://github.com/pytition/pytition
  $ cd pytition
  $ git checkout $version

Enter your virtualenv and install Pytition's dependencies:

.. code-block:: bash

  $ source ../../pytition_venv/bin/activate
  (pytition_venv) $ pip3 install -r requirements.txt

Create a MySQL database and user for Pytition:

.. code-block:: bash

  $ password="ENTER_A_SECURE_PASSWORD_YOU_WILL_REMEMBER_HERE"
  $ sudo mysql -h localhost -u root -Bse "CREATE USER pytition@localhost IDENTIFIED BY '${password}'; CREATE DATABASE pytition; GRANT USAGE ON *.* TO 'pytition'@localhost IDENTIFIED BY '${password}'; GRANT ALL privileges ON pytition.* TO pytition@localhost; FLUSH PRIVILEGES;"

Write your SQL credential file in `my.cnf` outside of `www`::

  [client]
  database = pytition
  user = pytition
  password = YOUR_PASSWORD_HERE
  default-character-set = utf8

If your SQL server is MariaDB <= 10.2.1, you need to setup your SQL server to use table format compatible with larger-than-767-bytes columns. From 10.2.2 onward, row format is already DYNAMIC by default.
So, if you have an old MariaDB, add the following lines after `[server]` in `/etc/mysql/mariadb.conf.d/50-server.cnf` (This path is for Ubuntu 18.04)::

  innodb_large_prefix=true
  innodb_file_format=barracuda
  innodb_file_per_table=true
  innodb_default_row_format=DYNAMIC


Create your Pytition instance config file by copying the example one:

.. code-block:: bash

  $ cd www/pytition
  $ cp pytition/pytition/settings/config_example.py pytition/pytition/settings/config.py

Now you can edit your config file in `pytition/pytition/settings/config.py` according to :ref:`Configuration`.

.. note:: Do not forget to put a correct path to your `my.cnf` MySQL credential file in your config `DATABASES` setting.

Initialize Pytition project database. Pay attention to be in your virtualenv to enter the following commands:

.. code-block:: bash

  $ cd www/pytition/pytition
  $ export DJANGO_SETTINGS_MODULE="pytition.settings.config"
  $ python3 manage.py migrate
  $ python3 manage.py collectstatic
  $ python3 manage.py compilemessages
  $ python3 manage.py createsuperuser

.. note:: You will be asked to enter a `username`, `email` and `password` for the administrator's account.

Before trying to configure a web server you can try to see if your configuration is OK by running:

.. code-block:: bash

  $ DEBUG=1 DJANGO_SETTINGS_MODULE=pytition.settings.config python3 ./manage.py runserver

You can then point your browser to `http://yourdomain.tld:8000` and check that you can see Pytitiont's home page and log-in with your newly created admin account.

.. warning:: If you've set ``USE_MAIL_QUEUE`` to ``True`` and ``MAIL_EXTERNAL_CRON_SET`` to ``False``, running Pytition via ``manage.py runserver`` might not work well since you need to be run via `uwsgi`. Especially emails might not be sent.

.. note:: If you switch ``USE_MAIL_QUEUE`` from ``False`` to ``True`` at some point, you might have to re-run ``python3 manage.py migrate`` to create the database structures needed for the mail queues.

Configure your web server
-------------------------

Nginx + uwsgi (recommended)
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Here is an example of Nginx configuration that you can put in `/etc/nginx/sites-available/pytition`::

  server {
    server_name pytition.mydomain.tld;
    keepalive_timeout   70;

    location / {
      include         uwsgi_params;
      uwsgi_pass      unix:/var/run/uwsgi/app/pytition/socket;
    }
    location /static {
      alias /home/pytition/www/static;
    }

    listen 443 ssl; # managed by Certbot
    ssl_certificate /etc/letsencrypt/live/pytition.mydomain.tld/fullchain.pem; # managed by Certbot
    ssl_certificate_key /etc/letsencrypt/live/pytition.mydomain.tld/privkey.pem; # managed by Certbot
    include /etc/letsencrypt/options-ssl-nginx.conf; # managed by Certbot
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem; # managed by Certbot
  }

  server {
    server_name pytition.mydomain.tld;
    listen 80;
    return 301 https://pytition.mydomain.tld$request_uri;
  }

The previous example automatically redirects HTTP/80 to HTTPS/443 and uses Let's Encrypt generated certificate.

Now let's create our uwsgi configuration in `/etc/uwsgi/apps-available/pytition.init`::

  [uwsgi]
  chdir = /home/pytition/www/pytition/pytition
  module = pytition.wsgi
  home = /home/pytition/pytition_venv
  master = true
  processes = 10
  vacuum = true
  socket = /var/run/uwsgi/app/pytition/socket
  plugins = python3
  plugin = python3
