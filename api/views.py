import patoolib
from core.models import Order, Price, Shape, Implement, Region, Profile, Diler, Provider, Quantity, Review
from .serializers import *
from django.core.mail import send_mail
from rest_framework import views
import datetime
from django.utils.timezone import utc
from django.contrib.auth.models import User
from core.utils.pass_generator import generator
from django.conf import settings
import re
from django.core.files import File
from pathlib import Path
import os

from django.contrib.auth import authenticate, logout
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from core.tasks import sendmass, savephones

type_payd = {
    'Карта' : 'C', 
    'Безнал' : 'N'
}

type_deld = {
    'Адрес клиента': 0,
    'Мой склад': 1,
    'Самовывоз': 2
}

rtype_payd = {
    'C' : 'Карта', 
    'N' : 'Безнал'
}

rtype_deld = {
    0: 'Адрес клиента',
    1: 'Мой склад',
    2: 'Самовывоз'
}

@api_view(["POST"])
@permission_classes((AllowAny,))
def signin(request):
    
    user = authenticate(
            username = request.data['username'],
            password = request.data['password'] 
        )
    if not user:
        return Response({'detail': 'Invalid Credentials or activate account'}, status=status.HTTP_400_BAD_REQUEST)

    token, _ = Token.objects.get_or_create(user = user)


    return Response({
        'token': token.key
    })

@api_view(["GET"])
def token_destroyed(request):
    request.user.auth_token.delete()
    logout(request)
    return Response({'success': True})

@api_view(["GET"])
def isdiler(request):
    return Response({'success': True if request.user.profile.spec == 'D' else False})

@api_view(["GET"])
def isblanked(request):
    flag = False
    if request.user.profile.diler.organization == '' or request.user.profile.diler.warehouse_address == '' or request.user.profile.diler.region == None:
        flag = True
    return Response({'isblanked': flag})


@api_view(["GET"])
def provider_check(request, id):
    if request.user.profile.spec == 'P':
        o = Quantity.objects.get(id=id)
        if o.author_id == request.user.profile.provider.id:
            o.order.isactive = False
            o.order.save()
    return Response({'success': True})


@api_view(["GET"])
def balance(request):
    if request.user.profile.spec == 'P':
        l = []
        p = Price.objects.all()
        for ps in p:
            d = {}
            d['title'] = ps.title
            d['price'] = ps.price
            d['description'] = ps.description
            l.append(d)
    return Response(l)

@api_view(["GET"])
def send_quantity(request):
    d = []
    for quantity in request.user.profile.provider.quantity_set.all().order_by('-id'):
        if quantity.order.isactive:
            s = {}
            s['id'] = quantity.id
            s['date'] = quantity.order.date
            s['amount_window'] = quantity.order.amount_window
            s['shape'] = quantity.order.shape.data
            s['implement'] = quantity.order.implement.data
            s['order_price'] = quantity.order.price
            s['quantity_shape'] = quantity.shape.data
            s['quantity_impl'] = quantity.implement.data
            s['quantity_price'] = quantity.price
            d.append(s)
    return Response(d)

class QuantityDel(views.APIView):
    def delete(self, request, id):
        Quantity.objects.get(id=id).delete()
        return Response({'detail': True})


@api_view(['POST'])
def sign_up(request):
    password = generator(8)
    new_user = User()
    new_user.username = request.data['email']
    new_user.email = request.data['email']
    new_user.set_password(password)
    new_user.save()
    spec = 'Дилер' if request.data['spec']=='D' else 'Поставщик окон'
    try:
        p = Profile.objects.create(user=new_user,fio=request.data['fio'],spec=request.data['spec'],email=request.data['email'],phone_number=request.data['phone'])
    except:
        new_user.delete()
        return Response({'success': False})
    if request.data['spec']=='D':
        try:
            Diler.objects.create(user=p)
        except:
            new_user.delete()
            return Response({'success': False})
    else:
        try:
            Provider.objects.create(user=p)
        except:
            new_user.delete()
            return Response({'success': False})

    msg = 'Вы зарегистрировались как ' + spec + '\n' + 'Ваш login: ' + request.data['email'] + '\n' + 'Ваш password: ' + password
    try:
        send_mail('Регистрация в todotodo', msg, settings.EMAIL_HOST_USER, [request.data['email']], fail_silently=False)
    except:
        new_user.delete()
        return Response({'success': False})
    return Response({'success': True}) 

    
        
