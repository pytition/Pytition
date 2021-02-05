
Advance installation on Debian
******************************

Objectif
========
Mutualiser le code de pytition pour pouvoir rendre indépendante la base de donnée 
et le répertoire mediaroot pour chaque organisation
En pratique sur un seul serveur, on aura par exemple deux organisations 
qui auront leur propre pytition: pytition.orga1.org et pytition.orga2.org 
et chaque site partagera un seul code de pytition avec des bases de données séparées et un repertoire mediaroot indépendants.
Le code étant mutualisé, il sera plus simple de mettre toutes les sites à jour avec un compte dédié pour.


Création des users et des repertoires
=====================================
.. code-block:: bash

  sudo useradd -m -s /bin/bash pytition-admin
  sudo useradd -m -s /bin/bash orga1-user
  sudo useradd -m -s /bin/bash orga2-user

pytition-admin sera l'utilisateur dédié à la maintenance du code de pytition

.. code-block:: bash
  sudo mkdir -p /etc/pytition/{orga1,orga2,admin}
  sudo touch /etc/pytition/{orga1,orga2,admin}/__init__.py
  sudo touch /etc/pytition/__init__.py

Le repertoitre /etc/pytition/ contient la configuration de la base de donnée et la configuration de pytition pour chaque site

.. code-block:: bash
  sudo mkdir -p /srv/pytition/www/mediaroot/{admin,orga1,orga2}
  sudo mkdir -p /srv/pytition/www/static


Install system dependencies:
============================

.. code-block:: bash

  $ sudo apt update
  $ sudo apt install git virtualenv python3-dev build-essential default-libmysqlclient-dev gettext libzip-dev libssl-dev apache2 uwsgi

Get the source, configure and initialize Pytition
=================================================

Get the latest release git tag:

