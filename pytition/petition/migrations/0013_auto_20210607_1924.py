# Generated by Django 2.2.16 on 2021-06-07 17:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('petition', '0012_pytitionuser_moderated'),
    ]

    operations = [
        migrations.AlterField(
            model_name='moderation',
            name='reason',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='petition.ModerationReason'),
        ),
    ]
