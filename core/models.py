from django.db import models
from django.contrib.auth.models import User
import os


class Region(models.Model):
    data = models.CharField(max_length=100,unique=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Регион'
        verbose_name_plural = 'Регионы'

    def __str__(self):
        return self.data

class Shape(models.Model):
    data = models.CharField(max_length=100,unique=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Профили'

    def __str__(self):
        return self.data


class Implement(models.Model):
    data = models.CharField(max_length=100,unique=True, verbose_name='Название')

    class Meta:
        verbose_name = 'Фурнитура'
        verbose_name_plural = 'Фурнитуры'

    def __str__(self):
        return self.data


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Аккаунт')
    fio = models.CharField(max_length=100, verbose_name='ФИО')
    ch = [
        ('D', 'Дилер'),
        ('P', 'Поставщик окон')
    ]
    spec = models.CharField(max_length=9, choices=ch, verbose_name='Спец')
    email = models.EmailField(primary_key=True, verbose_name='Почта')
    phone_number = models.CharField(max_length=20, unique=True, verbose_name='Телефон')

    class Meta:
        verbose_name = 'Аккаунт'
        verbose_name_plural = 'Аккаунты'

    def __str__(self):
        return self.fio


class Diler(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, verbose_name='Дилер')
    logo = models.FileField(upload_to='diler/logo', null=True, blank=True, verbose_name='Логотип')
    organization = models.CharField(max_length=200, default='', verbose_name='Организация')
    warehouse_address = models.CharField(max_length=200, default='', verbose_name='Адрес склада')
    region = models.ForeignKey(Region, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Регион')
    practice = models.PositiveIntegerField(default=0, verbose_name='Опыт')
    isEmailsubmit = models.BooleanField(default=True)


    def __str__(self):
        return self.user.fio


    class Meta:
        verbose_name = 'Дилер'
        verbose_name_plural = 'Дилеры'

class Provider(models.Model):
    user = models.OneToOneField(Profile, on_delete=models.CASCADE, verbose_name='Поставщик')
    company = models.CharField(max_length=200, default='', verbose_name='Компания')
    legal_entity = models.CharField(max_length=200, default='', verbose_name='Юридическое лицо')
    product_address = models.CharField(max_length=200, default='', verbose_name='Адрес производства')
    contact_entity = models.CharField(max_length=200, default='', verbose_name='Руководитель')
    contact_phone = models.CharField(default='', max_length=20, verbose_name='Телефон производства')
    service_entity = models.CharField(max_length=200, default='', verbose_name='Менеджер')
    service_phone = models.CharField(default='',max_length=20, verbose_name='Контактный телефон')
    service_email = models.EmailField(default='', verbose_name='E-mail')
    shapes = models.ManyToManyField(Shape, verbose_name='Профили', blank=True)
    regions = models.ManyToManyField(Region, verbose_name='Регионы', blank=True)
    implements = models.ManyToManyField(Implement, verbose_name='Фурнитуры', blank=True)
    logo = models.FileField(upload_to='provider/logo', null=True, blank=True, verbose_name='Логотип')
    description = models.TextField(default='', verbose_name='О компании')
    isEmailsubmit = models.BooleanField(default=True)

    def __str__(self):
        return self.user.fio


    class Meta:
        verbose_name = 'Поставщик'
        verbose_name_plural = 'Поставщики'


class Review(models.Model):
    to = models.ForeignKey(Provider, on_delete=models.CASCADE)
    fr = models.ForeignKey(Diler, on_delete=models.DO_NOTHING)
    product_quality = models.IntegerField(default=0)
    delivery_quality = models.IntegerField(default=0)
    supplier_loyalty = models.IntegerField(default=0)


class Order(models.Model):
    user = models.ForeignKey(Diler, on_delete=models.CASCADE, verbose_name='Автор заказа')
    shape = models.ForeignKey(Shape, on_delete=models.CASCADE, verbose_name='Профиль')
    implement = models.ForeignKey(Implement, on_delete=models.CASCADE, verbose_name='Фурнитура')
    address = models.CharField(max_length=50, verbose_name='Адрес')
    pay_ch = [
        ('C', 'Карта'),
        ('N', 'Безнал')
    ]
    type_pay = models.CharField(max_length=4, choices=pay_ch, verbose_name='Тип оплаты')
    delivery_ch = [
        ('0', 'Адрес клиента'),
        ('1', 'Мой склад'),
        ('2', 'Самовывоз')
    ]
    type_delivery = models.CharField(max_length=14, choices=delivery_ch, verbose_name='Тип доставки')
    amount_window = models.PositiveIntegerField(verbose_name='Количество окон')
    price = models.FloatField(verbose_name='Желаемая цена')
    comment = models.TextField(max_length=300, verbose_name='Комментарий к заказу', null=True, blank=True)
    date = models.DateField(auto_now_add=True, verbose_name='Дата создания')
    file = models.FileField(upload_to='diler/order/files')
    isactive = models.BooleanField(default=True)


    def filename(self):
        return os.path.basename(self.file.name)


    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'



class Quantity(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    author = models.ForeignKey(Provider, on_delete=models.CASCADE)
    date_create = models.DateField(auto_now_add=True)
    date = models.DateField()
    shape = models.ForeignKey(Shape, on_delete=models.CASCADE)
    implement = models.ForeignKey(Implement, on_delete=models.CASCADE)
    price = models.FloatField()
    file = models.FileField(upload_to='providers/quantity/files')
    comment = models.TextField(null=True)
    isresponse = models.BooleanField(default=False)


    def filename(self):
        return os.path.basename(self.file.name)


class Price(models.Model):
    title = models.CharField(max_length=20)
    price = models.PositiveBigIntegerField()
    description = models.CharField(max_length=50)


    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'