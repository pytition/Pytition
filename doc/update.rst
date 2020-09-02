Update
******

Backup your files
=================

Backup your media files, those are the pictures uploaded by your users in the petition contents and metadata.

The files to backup are in the mediaroot directory that you configured in your settings in the `MEDIA_ROOT` variable.

.. code-block::

    $ source path/to/pytition_venv/bin/activate
    $ export DJANGO_SETTINGS_MODULE="pytition.settings.config" # path to your config
    $ backup_dir=pytition_backup_$(date +%Y%m%d_%H%M%S)
    $ mediaroot_dir=$(python3 pytition/manage.py shell -c 'from django.conf import settings; print(settings.MEDIA_ROOT)')
    $ rsync -av $mediaroot_dir $backup_dir

Backup your Database
====================

For this, I would advise to use the tools provided with your database server.

* SQLite: just copy your .db file and you're done!
* PostgreSQL: use `pg_dump` to backup and `psql` to restore
* MariaDB / MySQL: use `mysqldump` to backup and `mysql` to restore

You can also try to backup using the django tool:

.. code-block::

    $ source path/to/pytition_venv/bin/activate
    $ export DJANGO_SETTINGS_MODULE="pytition.settings.config" # path to your config
    $ # let's dump data
    $ python3 pytition/manage.py dumpdata --all --output data.json
    $ # now let's restore it
    $ python3 pytition/manage.py loaddata data.json

.. warning::

    Always *test* your backup mechanism. If not tested, you can only suppose your backups are worthless.
    You need to try to restore them on a dummy and empty instance, in order to make sure the backup is OK.
    Untested backups do not work.

Update to a newer Pytition version
==================================

You can simply run the `update` command of the `manage.py` CLI:

.. code-block::

    $ source pytition_venv/bin/activate
    $ python3 pytition/manage.py update

Or go through the following document and do it manually.

Download latest Pytition release tarball or update your git clone:

.. code-block::

    $ git stash && git pull
    $ version=$(curl -s https://api.github.com/repos/pytition/pytition/releases/latest | grep "tag_name" | cut -d : -f2,3 | tr -d \" | tr -d ,)
    $ git checkout $version

Then upgrade Pytition's dependencies:

.. code-block::

    $ source pytition_venv/bin/activate
    (pytition_venv) $ pip3 install --upgrade -r requirements.txt

Then update your database scheme, update static files, compile new translation files:

.. code-block::

    $ export DJANGO_SETTINGS_MODULE="pytition.settings.config" # path to your config
    $ python3 pytition/manage.py migrate
    $ python3 pytition/manage.py collectstatic
    $ python3 pytition/manage.py compilemessages

Then restart your web server, be it apache or nginx, and also your application server (uWSGI).
Congratulations! You should now be OK with a brand new Pytition release!