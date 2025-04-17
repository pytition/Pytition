[![Documentation Status](https://readthedocs.org/projects/pytition/badge/?version=latest)](https://pytition.readthedocs.io/en/latest/?badge=latest)

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

* [x] Multi-lingual UI with i18n: English, French, Italian, Occitan, Spanish.
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
* [x] Optional share buttons

## Future features

* [ ] Support for multi-lingual petition content: [v3.0](https://github.com/pytition/Pytition/milestone/3)
* [ ] Support for adding several petition templates: [v4.0](https://github.com/pytition/Pytition/milestone/4)
* [ ] Add optional Diaspora share icon

## Install development environment

See [dev/CONTRIBUTE.md](dev/CONTRIBUTE.md)

## Documentation (Installing in production, configuration, update etc)

See https://pytition.readthedocs.io

## Included dependencies

Those are external projects that are needed and used by Pytition, but included in Pytition source tree:

* Bootstrap 4.2.1
* JQuery 3.3.1
* Popper 1.14.6
* Open Iconic 1.1.1
* TinyMCE 4.9.2
* jQuery Smart Wizard 4

## Dependencies

* Python 3.8 up to 3.11
* Django 4.2.x
* django-tinymce 3.5.0
* django-colorfield 0.8.0
* requests 2.20.x
* mysqlclient 2.0.1
* beautifulsoup4 4.6.3
* django-formtools 2.2
* bcrypt

## Translations

| Language      | Translation % |
| ------------- | ------------- |
| English       | <a href="https://weblate.framasoft.org/engage/pytition/en/?utm_source=widget"><img src="https://weblate.framasoft.org/widgets/pytition/en/pytitions/svg-badge.svg" alt="État de la traduction" /></a>|
| French  | <a href="https://weblate.framasoft.org/engage/pytition/fr_FR/?utm_source=widget"><img src="https://weblate.framasoft.org/widgets/pytition/fr_FR/pytitions/svg-badge.svg" alt="État de la traduction" /></a>|
| Italian       | <a href="https://weblate.framasoft.org/engage/pytition/it/?utm_source=widget"><img src="https://weblate.framasoft.org/widgets/pytition/it/pytitions/svg-badge.svg" alt="État de la traduction" /></a>|
| Occitan       | <a href="https://weblate.framasoft.org/engage/pytition/oc/?utm_source=widget"><img src="https://weblate.framasoft.org/widgets/pytition/oc/pytitions/svg-badge.svg" alt="État de la traduction" /></a> |
| Spanish       | <a href="https://weblate.framasoft.org/engage/pytition/es/?utm_source=widget"><img src="https://weblate.framasoft.org/widgets/pytition/es/pytitions/svg-badge.svg" alt="État de la traduction" /></a> |
