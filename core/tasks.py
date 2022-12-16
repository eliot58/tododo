import json
from celery import shared_task
from .models import *
from django.conf import settings
from django.core.mail import send_mail
import requests

@shared_task
def sendmass(id, isdiler):
    if isdiler:
        order = Order.objects.get(id=id)
        m = f'Появился новый расчёт по адресу: {order.address}' + '\n' + f'Профиль: {order.shape.data}' + '\n' + f'Фурнитура: {order.implement.data}' + '\n' + f'М2: {order.amount_window}' + '\n' + 'Подробности в сервисе: дилеры-окон.рф'

        try:
            response = requests.post('https://api.telegram.org/bot5852658863:AAHezP9l75ukvpQHSD3Bt5x24kMETAeqDfY/sendMessage', json={'chat_id': '-1001881532635', 'text': m})
            response = requests.post('https://api.telegram.org/bot5852658863:AAHezP9l75ukvpQHSD3Bt5x24kMETAeqDfY/sendMessage', json={'chat_id': '-1001486998352', 'text': m})
            print(response.text)
        except Exception as e:
            print(e)
        
        for provider in Provider.objects.filter(regions__in=[order.user.region_id]):
            if provider.isEmailsubmit:
                msg = provider.company + '\n' + f'Вернитесь в сервис дилеры-окон.рф, появился новый расчёт https://xn----gtbdlmdrgbq5j.xn--p1ai/provider/response/{id}' + '\n' + 'Вы получили это сообщение, потому что были зарегистрированы на сайте дилеры-окон.рф' + '\n' + 'Если Вы не хотите получать это сообщение, то его можно отключить в разделе профиля'
                send_mail('Новый расчёт', msg, settings.EMAIL_HOST_USER, [provider.service_email], fail_silently=False)
    else:
        m = f'Зарегестрировался новый поставщик окон https://xn----gtbdlmdrgbq5j.xn--p1ai/diler/company/card/{p.id}, попробуйте разместить заказ и узнайте цену поставщика https://xn----gtbdlmdrgbq5j.xn--p1ai/diler/company/card/{p.id}'
        try:
            response = requests.post('https://api.telegram.org/bot5852658863:AAHezP9l75ukvpQHSD3Bt5x24kMETAeqDfY/sendMessage', json={'chat_id': '-1001881532635', 'text': m})
            response = requests.post('https://api.telegram.org/bot5852658863:AAHezP9l75ukvpQHSD3Bt5x24kMETAeqDfY/sendMessage', json={'chat_id': '-1001486998352', 'text': m})
            print(response.text)
        except Exception as e:
            print(e)
        p = Provider.objects.get(id=id)
        for region in p.regions.all():
            for diler in region.diler_set.all():
                msg = diler.organization + '\n' + f'Зарегестрировался новый поставщик окон https://xn----gtbdlmdrgbq5j.xn--p1ai/diler/company/card/{p.id}, попробуйте разместить заказ и узнайте цену поставщика https://xn----gtbdlmdrgbq5j.xn--p1ai/diler/company/card/{p.id}' + '\n' + 'Вы получили это сообщение, потому что были зарегистрированы на сайте дилеры-окон.рф' + '\n' + 'Если Вы не хотите получать это сообщение, то его можно отключить в разделе профиля'
                send_mail('Новый поставщик', msg, settings.EMAIL_HOST_USER, [diler.user.email], fail_silently=False)

@shared_task
def savephones(phones):
    with open("phones.json", 'r', encoding='utf-8') as f:
        d = json.load(f)
    d = d + phones

    with open('phones.json', 'w', encoding='utf-8') as f:
        json.dump(d,f,indent=4,ensure_ascii=False)
