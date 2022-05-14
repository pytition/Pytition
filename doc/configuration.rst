Configuration
*************

A configuration example is provided in `pytition/settings/config_example.py`.
You should copy and edit it to configure Pytition.


Mandatory settings
==================

You **must** set the following variables:

.. automodule:: pytition.settings.config_example
  :members:

.. warning:: The ``TINYMCE_JS_URL`` setting must be present in your config file if you modified the ``STATIC_URL`` setting from its default value (``/static/``), either before of after the ``DO NOT EDIT AFTER THIS BANNER``. It is already present in the config_example.py file.

Not mandatory but important settings
====================================

You are **highly encouraged** to set the following variables in a production environment:

Pytition specific settings
--------------------------

.. autodata:: pytition.settings.base.USE_MAIL_QUEUE
.. autodata:: pytition.settings.base.ALLOW_REGISTER
.. autodata:: pytition.settings.base.DEFAULT_NOREPLY_MAIL

Django settings
---------------

The following settings are important to set so that the email sent by Pytition are less likely to be considered as spam/junk.
You should configure a real SMTP email account and not just rely on "fake" email address from local sendmail:

.. hlist::

  * :django:setting:`DEFAULT_FROM_EMAIL`
  * :django:setting:`SERVER_EMAIL`
  * :django:setting:`EMAIL_HOST`
  * :django:setting:`EMAIL_HOST_PASSWORD`
  * :django:setting:`EMAIL_HOST_USER`
  * :django:setting:`EMAIL_PORT`
  * :django:setting:`EMAIL_USE_TLS`
  * :django:setting:`EMAIL_USE_SSL`
  * others when necessary

Other optional settings
=======================

Those are things you can configure to customize your Pytition instance:

.. autodata:: pytition.settings.base.SITE_NAME
.. autodata:: pytition.settings.base.FOOTER_TEMPLATE
.. autodata:: pytition.settings.base.DISABLE_USER_PETITION
.. autodata:: pytition.settings.base.RESTRICT_ORG_CREATION
