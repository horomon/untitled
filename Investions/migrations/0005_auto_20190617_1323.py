# Generated by Django 2.2 on 2019-06-17 13:23

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('Investions', '0004_contacts'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='contacts',
            options={'verbose_name': 'Site Contact', 'verbose_name_plural': 'Site Contacts'},
        ),
        migrations.AlterModelOptions(
            name='investactive',
            options={'verbose_name': 'Investition Active', 'verbose_name_plural': 'Investition Actives'},
        ),
        migrations.AlterModelOptions(
            name='investplan',
            options={'verbose_name': 'Investition Plan', 'verbose_name_plural': 'Investition Plans'},
        ),
    ]
