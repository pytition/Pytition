Configuration
*************

A configuration example is provided in `pytition/settings/config_example.py`.
You should copy and edit it to configure Pytition.


Mandatory settings
==================

You **must** set the following variables:

.. automodule:: pytition.settings.config_example
  :members:

Not mandatory but important settings
====================================

You are **highly encouraged** to set the following variables in a production environment:

Pytition specific settings
--------------------------

.. autodata:: pytition.settings.base.USE_MAIL_QUEUE
.. autodata:: pytition.settings.base.ALLOW_REGISTER
.. autodata:: pytition.settings.base.DEFAULT_NOREPLY_MAIL
.. autodata:: pytition.settings.base.MODERATION_EMAIL

Django settings
---------------

The following settings are important to set so that the email sent by Pytition are less likely to be considered as spam/junk.
You should configure a real SMTP email account and not just rely on "fake" email address from local sendmail:

.. hlist::

  * :setting:`DEFAULT_FROM_EMAIL`
  * :setting:`SERVER_EMAIL`
  * :setting:`EMAIL_HOST`
  * :setting:`EMAIL_HOST_PASSWORD`
  * :setting:`EMAIL_HOST_USER`
  * :setting:`EMAIL_PORT`
  * :setting:`EMAIL_USE_TLS`
  * :setting:`EMAIL_USE_SSL`
  * others when necessary

Spam-fighting related settings
==============================

.. autodata:: pytition.settings.base.SPAM_DETECTORS
.. autodata:: pytition.settings.base.FORBIDDEN_WORDS
.. autodata:: pytition.settings.base.AKISMET_KEY
.. autodata:: pytition.settings.base.AKISMET_URL
.. autodata:: pytition.settings.base.AKISMET_MODERATION_AUTO
.. autodata:: pytition.settings.base.SEND_MONITORING_MAIL_TO_USER

Monitoring and moderation thresholds
------------------------------------

Pytition checks if petitions and or users behave weirldy in order to detect abuses.

Set variable to 0 if you want to disable a test.

Signature variation from one day to the next
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autodata:: pytition.settings.base.SIGNATURE_VARIATION_CRITICAL
.. autodata:: pytition.settings.base.SIGNATURE_VARIATION_STRONG
.. autodata:: pytition.settings.base.SIGNATURE_VARIATION_AVERAGE
.. autodata:: pytition.settings.base.SIGNATURE_VARIATION_LOW

Total signature numbers according to monitoring priorities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autodata:: pytition.settings.base.SIGNATURE_NUMBER_CRITICAL
.. autodata:: pytition.settings.base.SIGNATURE_NUMBER_STRONG
.. autodata:: pytition.settings.base.SIGNATURE_NUMBER_AVERAGE
.. autodata:: pytition.settings.base.SIGNATURE_NUMBER_LOW

Number of unconfirmed signatures in the last 6h according to monitoring priorities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autodata:: pytition.settings.base.UNCONFIRMED_NUMBER_CRITICAL
.. autodata:: pytition.settings.base.UNCONFIRMED_NUMBER_STRONG
.. autodata:: pytition.settings.base.UNCONFIRMED_NUMBER_AVERAGE
.. autodata:: pytition.settings.base.UNCONFIRMED_NUMBER_LOW

Number of signatures in 24h after the creation of the petition according to monitoring priorities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autodata:: pytition.settings.base.CREATION_NUMBER_CRITICAL
.. autodata:: pytition.settings.base.CREATION_NUMBER_STRONG
.. autodata:: pytition.settings.base.CREATION_NUMBER_AVERAGE
.. autodata:: pytition.settings.base.CREATION_NUMBER_LOW

Maximum numbers of petitions created in one day by a user or an organization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autodata:: pytition.settings.base.DAY_PETITION_CRITICAL
.. autodata:: pytition.settings.base.DAY_PETITION_STRONG
.. autodata:: pytition.settings.base.DAY_PETITION_AVERAGE
.. autodata:: pytition.settings.base.DAY_PETITION_LOW

Maximum numbers of monitored or moderated petitions for a user or an organization
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Checked at the creation of a petition

.. autodata:: pytition.settings.base.MONITORED_PETITIONS_CRITICAL
.. autodata:: pytition.settings.base.MONITORED_PETITIONS_STRONG
.. autodata:: pytition.settings.base.MONITORED_PETITIONS_AVERAGE
.. autodata:: pytition.settings.base.MONITORED_PETITIONS_LOW

Maximum total numbers of signatures for a user’s or an organization’s petitions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. autodata:: pytition.settings.base.SIGNATURES_TOTAL_CRITICAL
.. autodata:: pytition.settings.base.SIGNATURES_TOTAL_STRONG
.. autodata:: pytition.settings.base.SIGNATURES_TOTAL_AVERAGE
.. autodata:: pytition.settings.base.SIGNATURES_TOTAL_LOW


Other optional settings
=======================

Those are things you can configure to customize your Pytition instance:

.. autodata:: pytition.settings.base.SITE_NAME
.. autodata:: pytition.settings.base.FOOTER_TEMPLATE
.. autodata:: pytition.settings.base.DISABLE_USER_PETITION
.. autodata:: pytition.settings.base.RESTRICT_ORG_CREATION
.. autodata:: pytition.settings.base.NUMBER_OF_DAYS_FOR_EXPIRATION
