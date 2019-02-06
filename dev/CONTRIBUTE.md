# Contribute to Pytition

## Translations

You can help with translations.
Contact me by opening an issue or by sending a private e-mail if you want to contribute by translating the project
in a language you know. I can explain how to do it.

## Open a Pull Request

Please don't hesitate to open a Pull Request if you have a fix for one of the [issues](https://github.com/fallen/pytition/issues).

## Report bugs or give new enhancements/feature ideas

Don't hesitate to open new [issues](https://github.com/fallen/pytition/issues) with your reports or remarks.

## Install a development environment

### With a script

You can use [this script](https://github.com/fallen/Pytition/blob/master/dev/dev_setup.sh) to:

* Install all system requirements
* clone the git repo
* create a virtual environment with all runtime dependencies
* Install MariaDB and create user/database and generate the credential config file for you
* Run database migration
* Create superuser account
* Insert data into the development database
  * Create dummy Organizations, Users and Petitions.

This script is only proven to work on a fresh Ubuntu 18.04 install.
You can use VirtualBox, Docker, qemu or whatever virtualisation/containerization technology you prefer.

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
