from django.contrib.auth import authenticate, logout
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_403_FORBIDDEN
)
from rest_framework.response import Response

from core.utils.pass_generator import generator

from .serializers import *

from core.tasks import *

from .authentication import *

from rest_framework import generics, views
from django.db.models import Q

from django.core.files import File
from pathlib import Path
import patoolib

class DilerClass:
    def __init__(self, logo, organization, warehouse_address, region, regions, fullName, email, phone, practice):
        self.logo  = logo
        self.organization = organization
        self.warehouse_address = warehouse_address
        self.region = region
        self.regions = regions
        self.fullName = fullName
        self.email = email
        self.phone = phone
        self.practice = practice


class ProviderClass:
    def __init__(self, logo, company, legal_entity, product_address, contact_entity, contact_phone, service_entity, service_phone, service_email, shapes, regions, implements, description, shapes_select, implements_select, regions_select):
        self.logo  = logo
        self.company = company
        self.legal_entity = legal_entity
        self.product_address = product_address
        self.contact_entity = contact_entity
        self.contact_phone = contact_phone
        self.service_entity = service_entity
        self.service_phone = service_phone
        self.service_email = service_email
        self.shapes = shapes
        self.regions = regions
        self.implements = implements
        self.description = description
        self.shapes_select = shapes_select
        self.implements_select = implements_select
        self.regions_select = regions_select


class ItemClass:
    def __init__(self, shapes, implements):
        self.shapes_select = shapes
        self.implements_select = implements


@api_view(["POST"])
def phonesSend(request):
    savephones.delay(request.user.profile.provider.id, request.data)
    return Response(status=HTTP_200_OK)





@api_view(["POST"])
@permission_classes((AllowAny,))
def signin(request):
    serializer = UserSigninSerializer(data = request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status = HTTP_400_BAD_REQUEST)


    user = authenticate(
        username = serializer.data['email'],
        password = serializer.data['password'] 
    )
    if not user:
        return Response({'detail': 'Invalid Credentials or activate account'}, status=HTTP_404_NOT_FOUND)

        
    token, _ = Token.objects.get_or_create(user = user)

    return Response({
        'token': token.key,
        'spec': user.profile.spec
    }, status=HTTP_200_OK)

@api_view(["POST"])
@permission_classes((AllowAny,))
def signup(request):
    serializer = UserSignupSerializer(data = request.data)
    if not serializer.is_valid(raise_exception=True):
        return Response(serializer.errors, status = HTTP_400_BAD_REQUEST)

    password = generator(8)
    
    new_user = User()
    new_user.username = serializer.data['email']
    new_user.email = serializer.data['email']
    new_user.set_password(password)
    new_user.save()

    spec = 'Дилер' if serializer.data['spec']=='D' else 'Поставщик окон'

    profile = Profile.objects.create(user=new_user,fio=serializer.data['fullName'],spec=serializer.data['spec'],email=serializer.data['email'],phone_number=serializer.data['phoneNumber'])

    if serializer.data['spec']=='D':
        Diler.objects.create(user=profile)
    else:
        Provider.objects.create(user=profile)
    

    msg = 'Вы зарегистрировались как ' + spec + '\n' + 'Ваш login: ' + serializer.data['email'] + '\n' + 'Ваш password: ' + password
    try:
        send_mail('Регистрация в todotodo', msg, settings.EMAIL_HOST_USER, [serializer.data['email']], fail_silently=False)
        newuser.delay(f'В сервис зарегистрировался новый {spec.lower()}: {serializer.data["fullName"]}, подробнее в дилеры-окон.рф')
    except:
        new_user.delete()
        return Response({'detail': 'Invalid Credentials'}, status=HTTP_400_BAD_REQUEST)

    return Response({'detail': 'Success Sign-Up'}, status=HTTP_200_OK)


@api_view(["DELETE"])
def token_destroyed(request):
    request.user.auth_token.delete()
    logout(request)
    return Response({'detail': 'Success logout'}, status=HTTP_200_OK)

