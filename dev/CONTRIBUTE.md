# Contribute to Pytition

## Translations

You can help with translations.
Contact me by opening an issue or by sending a private e-mail if you want to contribute by translating the project
in a language you know. I can explain how to do it.

## Open a Pull Request

Please don't hesitate to open a Pull Request if you have a fix for one of the [issues](https://github.com/pytition/pytition/issues).
## Report bugs or give new enhancements/feature ideas
Don't hesitate to open new [issues](https://github.com/pytition/pytition/issues) with your reports or remarks.

## Install a development environment

### With a script

You can use [this script](https://github.com/pytition/Pytition/blob/master/dev/dev_setup.sh) to setup a development environment.
If you trust it, run, in the directory where you want to clone the project:

```bash
curl -sSL "https://raw.githubusercontent.com/pytition/Pytition/master/dev/dev_setup.sh" | sh
```

This script is only proven to work on a fresh Ubuntu 18.04 install.
You can use VirtualBox, Docker, qemu or whatever virtualisation/containerization technology you prefer.

### Manual

If you don't trust the above script, and don't want to use Docker, you can install Pytition manually.
We will use MariaDB as a backend. If you prefer PostgreSQL or SQlite, try with the automatic script or with Docker.

First, you'll need to clone the repository:
```bash
git clone git@github.com:pytition/Pytition.git
# or, if you prefer HTTPS
git clone https://github.com/pytition/Pytition.git
```
Then you will need native dependencies:
```bash
# On Debian and derivatives
sudo apt update
sudo apt install git virtualenv libmariadbclient-dev python3-dev build-essential mariadb-server
# If you use Yum/DNF
sudo yum install MariaDB-server galera-4 MariaDB-client MariaDB-shared MariaDB-backup MariaDB-common git python3 python3-virtualenv make gcc
# On Arch
sudo pacman -S mariadb mariadb-libs python make gcc
```
Move in the freshly cloned directory with `cd Pytition`, and create a VirtualEnv.
It will isolate your Python setup for Pytition from the rest of your system, avoiding packages conflicts for other projects.
```
virtualenv -p python3 venv
# You can enter in the virtualenv with:
source venv/bin/activate
```
You will need to run this last command every time you start working on Pytition.
You can now install Python packages:
```
pip3 install -r requirements_dev.txt
```
Init the database with:
```bash
password="ENTER_A_SECURE_PASSWORD_YOU_WILL_REMEMBER_HERE"
sudo mysql -h localhost -u root -Bse "CREATE USER pytition@localhost IDENTIFIED BY '${password}'; CREATE DATABASE pytition; GRANT USAGE ON *.* TO 'pytition'@localhost IDENTIFIED BY '${password}'; GRANT ALL privileges ON pytition.* TO pytition@localhost; FLUSH PRIVILEGES;"
```
Then write the following in a new file called `my.cnf`:
```
[client]
database = pytition
user = pytition
password = YOUR_PASSWORD_HERE
default-character-set = utf8
```
Tell Pytition where to find this file with:
```bash
sed -i -e "s@/home/petition/www/@$PWD/@" pytition/pytition/settings/base.py
```
Then run migrations (scripts to initialize the database):
```bash
cd pytition && python3 ./manage.py migrate && cd -
```
You can create an administrator account, and populate the database with fake data:
```bash
cd pytition && python3 ./manage.py createsuperuser && cd -
./dev/prepropulate.sh
```
And… you are done! You can start the server with:
```bash
python3 ./pytition/manage.py runserver
```
You can access it at [http://localhost:8080](http://localhost:8080)!
### With docker-compose
This creates two containers, one for the database using postgresql, another for the django project.
```
docker-compose up --build
docker-compose exec web ./dev/initialize.sh
```
This script will
* Run database migration
* Create superuser account
* Insert data into the development database
## Run tests
It uses coverage to evaluate tests coverage.
```
coverage run pytition/manage.py test petition
coverage report -m
```
Add `docker-compose exec web` before each command to use it with docker.