.. code-block:: bash

  $ version=$(curl -s https://api.github.com/repos/pytition/pytition/releases/latest | grep "tag_name" | cut -d : -f2,3 | tr -d \" | tr -d ,)


Create a Python3 virtualenv to install Pytitiont's dependencies:

.. code-block:: bash

  cd /srv/pytition/
  sudo virtualenv -p python3 pytition_venv

Clone Pytition git repository and checkout latest release:

.. code-block:: bash

  cd www
  sudo git clone https://github.com/pytition/pytition
  cd pytition
  sudo git checkout $version

Attribuer les bons propriétaires et les bons droits aux dossiers:
.. code-block:: bash
  sudo chown -R pytition-admin:www-data /srv/pytition
  sudo chown orga1-user:www-data /srv/pytition/www/mediaroot/orga1
  sudo chown orga2-user:www-data /srv/pytition/www/mediaroot/orga2
  sudo chmod g+s /srv/pytition/www/static/

Enter your virtualenv and install Pytition's dependencies:

.. code-block:: bash
  sudo su pytition-admin
  source /srv/pytition/pytition_venv/bin/activate
  (pytition_venv) $ pip3 install -r /srv/pytition/www/pytition/requirements.txt

Créer les bases de données db-pytition-orga1, db-pytition-orga2, db-pytition-admin ainsi 
que les utilisateurs associés db-user-orga1, db-user-orga2 et db-user-admin sur votre serveur MariaDB

Pour chaque organisation, écrire le fichier /etc/pytition/{orga1,orga2,admin}/my.cnf
Exemple de fichier pour orga1
  [client]
  host = your-data-base-server
  database = db-pytition-orga1
  user = db-user-orga1
  password = YOUR_PASSWORD_HERE
  default-character-set = utf8

Pour l'admin, on pourra utiliser une base sqlite3 plutôt que de créer une nouvelle base sur les serveur mariaDB

Pour chaque organisation, créer le fichier /etc/pytition/{orga1,orga2,admin}/config.py en copiant par exemple le fichier 
/srv/pytition/www/pytition/config_example.py

Les fichiers my.cnf et config.py doivent avoir les bonnes permissions et droits. Par exemple pour orga1:

.. code-block:: bash
  sudo chown orga1:pytition-admin /etc/pytition/orga1/{my.cnf,config.py}
  sudo chmod u=rw,g=r,o=--- /etc/pytition/orga1/{my.cnf,config.py}

Now you can edit your config file in `pytition/pytition/settings/config.py` according to :ref:`Configuration`.

You **must** *at least* configure the settings described in the :ref:`Mandatory settings<mandatory settings>` section of the :ref:`Configuration` page.

Those are:

.. hlist::

  * SECRET_KEY
  * STATIC_URL
  * STATIC_ROOT
  * MEDIA_URL
  * MEDIA_ROOT
  * DATABASES
  * ALLOWED_HOSTS

Attention aux valeurs suivantes:
STATIC_ROOT = "/srv/pytition/www/static"
MEDIA_ROOT = "/srv/pytition/www/mediaroot/orga1 (pour le config.py de l'orga1)
la configuratio de DATABASE doit bien pointer sur /etc/pytition/orga1/my.cnf 


.. note:: Do not forget to put a correct path to the `my.cnf` MySQL credential file in your each config `DATABASES` setting.

Initialiser Pytition ainsi que les bases de données. Vous devez être dans le virtualenv pour entrer les commandes suivantes:

.. code-block:: bash
  $ export PYTHONPATH="/etc/pytition"
  $ cd /srv/pytition/www/pytition/pytition
  $ sudo -u pytition-admin -- DJANGO_SETTINGS_MODULE="admin.config" python3 manage.py migrate
  $ sudo -u pytition-admin -- DJANGO_SETTINGS_MODULE="admin.config" python3 manage.py collectstatic
  $ sudo -u pytition-admin -- DJANGO_SETTINGS_MODULE="admin.config" python3 manage.py compilemessages
  $ sudo -u pytition-admin -- DJANGO_SETTINGS_MODULE="admin.config" python3 manage.py createsuperuser
  $ sudo -u orga1-user -- DJANGO_SETTINGS_MODULE="orga1.config" python3 manage.py migrate
  $ sudo -u orga2-user -- DJANGO_SETTINGS_MODULE="orga2.config" python3 manage.py migrate

.. note:: You will be asked to enter a `username`, `email` and `password` for the administrator's

Before trying to configure a web server you can try to see if your configuration is OK by running:
Par exemple pour orga1:

.. code-block:: bash

  $ DEBUG=1 DJANGO_SETTINGS_MODULE=orga1.config python3 ./manage.py runserver

You can then point your browser to `http://yourdomain.tld:8000` and check that you can see Pytitiont's home page and log-in with your newly created admin account.

.. warning:: If you've set ``USE_MAIL_QUEUE`` to ``True`` and ``MAIL_EXTERNAL_CRON_SET`` to ``False``, running Pytition via ``manage.py runserver`` might not work well since you need to be run via `uwsgi`. Especially emails might not be sent.

.. note:: If you switch ``USE_MAIL_QUEUE`` from ``False`` to ``True`` at some point, you might have to re-run ``python3 manage.py migrate`` to create the database structures needed for the mail queues.


Apache + uwsgi + maintenance mode
=================================

Install uwsgi dependency::

  sudo apt install uwsgi uwsgi-plugin-python3 python3-uwsgidecorators

and enable proxy_uwsgi on apache:
  sudo a2enmod proxy_uwsgi

Here is an example of Apache configuration that you can put in `/etc/apache2/sites-available/orga1`::

  <VirtualHost *:80>

  ServerName pytition.orga1.org
  
  Alias /static /srv/pytition/www/static
  Proxypass /static !
  Alias /mediaroot /srv/pytition/www/mediaroot/orga1/
  Proxypass /mediaroot !
  
  ProxyPass / unix:/var/run/uwsgi/app/pytition.orga1.org/socket|uwsgi://localhost/

  <Directory /srv/pytition/www/static>
  Require all granted
  </Directory>
  
  <Directory /srv/pytition/www/mediaroot>
  Require all granted
  </Directory>
  
  CustomLog /var/log/apache2/access.log combined
  CustomLog /var/log/apache2/pytition.orga1.org.log combined
  
  </VirtualHost>

Voici un exemple de configuration pour uwsgi à mettre dans /etc/uwsgi/app-available avec un lien dans /etc/uwsgi/app-enabled

  [uwsgi]
  chdir = /srv/pytition/www/pytition/pytition
  module = pytition.wsgi
  home = /srv/pytition/pytition_venv
  master = true
  enable-threads = true
  processes = 5
  vacuum = true
  socket = /var/run/uwsgi/app/pytition.orga1.org/socket
  uid = orga1-user
  gid = www-data
  chmod-socket = 664
  pythonpath = /etc/pytition/
  plugins = python3
  env = DJANGO_SETTINGS_MODULE=orga1.config
  stats = 127.0.0.1:9191
  need-app = true
  max-requests = 5000                 
  max-worker-lifetime = 3600
  reload-on-rss = 2048
  worker-reload-mercy = 60
  harakiri = 120
  py-callos-afterfork = true
  auto-procname = true
  procname-prefix = orga1->

Start uwsgi and nginx servers:

.. code-block:: bash

  $ sudo systemctl start uwsgi
  $ sudo systemctl start apache2

Your Pytition home page should be available over there: http://pytition.orga1.org

Now it's time to :ref:`Configure<Configuration>` your Pytition instance the way you want!

Maintenance régulière (update)
==============================
Pour la mise à jour de tous les sites, voici un script (lancé par pytition-admin) qui peut être utilisé dans une tache cron:
.. code-block:: bash
  #!/bin/bash
  set -e
  DJANGO_MANAGE="/srv/pytition/www/pytition/pytition/manage.py"
  source /srv/pytition/pytition_venv/bin/activate
  export PYTHONPATH="/etc/pytition/"
  echo
  echo "###########################"
  echo "Mise à jour pytition admin"
  echo "###########################"
  echo
  DJANGO_SETTINGS_MODULE="admin.config" python3 $DJANGO_MANAGE maintenance on
  DJANGO_SETTINGS_MODULE="admin.config" python3 $DJANGO_MANAGE update
  DJANGO_SETTINGS_MODULE="admin.config" python3 $DJANGO_MANAGE maintenance off
  for site in $(ls /etc/pytition|grep -vE "^admin$|^__init__\.py$")
  do
  echo
  echo "#################################################"
  echo "Mise à jour pytition $site"
  echo "#################################################"
  echo
    DJANGO_SETTINGS_MODULE="$site.config" python3 $DJANGO_MANAGE maintenance on
    DJANGO_SETTINGS_MODULE="$site.config" python3 $DJANGO_MANAGE migrate
    DJANGO_SETTINGS_MODULE="$site.config" python3 $DJANGO_MANAGE maintenance off
  done
  deactivate




