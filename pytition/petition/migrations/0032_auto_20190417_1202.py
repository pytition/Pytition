# Generated by Django 2.2 on 2019-04-17 10:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('petition', '0031_petition_slugs'),
    ]

    operations = [
        migrations.AlterField(
            model_name='slugownership',
            name='organization',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='petition.Organization'),
        ),
        migrations.AlterField(
            model_name='slugownership',
            name='user',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, to='petition.PytitionUser'),
        ),
    ]