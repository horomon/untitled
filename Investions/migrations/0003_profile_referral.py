# Generated by Django 2.2 on 2019-06-15 16:08

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('referrals', '0002_auto_20180130_0904'),
        ('Investions', '0002_auto_20190615_1015'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='referral',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='referrals.Referral'),
        ),
    ]