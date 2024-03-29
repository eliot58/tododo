# Generated by Django 4.1.3 on 2023-05-21 12:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_providercomment_dilercomment'),
    ]

    operations = [
        migrations.AlterField(
            model_name='diler',
            name='organization',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Организация'),
        ),
        migrations.AlterField(
            model_name='diler',
            name='warehouse_address',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Адрес склада'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='company',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Компания'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='contact_entity',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Руководитель'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='contact_phone',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='Телефон производства'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='description',
            field=models.TextField(blank=True, default='', verbose_name='О компании'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='legal_entity',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Юридическое лицо'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='product_address',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Адрес производства'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='service_email',
            field=models.EmailField(blank=True, default='', max_length=254, verbose_name='E-mail'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='service_entity',
            field=models.CharField(blank=True, default='', max_length=200, verbose_name='Менеджер'),
        ),
        migrations.AlterField(
            model_name='provider',
            name='service_phone',
            field=models.CharField(blank=True, default='', max_length=20, verbose_name='Контактный телефон'),
        ),
    ]