class IsUser(views.APIView):
    def post(self, request):
        if request.data['email'] == '':
            return Response({'validate': 'введите почу'})
        regx = re.match(r'^[a-zA-Z0-9.]+@[a-zA-Z0-9]+\.[a-zA-Z]+',request.data['email'])
        try:
            regx.start()
        except AttributeError:
            return Response({'validate': 'неправильная почта'})
        try:
            User.objects.get(email=request.data['email'])
        except User.DoesNotExist:
            pass
        else:
            return Response({'validate': 'Такая почта уже используется'})
        return Response({'validate': None})

class IsPhone(views.APIView):
    def post(self, request):
        if request.data['phone'] == '':
            return Response({'validate': 'введдите номер'})
        regx = re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$',request.data['phone'])
        try:
            regx.start()
        except AttributeError:
            return Response({'validate': 'номер введён неправильно'})
        try:
            Profile.objects.get(phone_number=request.data['phone'])
        except Profile.DoesNotExist:
            pass
        else:
            return Response({'validate': 'Такой номер уже используется'})
        return Response({'validate': None})



class Orders(views.APIView):
    def get(self, request):
        res = []
        if request.user.profile.spec == 'D':
            for order in request.user.profile.diler.order_set.all():
                if order.isactive:
                    d = {}
                    d['id'] = order.id
                    d['address'] = order.address
                    d['author'] = order.user.organization
                    d['date'] = order.date
                    d['shape'] = order.shape.data
                    d['implement'] = order.implement.data
                    d['price'] = order.price
                    d['count_kp'] = len(order.quantity_set.all())
                    res.append(d)
            res = sorted(res, key=lambda item: item['id'], reverse=True)
            return Response(res)
        else: 
            for region in request.user.profile.provider.regions.all():
                for diler in region.diler_set.all():
                    for order in diler.order_set.all():
                        if order.isactive:
                            d = {}
                            d['id'] = order.id
                            d['address'] = order.address
                            d['type_pay'] = rtype_payd[order.type_pay]
                            d['type_delivery'] = rtype_deld[int(order.type_delivery)]
                            d['count_win'] = order.amount_window
                            d['date'] = order.date
                            d['shape'] = order.shape.data
                            d['implement'] = order.implement.data
                            d['price'] = order.price
                            res.append(d)
            res = sorted(res, key=lambda item: item['id'], reverse=True)

            return Response(res)
    

    def post(self, request):
        user = request.user
        order = user.profile.diler.order_set.create(shape_id=Shape.objects.get(data=request.data['shape']).id,implement_id=Implement.objects.get(data=request.data['implement']).id,address=request.data['address'], type_pay=type_payd[request.data['type_pay']], type_delivery=type_deld[request.data['type_delivery']], amount_window=int(request.data['amount']), price=request.data['price'], comment=request.data['comment'])
        files = request.FILES.getlist('upl')
        f = []
        os.system('rm -rf scetch.zip')
        for file in files:
            f.append(file.temporary_file_path())
        os.system('rm -rf scetch.zip')
        patoolib.create_archive('scetch.zip',f)
        path = Path('scetch.zip')
        with path.open(mode='rb') as f:
            order.file = File(f,name=path.name)
            order.save()
        os.system('rm -rf scetch.zip')
        sendmass.delay(order.id, True)
        return Response({'success': True})


