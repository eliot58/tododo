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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.db.models import Q
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.decorators import parser_classes

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


@swagger_auto_schema(method='post',request_body=UserSigninSerializer)
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

@swagger_auto_schema(method='post',request_body=UserSignupSerializer)
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
        # newuser(f'В сервис зарегистрировался новый {spec.lower()}: {serializer.data["fullName"]}, подробнее в дилеры-окон.рф')
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
    
class DilerProfileView(views.APIView):
    def get(self, request):
        diler = DilerClass(request.user.profile.diler.logo, request.user.profile.diler.organization, request.user.profile.diler.warehouse_address, request.user.profile.diler.region_id, Region.objects.all(), request.user.profile.fio, request.user.profile.email, request.user.profile.phone_number, request.user.profile.diler.practice)
        serializer = DilerSerializer(diler)
        return Response(serializer.data, status=HTTP_200_OK)
        

    @swagger_auto_schema(request_body=DilerSerializer)
    def put(self, request):
        serializer = DilerSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            user = request.user
            user.profile.fio = serializer.data["fullName"]
            user.profile.phone_number = serializer.data['phone']
            user.profile.email = serializer.data['email']
            user.profile.save()
            user.profile.diler.organization = serializer.data['organization']
            user.profile.diler.warehouse_address = serializer.data['warehouse_address']
            try:
                user.profile.diler.logo = serializer.data['logo']
            except KeyError:
                pass
            user.profile.diler.region_id = serializer.data['region']
            user.profile.diler.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ProviderProfileView(views.APIView):
    def get(self, request):
        serializer = ProviderSerialiazer(request.user.profile.provider)
        return Response(serializer.data, status=HTTP_200_OK)
    

    @swagger_auto_schema(request_body=ProviderSerialiazer)
    def put(self, request):
        serializer = ProviderSerialiazer(instance=request.user.profile.provider, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class OrderView(views.APIView):
    @swagger_auto_schema(manual_parameters=[openapi.Parameter('id', openapi.IN_PATH, description="post id", type=openapi.TYPE_INTEGER)])
    def get(self, request, *args, **kwargs):
        try:
            serializer = OrdersSerializer(Order.objects.get(id=kwargs['pk']))
        except Order.DoesNotExist:
            return Response({'error': 'Order does not exist'}, status=HTTP_404_NOT_FOUND)
        return Response(serializer.data)

    @swagger_auto_schema(request_body=OrderCreateSerializer)
    def post(self, request):
        if request.user.profile.spec == 'D':
            serializer = OrderCreateSerializer(data=request.data)
            if serializer.is_valid(raise_exception=True):
                user = request.user
                order = user.profile.diler.order_set.create(shape_id=request.data['shape'],implement_id=request.data['implement'],address=request.data['address'], type_pay=request.data['type_pay'], type_delivery=request.data['type_delivery'], amount_window=int(request.data['amount_window']), price=request.data['price'], comment=request.data['comment'])
                files = request.FILES.getlist('file')
                f = []
                os.system('rm -rf scetch.zip')
                for file in files:
                    print(file)
                    f.append(file.temporary_file_path())
                os.system('rm -rf scetch.zip')
                patoolib.create_archive('scetch.zip',f)
                path = Path('scetch.zip')
                with path.open(mode='rb') as f:
                    order.file = File(f,name=path.name)
                    order.save()
                os.system('rm -rf scetch.zip')
                return Response(status=HTTP_201_CREATED)
            return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
        return Response(status=HTTP_403_FORBIDDEN)


    @swagger_auto_schema(request_body=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'isactive': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='isactive')
                        }))
    def patch(self, request, *args, **kwargs):
        try:
            instance = Order.objects.get(id=kwargs['pk'])
        except Order.DoesNotExist:
            return Response({'error': 'Order does not exist'})
        serializer = OrdersSerializer(instance=instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

class OrdersView(views.APIView):
    def get(self, request):
        if request.user.profile.spec == 'D':
            serializer = OrdersSerializer(Order.objects.filter(isactive=True), many = True)
            return Response(serializer.data)
        serializer = OrdersSerializer(Order.objects.filter(user__region__in=request.user.profile.provider.regions.all()), many=True)
        return Response(serializer.data)
    

class QuantityView(views.APIView):

    def get(self, request):
        if request.user.profile.spec == 'P':
            serializer = QuantitySerializer(request.user.profile.provider.quantity_set.filter(order__isactive=True), many=True)
            return Response(serializer.data)

    def patch(self, request, **kwargs):
        serializer = QuantitySerializer(instance = Quantity.objects.get(id=kwargs['pk']), data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)
    


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