# Generated by Django 3.2 on 2023-01-06 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petition', '0016_signature_uses_phone_number_field'),
    ]

    operations = [
        migrations.AddField(
            model_name='petitiontemplate',
            name='paper_signatures_enabled',
            field=models.BooleanField(default=False),
        ),
    ]