class WorkList(views.APIView):
    def get(self, request):
        if request.user.profile.spec == 'D':
            works = []
            for order in request.user.profile.diler.order_set.all():
                for quantity in order.quantity_set.all():
                    if quantity.isresponse and quantity.order.isactive:
                        d = {}
                        d['id'] = quantity.id
                        d['date'] = quantity.order.date
                        d['kpcount'] = len(order.quantity_set.all())
                        d['price'] = quantity.order.price
                        d['shape'] = quantity.order.shape.data
                        d['implement'] = quantity.order.implement.data
                        d['address'] = quantity.order.address
                        works.append(d)
            works = sorted(works, key=lambda item: item['id'], reverse=True)
            
            return Response(works)
        else:
            works = []
            for quantity in request.user.profile.provider.quantity_set.all():
                if quantity.isresponse and quantity.order.isactive:
                    d = {}
                    d['id'] = quantity.id
                    d['date'] = quantity.date
                    d['shape'] = quantity.shape.data
                    d['implement'] = quantity.implement.data
                    d['price'] = quantity.price
                    d['scetch'] = quantity.order.file.url.split('/')[-1]
                    d['file'] = quantity.file.url.split('/')[-1]
                    d['scetch_url'] = quantity.order.file.url
                    d['file_url'] = quantity.file.url
                    d['fio'] = quantity.order.user.user.fio
                    d['phone'] = quantity.order.user.user.phone_number
                    d['email'] = quantity.order.user.user.email
                    d['quantity_id'] = quantity.id
                    works.append(d)
            works = sorted(works, key=lambda item: item['id'], reverse=True)
        
            return Response(works)
        

class ArchiveList(views.APIView):
    def get(self, request):
        if request.user.profile.spec == 'D':
            review = Review.objects.filter(fr_id=request.user.profile.diler)
            to = list(map(lambda item: item.to.id, review))
            archive = []
            for order in request.user.profile.diler.order_set.all():
                for quantity in order.quantity_set.all():
                    if quantity.isresponse and not(quantity.order.isactive):
                        d = {}
                        d['id'] = quantity.id
                        d['date'] = quantity.order.date
                        d['kpcount'] = len(order.quantity_set.all())
                        d['price'] = quantity.order.price
                        d['shape'] = quantity.order.shape.data
                        d['implement'] = quantity.order.implement.data
                        d['address'] = quantity.order.address
                        d['author_id'] = quantity.author.id
                        d['author_company'] = quantity.author.company
                        d['isreview'] = quantity.author.id in to
                        archive.append(d)
            archive = sorted(archive, key=lambda item: item['id'], reverse=True)
            
            return Response(archive)
        else:
            archive = []
            for quantity in request.user.profile.provider.quantity_set.all():
                if quantity.isresponse:
                    if quantity.order.isactive:
                        pass
                    else:
                        d = {}
                        d['id'] = quantity.id
                        d['date'] = quantity.date
                        d['shape'] = quantity.shape.data
                        d['implement'] = quantity.implement.data
                        d['price'] = quantity.price
                        d['scetch'] = quantity.order.file.url.split('/')[-1]
                        d['file'] = quantity.file.url.split('/')[-1]
                        d['scetch_url'] = quantity.order.file.url
                        d['file_url'] = quantity.file.url
                        d['fio'] = quantity.order.user.user.fio
                        d['phone'] = quantity.order.user.user.phone_number
                        d['email'] = quantity.order.user.user.email
                        d['quantity_id'] = quantity.id
                        archive.append(d)
            archive = sorted(archive, key=lambda item: item['id'], reverse=True)
            return Response(archive)

