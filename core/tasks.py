from celery import shared_task
from .models import *
from django.conf import settings
from django.core.mail import send_mail
import requests
from openpyxl import Workbook
import uuid

@shared_task
def sendmass(id, isdiler):
    if isdiler:
        order = Order.objects.get(id=id)
        m = f'Появился новый расчёт по адресу: {order.address}' + '\n' + f'Профиль: {order.shape.data}' + '\n' + f'Фурнитура: {order.implement.data}' + '\n' + f'М2: {order.amount_window}' + '\n' + 'Подробности в сервисе: дилеры-окон.рф'

        try:
            requests.post('https://api.telegram.org/bot5852658863:AAHezP9l75ukvpQHSD3Bt5x24kMETAeqDfY/sendMessage', json={'chat_id': '-1001881532635', 'text': m})
            requests.post('https://api.telegram.org/bot5852658863:AAHezP9l75ukvpQHSD3Bt5x24kMETAeqDfY/sendMessage', json={'chat_id': '-1001486998352', 'text': m})
        except Exception as e:
            print(e)
        
        for provider in Provider.objects.filter(regions__in=[order.user.region_id]):
            if provider.isEmailsubmit:
                msg = provider.company + '\n' + f'Вернитесь в сервис дилеры-окон.рф, появился новый расчёт https://xn----gtbdlmdrgbq5j.xn--p1ai/provider/response/{id}' + '\n' + 'Вы получили это сообщение, потому что были зарегистрированы на сайте дилеры-окон.рф' + '\n' + 'Если Вы не хотите получать это сообщение, то его можно отключить в разделе профиля'
                send_mail('Новый расчёт', msg, settings.EMAIL_HOST_USER, [provider.service_email], fail_silently=False)
    else:
        m = f'Зарегестрировался новый поставщик окон https://xn----gtbdlmdrgbq5j.xn--p1ai/diler/company/card/{id}, попробуйте разместить заказ и узнайте цену поставщика https://xn----gtbdlmdrgbq5j.xn--p1ai/diler/company/card/{id}'
        try:
            requests.post('https://api.telegram.org/bot5852658863:AAHezP9l75ukvpQHSD3Bt5x24kMETAeqDfY/sendMessage', json={'chat_id': '-1001881532635', 'text': m})
            requests.post('https://api.telegram.org/bot5852658863:AAHezP9l75ukvpQHSD3Bt5x24kMETAeqDfY/sendMessage', json={'chat_id': '-1001486998352', 'text': m})
        except Exception as e:
            print(e)
        p = Provider.objects.get(id=id)
        for region in p.regions.all():
            for diler in region.diler_set.all():
                msg = diler.organization + '\n' + f'Зарегестрировался новый поставщик окон https://xn----gtbdlmdrgbq5j.xn--p1ai/diler/company/card/{p.id}, попробуйте разместить заказ и узнайте цену поставщика https://xn----gtbdlmdrgbq5j.xn--p1ai/diler/company/card/{p.id}' + '\n' + 'Вы получили это сообщение, потому что были зарегистрированы на сайте дилеры-окон.рф' + '\n' + 'Если Вы не хотите получать это сообщение, то его можно отключить в разделе профиля'
                send_mail('Новый поставщик', msg, settings.EMAIL_HOST_USER, [diler.user.email], fail_silently=False)

@shared_task
def newuser(msg):
    try:
        requests.post('https://api.telegram.org/bot5852658863:AAHezP9l75ukvpQHSD3Bt5x24kMETAeqDfY/sendMessage', json={'chat_id': '-1001881532635', 'text': msg})
    except Exception as e:
        print(e)

@shared_task
def savephones(provider, phones):
    excel_file = Workbook()
    excel_sheet = excel_file.create_sheet(title='contacts', index=0)

    
    for i in range(len(phones)):
        excel_sheet[f"A{i+1}"] = phones["fullName"]
        excel_sheet[f"B{i+1}"] = phones["phone"]

    filename = f"provider/contacts/{uuid.uuid4()}.xlsx"
    
    excel_file.save(filename=filename)

    try:
        contacts = Contacts.objects.get(user_id=provider.id)
        contacts.file = "https://xn----gtbdlmdrgbq5j.xn--p1ai/media/" + filename
        contacts.save()
    except Contacts.DoesNotExist:
        contacts = Contacts()
        contacts.user = provider
        contacts.file = "https://xn----gtbdlmdrgbq5j.xn--p1ai/media/" + filename
        contacts.save()
