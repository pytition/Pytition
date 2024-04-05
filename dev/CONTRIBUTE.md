# Contribute to Pytition

## Translations

You can help with translations.
The best way to do so is via our weblate hosted by Framasoft: https://weblate.framasoft.org/projects/pytition/pytitions/
Contact me by opening an issue or by sending a private e-mail if you want to contribute by translating the project
in a language you know and have any issue with weblate (for instance your language is not available). I can help.

## Open a Pull Request

Please don't hesitate to open a Pull Request if you have a fix for one of the [issues](https://github.com/pytition/pytition/issues).

## Report bugs or give new enhancements/feature ideas

Don't hesitate to open new [issues](https://github.com/pytition/pytition/issues) with your reports or remarks.

## Install a development environment

### Manual install (recommended for production)

See https://pytition.readthedocs.io/en/latest/installation.html#manual-installation-recommended-for-production

### With docker-compose

See https://pytition.readthedocs.io/en/latest/installation.html#installation-via-docker-recommended-for-development

### With a script (not recommended)

You can use [this script](https://github.com/pytition/Pytition/blob/master/dev/dev_setup.sh) to setup a development environment.
If you trust it, run, in the directory where you want to clone the project:

```bash
curl -sSL "https://raw.githubusercontent.com/pytition/Pytition/master/dev/dev_setup.sh" | sh
```

This script is only proven to work on a fresh Ubuntu 18.04 install.
You can use VirtualBox, Docker, qemu or whatever virtualisation/containerization technology you prefer.


## Run tests

It uses coverage to evaluate tests coverage.
```
pdm run coverage run pytition/manage.py test petition
pdm run coverage report -m
```
Add `docker-compose exec web` before each command to use it with docker.