class Profiles(views.APIView):
    def get(self, request):
        d = {}
        if request.user.profile.spec == 'D':
            try:
                d['logo'] = request.user.profile.diler.logo.url
            except ValueError:
                d['logo'] = None
            d['practice'] = 'Опыт: ' + str(request.user.profile.diler.practice)
            d['company'] = request.user.profile.diler.organization
            d['fio'] = request.user.profile.fio
            d['phone'] = str(request.user.profile.phone_number)
            d['email'] = request.user.profile.email
            d['warehouse_address'] = request.user.profile.diler.warehouse_address
            try:
                d['region'] = request.user.profile.diler.region.data
            except AttributeError:
                d['region'] = 'Мой регион'
            d['regions'] = ['Мой регион']   
            regions = Region.objects.all()
            for region in regions:
                d['regions'].append(region.data)
        else:
            try:
                d['logo'] = request.user.profile.provider.logo.url
            except ValueError:
                d['logo'] = None
            d['company'] = request.user.profile.provider.company
            d['legal_entity'] = request.user.profile.provider.legal_entity
            d['product_address'] = request.user.profile.provider.product_address
            d['contact_entity'] = request.user.profile.provider.contact_entity
            d['contact_phone'] = request.user.profile.provider.contact_phone
            d['service_entity'] = request.user.profile.provider.service_entity
            d['service_phone'] = request.user.profile.provider.service_phone
            d['service_email'] = request.user.profile.provider.service_email
            d['description'] = request.user.profile.provider.description
            d['shapes'] = []
            shapes = Shape.objects.all()
            for shape in shapes:
                d['shapes'].append(shape.data)
            d['implements'] = []
            implements = Implement.objects.all()
            for implement in implements:
                d['implements'].append(implement.data)
            d['regions'] = []    
            regions = Region.objects.all()
            for region in regions:
                d['regions'].append(region.data)
            d['selshapes'] = []
            for shape in request.user.profile.provider.shapes.all():
                d['selshapes'].append(shape.data)
            d['selimplements'] = []
            for implement in request.user.profile.provider.implements.all():
                d['selimplements'].append(implement.data)
            d['selregions'] = []
            for region in request.user.profile.provider.regions.all():
                d['selregions'].append(region.data)

        return Response(d)


    def post(self, request):
        if request.user.profile.spec == 'D':
            user = request.user
            user.profile.fio = request.data['fio']
            user.profile.phone_number = request.data['phone']
            user.profile.email = request.data['email']
            user.profile.save()
            user.profile.diler.organization = request.data['company']
            user.profile.diler.warehouse_address = request.data['warehouse_address']
            try:
                user.profile.diler.logo = request.FILES['logo']
            except KeyError:
                pass
            user.profile.diler.region_id = Region.objects.get(data=request.data['region']).id
            user.profile.diler.save()
        else:
            p = request.user.profile.provider
            flag = False
            if len(p.regions.all()) == 0:
                flag = True
            p.user = request.user.profile
            p.company = request.data['company']
            p.legal_entity = request.data['legal_entity']
            p.product_address = request.data['product_address']
            p.contact_entity = request.data['contact_entity']
            p.contact_phone = request.data['contact_phone']
            p.service_entity = request.data['service_entity']
            p.service_phone = request.data['service_phone']
            p.service_email = request.data['service_email']
            try: 
                p.logo = request.FILES['logo']
            except KeyError:
                pass
            p.description = request.data['description']
            p.save()
            try:
                p.shapes.clear()
                for i in request.data.getlist('shapes'):
                    p.shapes.add(Shape.objects.get(data=i))
            except KeyError:
                p.shapes.clear()
            try:
                p.implements.clear()   
                for i in request.data.getlist('implements'):
                    p.implements.add(Implement.objects.get(data=i))  
            except KeyError:
                p.implements.clear() 
            try:
                p.regions.clear()
                for i in request.data.getlist('regions'):
                    p.regions.add(Region.objects.get(data=i))
            except KeyError:
                p.regions.clear()

            if flag:
                sendmass(p.id, False)

        return Response({'success': True})




class GetData(views.APIView):
    def get(self, request):
        d = {
            'shapes' : ['Выберите профиль'],
            'implements': ['Выберите фурнитуру']
        }
        for shape in Shape.objects.all():
            d['shapes'].append(shape.data)
        for implement in Implement.objects.all():
            d['implements'].append(implement.data)
        return Response(d)


class Orderget(views.APIView):
    def get(self, request, id):
        if request.user.profile.spec == 'D':
            order = Order.objects.get(id=id)
            d = {}
            d['shape'] = order.shape.data
            d['implement'] = order.implement.data
            d['address'] = order.address
            d['type_pay'] = rtype_payd[order.type_pay]
            d['type_delivery'] = rtype_deld[int(order.type_delivery)]
            d['price'] = order.price
            d['file'] = order.file.url.split('/')[-1]
            d['fileurl'] = order.file.url
            d['comment'] = order.comment
            d['kp'] = []
            for quantity in order.quantity_set.all():
                q = {}
                q['id'] = quantity.id
                q['author_id'] = quantity.author.id
                q['author_company'] = quantity.author.company
                q['date_create'] = quantity.date_create
                q['date'] = quantity.date
                q['shape'] = quantity.shape.data
                q['implement'] = quantity.implement.data
                q['price'] = quantity.price
                q['file'] = quantity.file.url.split('/')[-1]
                q['fileurl'] = quantity.file.url
                q['isresponse'] = quantity.isresponse
                d['kp'].append(q)
            return Response(d)
        else:
            order = Order.objects.get(id=id)
            d = {}
            d['date'] = order.date
            d['shape'] = order.shape.data
            d['implement'] = order.implement.data
            d['address'] = order.address
            d['type_pay'] = rtype_payd[order.type_pay]
            d['type_delivery'] = rtype_deld[int(order.type_delivery)]
            d['price'] = order.price
            d['count_window'] = order.amount_window
            d['file'] = order.file.url.split('/')[-1]
            d['fileurl'] = order.file.url
            d['comment'] = order.comment
            d['shapes'] = ['Выберите профиль']
            for shape in request.user.profile.provider.shapes.all():
                d['shapes'].append(shape.data)
            d['implements'] = ['Выберите фурнитуру']
            for implement in request.user.profile.provider.implements.all():
                d['implements'].append(implement.data)
            
            
            return Response(d)
    def delete(self, request, id):
        if request.user.profile.spec == 'D':
            order = Order.objects.get(id=id)
            if order.user == request.user.profile.diler:
                order.delete()
        return Response({'detail': True})


