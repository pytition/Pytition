# -*- coding: utf-8 -*-
# Generated by Django 1.11.14 on 2018-10-22 19:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('petition', '0011_pytitionuser_invitations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='petitiontemplate',
            name='background',
        ),
        migrations.RemoveField(
            model_name='petitiontemplate',
            name='mobile_background',
        ),
        migrations.RemoveField(
            model_name='petitiontemplate',
            name='top_picture',
        ),
    ]