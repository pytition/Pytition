# Generated by Django 2.2.28 on 2022-12-09 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('petition', '0017_petitiontemplate_paper_signatures_enabled'),
    ]

    operations = [
        migrations.AddField(
            model_name='petition',
            name='publication_date',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