@api_view(['GET'])
def isblank(request):
    if request.user.profile.diler.organization == '' or request.user.profile.diler.warehouse_address == '' or request.user.profile.diler.region == None:
        return Response({'isblanked': False})
    return Response({'isblanked': True})

@api_view(['GET'])
def isdiler(request):
    return Response({"success": True if request.user.profile.spec == 'D' else False})

@api_view(["GET"])
def submit(request, id):
    if request.user.profile.spec == 'P':
        o = Quantity.objects.get(id=id)
        if o.author_id == request.user.profile.provider.id:
            o.order.isactive = False
            o.order.save()
        else:
            return Response(data = {'success': True, "detail": None, "data": o}, status=HTTP_403_FORBIDDEN)
    else:
        o = Quantity.objects.get(id=id)
        if request.user.profile.diler.id == o.order.user_id:
            o.isresponse = True
            o.save()
    return Response(data = {'success': True, "detail": None, "data": o}, status=HTTP_200_OK)
    
class DilerProfileView(views.APIView):
    def get(self, request):
        diler = DilerClass(request.user.profile.diler.logo, request.user.profile.diler.organization, request.user.profile.diler.warehouse_address, request.user.profile.diler.region_id, Region.objects.all().order_by("id"), request.user.profile.fio, request.user.profile.email, request.user.profile.phone_number, request.user.profile.diler.practice)
        serializer = DilerSerializer(diler)
        return Response(serializer.data, status=HTTP_200_OK)
        
    def patch(self, request):
        serializer = DilerSerializer(data=request.data, partial=True)
        if serializer.is_valid():
            user = request.user
            user.profile.fio = serializer.validated_data["fullName"]
            user.profile.phone_number = serializer.validated_data["phone"]
            user.profile.email = serializer.validated_data["email"]
            user.profile.save()
            user.profile.diler.organization = serializer.validated_data["organization"]
            user.profile.diler.warehouse_address = serializer.validated_data["warehouse_address"]
            try:
                user.profile.diler.logo = serializer.validated_data['logo']
            except KeyError:
                pass
            user.profile.diler.region_id = serializer.validated_data.get("region", user.profile.diler.region_id)
            user.profile.diler.save()
            return Response({"status": "success", "detail": None, "data": None}, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ProviderProfileView(views.APIView):
    def get(self, request):
        provider = ProviderClass(company=request.user.profile.provider.company, legal_entity=request.user.profile.provider.legal_entity, product_address=request.user.profile.provider.product_address, contact_entity=request.user.profile.provider.contact_entity, contact_phone=request.user.profile.provider.contact_phone, service_entity=request.user.profile.provider.service_entity, service_email=request.user.profile.provider.service_email, service_phone=request.user.profile.provider.service_phone, shapes=request.user.profile.provider.shapes, regions=request.user.profile.provider.regions, implements=request.user.profile.provider.implements, shapes_select=Shape.objects.all().order_by("id"), implements_select=Implement.objects.all().order_by("id"), regions_select=Region.objects.all().order_by("id"), description=request.user.profile.provider.description, logo=request.user.profile.provider.logo)
        serializer = ProviderSerialiazer(provider)
        return Response(serializer.data, status=HTTP_200_OK)
    
    def patch(self, request):
        serializer = ProviderSerialiazer(instance=request.user.profile.provider, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class OrderView(views.APIView):
    def get(self, request):
        try:
            serializer = OrdersSerializer(Order.objects.get(id=request.query_params.get('id')))
        except Order.DoesNotExist:
            return Response({'error': 'Order does not exist'}, status=HTTP_404_NOT_FOUND)
        return Response(serializer.data)

    def post(self, request):
        if request.user.profile.spec == 'D':
            serializer = OrderCreateSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = request.user
                order = user.profile.diler.order_set.create(shape=serializer.validated_data['shape'],implement=serializer.validated_data['implement'],address=serializer.validated_data['address'], type_pay=serializer.validated_data['type_pay'], type_delivery=serializer.validated_data['type_delivery'], amount_window=int(serializer.validated_data['amount_window']), price=serializer.validated_data['price'], comment=serializer.validated_data['comment'])
                files = serializer.validated_data["files"]
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
                return Response(status=HTTP_201_CREATED)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        return Response(status=HTTP_403_FORBIDDEN)
    
    def delete(self, request):
        order = Order.objects.get(id=request.query_params.get('id'))
        if order.user != request.user.profile.diler:
            return Response(status=HTTP_403_FORBIDDEN)
        order.delete()
        return Response(data={"status": "success"}, status=HTTP_200_OK)



class OrdersView(views.APIView):
    def get(self, request):
        if request.user.profile.spec == 'D':
            serializer = OrdersSerializer(Order.objects.filter(Q(user__id=request.user.profile.diler.id) & Q(isactive=True)).order_by("-id"), many = True)
            return Response(serializer.data)
        serializer = OrdersSerializer(Order.objects.filter(user__region__in=request.user.profile.provider.regions.all()).order_by("-id"), many=True)
        return Response(serializer.data)
    

class QuantityView(views.APIView):

    def get(self, request):
        if request.user.profile.spec == 'P':
            serializer = QuantitySerializer(request.user.profile.provider.quantity_set.filter(order__isactive=True), many=True)
            return Response(serializer.data)
        

    def post(self, request):
        if request.user.profile.spec == "P":
            serializer = CreateQuantitySerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                q = Quantity()
                q.order = serializer.validated_data['order']
                q.author  = request.user.profile.provider
                q.date = serializer.validated_data['date']
                q.shape = serializer.validated_data['shape']
                q.implement = serializer.validated_data['implement']
                q.price = serializer.validated_data['price']
                q.file = serializer.validated_data['file']
                q.comment = serializer.validated_data['comment']
                q.save()
                return Response(status=HTTP_201_CREATED)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        return Response(status=HTTP_403_FORBIDDEN)
    


class ArchiveList(views.APIView):
    
    def get(self, request):
        if request.user.profile.spec == 'D':
            serializer = QuantitySerializer(Quantity.objects.filter(Q(order__user=request.user.profile.diler) & Q(isresponse=True) & Q(order__isactive=False)), many=True)
            return Response(serializer.data)
        serializer = QuantitySerializer(Quantity.objects.filter(Q(author__id=request.user.profile.provider.id) & Q(isresponse=True) & Q(order__isactive=False)), many=True)
        return Response(serializer.data)


class WorkList(views.APIView):
    
    def get(self, request):
        if request.user.profile.spec == 'D':
            serializer = QuantitySerializer(Quantity.objects.filter(Q(order__user__id=request.user.profile.diler.id) & Q(isresponse=True) & Q(order__isactive=True)), many=True)
            return Response(serializer.data)
        serializer = QuantitySerializer(Quantity.objects.filter(Q(author__id=request.user.profile.provider.id) & Q(isresponse=True) & Q(order__isactive=True)),many=True)
        return Response(serializer.data)
    


class ItemsList(views.APIView):

    def get(self, request):
        if not request.user.is_authenticated:
            return Response(status=HTTP_403_FORBIDDEN)
        serializer = ItemsSerializer(ItemClass(shapes=Shape.objects.all().order_by("id"), implements=Implement.objects.all().order_by("id")))
        return Response(serializer.data)
    

class PriceList(generics.ListAPIView):
    queryset = Price.objects.all().order_by("price")
    serializer_class = PriceSerializer
    


class CompanyView(views.APIView):
    def get(self, request, *args, **kwargs):
        if request.user.profile.spec == 'D':
            return Response(status=HTTP_403_FORBIDDEN)
        company_serializer = ProviderSerialiazer(Provider.objects.get(id=kwargs["id"]))
        reviews_serializer = ReviewSerializer(Review.objects.filter(to_id=kwargs["id"]))
        return Response(data={'company': company_serializer.data, 'reviews': reviews_serializer.data})