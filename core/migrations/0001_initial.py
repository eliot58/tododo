# Generated by Django 4.1.3 on 2022-11-13 13:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Diler',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('logo', models.FileField(blank=True, null=True, upload_to='diler/logo', verbose_name='Логотип')),
                ('organization', models.CharField(default='', max_length=200, verbose_name='Организация')),
                ('warehouse_address', models.CharField(default='', max_length=200, verbose_name='Адрес склада')),
                ('practice', models.PositiveIntegerField(default=0, verbose_name='Опыт')),
                ('date_register', models.DateField(auto_now_add=True, verbose_name='Дата регистрации')),
                ('date_last_auth', models.DateTimeField(verbose_name='Дата последнего входа')),
                ('isEmailsubmit', models.BooleanField(default=True)),
            ],
            options={
                'verbose_name': 'Дилер',
                'verbose_name_plural': 'Дилеры',
            },
        ),
        migrations.CreateModel(
            name='Implement',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.CharField(max_length=100, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Фурнитура',
                'verbose_name_plural': 'Фурнитуры',
            },
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('address', models.CharField(max_length=50, verbose_name='Адрес')),
                ('type_pay', models.CharField(choices=[('C', 'Карта'), ('N', 'Безнал')], max_length=4, verbose_name='Тип оплаты')),
                ('type_delivery', models.CharField(choices=[('0', 'Адрес клиента'), ('1', 'Мой склад'), ('2', 'Самовывоз')], max_length=14, verbose_name='Тип доставки')),
                ('amount_window', models.PositiveIntegerField(verbose_name='Количество окон')),
                ('price', models.FloatField(verbose_name='Желаемая цена')),
                ('comment', models.TextField(blank=True, max_length=300, null=True, verbose_name='Комментарий к заказу')),
                ('date', models.DateField(auto_now_add=True, verbose_name='Дата создания')),
                ('file', models.FileField(upload_to='diler/order/files')),
                ('isactive', models.BooleanField(default=True)),
                ('implement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.implement', verbose_name='Фурнитура')),
            ],
            options={
                'verbose_name': 'Заказ',
                'verbose_name_plural': 'Заказы',
            },
        ),
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('fio', models.CharField(max_length=400, verbose_name='ФИО')),
                ('spec', models.CharField(choices=[('D', 'Дилер'), ('P', 'Поставщик окон')], max_length=9, verbose_name='Спец')),
                ('email', models.EmailField(max_length=254, primary_key=True, serialize=False, verbose_name='Почта')),
                ('phone_number', models.CharField(max_length=20, unique=True, verbose_name='Телефон')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL, verbose_name='Аккаунт')),
            ],
            options={
                'verbose_name': 'Аккаунт',
                'verbose_name_plural': 'Аккаунты',
            },
        ),
        migrations.CreateModel(
            name='Provider',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('company', models.CharField(default='', max_length=200, verbose_name='Компания')),
                ('legal_entity', models.CharField(default='', max_length=200, verbose_name='Юридическое лицо')),
                ('product_address', models.CharField(default='', max_length=200, verbose_name='Адрес производства')),
                ('contact_entity', models.CharField(default='', max_length=200, verbose_name='Руководитель')),
                ('contact_phone', models.CharField(default='', max_length=200, verbose_name='Телефон производства')),
                ('service_entity', models.CharField(default='', max_length=200, verbose_name='Менеджер')),
                ('service_phone', models.CharField(default='', max_length=200, verbose_name='Контактный телефон')),
                ('service_email', models.CharField(default='', max_length=200, verbose_name='E-mail')),
                ('logo', models.FileField(blank=True, null=True, upload_to='provider/logo', verbose_name='Логотип')),
                ('description', models.TextField(default='', verbose_name='О компании')),
                ('date_register', models.DateField(auto_now_add=True, verbose_name='Дата регистрации')),
                ('date_last_auth', models.DateTimeField(verbose_name='Дата последнего входа')),
                ('isEmailsubmit', models.BooleanField(default=True)),
                ('implements', models.ManyToManyField(to='core.implement', verbose_name='Фурнитуры')),
            ],
            options={
                'verbose_name': 'Поставщик',
                'verbose_name_plural': 'Поставщики',
            },
        ),
        migrations.CreateModel(
            name='Region',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.CharField(max_length=100, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Регион',
                'verbose_name_plural': 'Регионы',
            },
        ),
        migrations.CreateModel(
            name='Shape',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', models.CharField(max_length=100, unique=True, verbose_name='Название')),
            ],
            options={
                'verbose_name': 'Профиль',
                'verbose_name_plural': 'Профили',
            },
        ),
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_quality', models.IntegerField(default=0)),
                ('delivery_quality', models.IntegerField(default=0)),
                ('supplier_loyalty', models.IntegerField(default=0)),
                ('fr', models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, to='core.diler')),
                ('to', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.provider')),
            ],
        ),
        migrations.CreateModel(
            name='Quantity',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_create', models.DateField(auto_now_add=True)),
                ('date', models.DateField()),
                ('price', models.FloatField()),
                ('file', models.FileField(upload_to='providers/quantity/files')),
                ('comment', models.TextField(null=True)),
                ('isresponse', models.BooleanField(default=False)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.provider')),
                ('implement', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.implement')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.order')),
                ('shape', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.shape')),
            ],
        ),
        migrations.AddField(
            model_name='provider',
            name='regions',
            field=models.ManyToManyField(to='core.region', verbose_name='Регионы'),
        ),
        migrations.AddField(
            model_name='provider',
            name='shapes',
            field=models.ManyToManyField(to='core.shape', verbose_name='Профили'),
        ),
        migrations.AddField(
            model_name='provider',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.profile', verbose_name='Поставщик'),
        ),
        migrations.AddField(
            model_name='order',
            name='shape',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.shape', verbose_name='Профиль'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.diler', verbose_name='Автор заказа'),
        ),
        migrations.AddField(
            model_name='diler',
            name='region',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='core.region', verbose_name='Регион'),
        ),
        migrations.AddField(
            model_name='diler',
            name='user',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.profile', verbose_name='Дилер'),
        ),
    ]
