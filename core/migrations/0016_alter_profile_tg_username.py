# Generated by Django 4.1.3 on 2023-06-12 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_alter_profile_tg_username'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='tg_username',
            field=models.CharField(blank=True, max_length=60, null=True),
        ),
    ]
