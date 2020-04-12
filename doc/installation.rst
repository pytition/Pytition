Installation
************

Manual installation (recommended)
=================================

Install system dependencies:

On Debian derivatives
---------------------

.. code-block:: bash

  $ sudo apt update
  $ sudo apt install git virtualenv libmariadbclient-dev python3-dev build-essential mariadb-server

On Centos/Fedora derivatives
----------------------------

.. code-block:: bash

  $ sudo yum install MariaDB-server galera-4 MariaDB-client MariaDB-shared MariaDB-backup MariaDB-common git python3 python3-virtualenv make gcc

On Arch Linux
-------------

.. code-block:: bash

  $ sudo pacman -S mariadb mariadb-libs python make gcc

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

  $ cd ../../pytition_venv
  $ source pytition_venv/bin/activate
  (pytition_venv) $ pip3 install -r requirements.txt

Create a MySQL database and user for Pytition:

.. code-block:: bash

  $ password="ENTER_A_SECURE_PASSWORD_YOU_WILL_REMEMBER_HERE"
  $ sudo mysql -h localhost -u root -Bse "CREATE USER pytition@localhost IDENTIFIED BY '${password}'; CREATE DATABASE pytition; GRANT USAGE ON *.* TO 'pytition'@localhost IDENTIFIED BY '${password}'; GRANT ALL privileges ON pytition.* TO pytition@localhost; FLUSH PRIVILEGES;"

Write your MySQL credential file in `my.cnf` outside of `www`::

  [client]
  database = pytition
  user = pytition
  password = YOUR_PASSWORD_HERE
  default-character-set = utf8

Create your Pytition instance config file by copying the example one:

.. code-block:: bash

  $ cd www/pytition
  $ cp pytition/pytition/settings/config_example.py pytition/pytition/settings/config.py

Now you can edit your config file in `pytition/pytition/settings/config.py` according to :ref:`Configuration`.

.. note:: Do not forget to put a correct path to your `my.cnf` MySQL credential file in your config `DATABASES` setting.
