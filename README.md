[![Build Status](http://jenkins.sionneau.net:8080/buildStatus/icon?job=Pytition/master)](http://jenkins.sionneau.net:8080/job/Pytition/job/master/) [![Coverage status](https://img.shields.io/jenkins/coverage/cobertura/http/jenkins.sionneau.net:8080/job/Pytition/job/master.svg)](http://jenkins.sionneau.net:8080/job/Pytition/job/master/lastBuild/cobertura/) [![Documentation Status](https://readthedocs.org/projects/pytition/badge/?version=latest)](https://pytition.readthedocs.io/en/latest/?badge=latest)

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

See https://pytition.readthedocs.io/en/latest/installation.html#manual-installation-recommended-for-production

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
