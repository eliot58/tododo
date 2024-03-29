# Generated by Django 4.1.3 on 2023-05-22 07:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import simple_history.models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('core', '0009_alter_diler_organization_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricalDiler',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('logo', models.TextField(blank=True, max_length=100, null=True, verbose_name='Логотип')),
                ('organization', models.CharField(blank=True, default='', max_length=200, verbose_name='Организация')),
                ('warehouse_address', models.CharField(blank=True, default='', max_length=200, verbose_name='Адрес склада')),
                ('practice', models.PositiveIntegerField(default=0, verbose_name='Опыт')),
                ('isEmailsubmit', models.BooleanField(default=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('region', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.region', verbose_name='Регион')),
                ('user', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.profile', verbose_name='Дилер')),
            ],
            options={
                'verbose_name': 'historical Дилер',
                'verbose_name_plural': 'historical Дилеры',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalOrder',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('address', models.CharField(max_length=50, verbose_name='Адрес')),
                ('type_pay', models.CharField(choices=[('C', 'Карта'), ('N', 'Безнал')], max_length=4, verbose_name='Тип оплаты')),
                ('type_delivery', models.CharField(choices=[('0', 'Адрес клиента'), ('1', 'Мой склад'), ('2', 'Самовывоз')], max_length=14, verbose_name='Тип доставки')),
                ('amount_window', models.PositiveIntegerField(verbose_name='Количество окон')),
                ('price', models.FloatField(verbose_name='Желаемая цена')),
                ('comment', models.TextField(blank=True, max_length=300, null=True, verbose_name='Комментарий к заказу')),
                ('date', models.DateField(blank=True, editable=False, verbose_name='Дата создания')),
                ('file', models.TextField(max_length=100)),
                ('isactive', models.BooleanField(default=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('implement', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.implement', verbose_name='Фурнитура')),
                ('shape', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.shape', verbose_name='Профиль')),
                ('user', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.diler', verbose_name='Автор заказа')),
            ],
            options={
                'verbose_name': 'historical Заказ',
                'verbose_name_plural': 'historical Заказы',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalPrice',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('title', models.CharField(max_length=20)),
                ('price', models.PositiveBigIntegerField()),
                ('description', models.CharField(max_length=50)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'historical Подписка',
                'verbose_name_plural': 'historical Подписки',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalProvider',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('company', models.CharField(blank=True, default='', max_length=200, verbose_name='Компания')),
                ('legal_entity', models.CharField(blank=True, default='', max_length=200, verbose_name='Юридическое лицо')),
                ('product_address', models.CharField(blank=True, default='', max_length=200, verbose_name='Адрес производства')),
                ('contact_entity', models.CharField(blank=True, default='', max_length=200, verbose_name='Руководитель')),
                ('contact_phone', models.CharField(blank=True, default='', max_length=20, verbose_name='Телефон производства')),
                ('service_entity', models.CharField(blank=True, default='', max_length=200, verbose_name='Менеджер')),
                ('service_phone', models.CharField(blank=True, default='', max_length=20, verbose_name='Контактный телефон')),
                ('service_email', models.EmailField(blank=True, default='', max_length=254, verbose_name='E-mail')),
                ('logo', models.TextField(blank=True, max_length=100, null=True, verbose_name='Логотип')),
                ('description', models.TextField(blank=True, default='', verbose_name='О компании')),
                ('isEmailsubmit', models.BooleanField(default=True)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('user', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.profile', verbose_name='Поставщик')),
            ],
            options={
                'verbose_name': 'historical Поставщик',
                'verbose_name_plural': 'historical Поставщики',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.CreateModel(
            name='HistoricalQuantity',
            fields=[
                ('id', models.BigIntegerField(auto_created=True, blank=True, db_index=True, verbose_name='ID')),
                ('date_create', models.DateField(blank=True, editable=False, verbose_name='Дата создания')),
                ('date', models.DateField(verbose_name='Дата поставки')),
                ('price', models.FloatField(verbose_name='Предложенная цена')),
                ('file', models.TextField(max_length=100, verbose_name='Файл')),
                ('comment', models.TextField(null=True, verbose_name='Кооментарий')),
                ('isresponse', models.BooleanField(default=False)),
                ('history_id', models.AutoField(primary_key=True, serialize=False)),
                ('history_date', models.DateTimeField(db_index=True)),
                ('history_change_reason', models.CharField(max_length=100, null=True)),
                ('history_type', models.CharField(choices=[('+', 'Created'), ('~', 'Changed'), ('-', 'Deleted')], max_length=1)),
                ('author', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.provider', verbose_name='Автор КП')),
                ('history_user', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='+', to=settings.AUTH_USER_MODEL)),
                ('implement', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.implement', verbose_name='Фурнитура')),
                ('order', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.order', verbose_name='Заказ')),
                ('shape', models.ForeignKey(blank=True, db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='core.shape', verbose_name='Профиль')),
            ],
            options={
                'verbose_name': 'historical Комм. предложение',
                'verbose_name_plural': 'historical Комм. предложения',
                'ordering': ('-history_date', '-history_id'),
                'get_latest_by': ('history_date', 'history_id'),
            },
            bases=(simple_history.models.HistoricalChanges, models.Model),
        ),
        migrations.DeleteModel(
            name='Manager',
        ),
    ]
