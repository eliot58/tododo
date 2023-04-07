# Generated by Django 4.1.3 on 2023-03-30 17:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_profile_fio_alter_profile_phone_number_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='provider',
            name='implements',
            field=models.ManyToManyField(blank=True, to='core.implement', verbose_name='Фурнитуры'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='regions',
            field=models.ManyToManyField(blank=True, to='core.region', verbose_name='Регионы'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='shapes',
            field=models.ManyToManyField(blank=True, to='core.shape', verbose_name='Профили'),
        ),
    ]