class Respon(views.APIView):
    def get(self, request, id):
        if request.user.profile.spec == 'D':
            q = Quantity.objects.get(id=id)
            if request.user.profile.diler.id == q.order.user_id:
                q.isresponse = True
                q.save()
                msg = 'Дилер выбрал Ваше коммерческое предложение, для связи с ним войдите в сервис todotodo.' + '\n' + 'В разделе заказы в работе, Вы сможете взять контакты дилера.' + '\n' + 'Спасибо'
                send_mail('Ваше Коммерческое предложение выбрали', msg, settings.EMAIL_HOST_USER, [q.author.service_email], fail_silently=False)
                return Response({'detail': 'success'})
            else:
                return Response({'detail': 'lose'}, status=status.HTTP_401_UNAUTHORIZED)
    
    def post(self, request, id):
        q = Quantity()
        q.order_id = id
        q.author  = request.user.profile.provider
        q.date = datetime.datetime.strptime(request.data['date'], "%d-%m-%Y").date()
        q.shape_id = Shape.objects.get(data=request.data['shape']).id
        q.implement_id = Implement.objects.get(data=request.data['implement']).id
        q.price = request.data['price']
        q.file = request.FILES['upload']
        q.comment = request.data['comment']
        q.save()
        return Response({'success': True})


class GetProvider(views.APIView):
    def get(self, request, id):
        d = {}
        provider = Provider.objects.get(id=id)
        try:
            d['logo'] = provider.logo.url
        except ValueError:
            d['logo'] = None
        d['company'] = provider.company
        d['legal_entity'] = provider.legal_entity
        d['product_address'] = provider.product_address
        d['contact_entity'] = provider.contact_entity
        d['contact_phone'] = provider.contact_phone
        d['service_entity'] = provider.service_entity
        d['service_phone'] = provider.service_phone
        d['service_email'] = provider.service_email
        d['submitemail'] = provider.isEmailsubmit
        d['description'] = provider.description
        d['shapes'] = []
        shapes = Shape.objects.all()
        for shape in shapes:
            d['shapes'].append(shape.data)
        d['implements'] = []
        implements = Implement.objects.all()
        for implement in implements:
            d['implements'].append(implement.data)
        d['regions'] = []    
        regions = Region.objects.all()
        for region in regions:
            d['regions'].append(region.data)
        d['selshapes'] = []
        for shape in provider.shapes.all():
            d['selshapes'].append(shape.data)
        d['selimplements'] = []
        for implement in provider.implements.all():
            d['selimplements'].append(implement.data)
        d['selregions'] = []
        for region in provider.regions.all():
            d['selregions'].append(region.data)
        return Response(d)


class Reviews(views.APIView):
    def post(self, request):
        if request.user.profile.spec == 'D':
            r = Review()
            r.to_id = int(request.POST['to'])
            r.fr = request.user.profile.diler
            r.product_quality = int(request.POST['product_quality'])
            r.delivery_quality = int(request.POST['delivery_quality'])
            r.supplier_loyalty = int(request.POST['supplier_loyalty'])
            r.save()
        return Response({'success': True})

@api_view(['POST'])
def savephonelist(request):
    savephones.delay(request.data['phones'])
    
    return Response({'success': True})

