from django.contrib.auth import authenticate, logout
from rest_framework.authtoken.models import Token
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
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


class DilerSave:
    def __init__(self, logo, organization, warehouse_address, region, regions, fullName, email, phone):
        self.logo  = logo
        self.organization = organization
        self.warehouse_address = warehouse_address
        self.region = region
        self.regions = regions
        self.fullName = fullName
        self.email = email
        self.phone = phone


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
    }, status=HTTP_200_OK)

@swagger_auto_schema(method='post',request_body=UserSignupSerializer)
@api_view(["POST"])
@permission_classes((AllowAny,))
def signup(request):
    serializer = UserSignupSerializer(data = request.data)
    if not serializer.is_valid():
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
        newuser(f'В сервис зарегистрировался новый {spec.lower()}: {serializer.data["fullName"]}, подробнее в дилеры-окон.рф')
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


class ProfileUpdate(generics.UpdateAPIView):
    serializer_class = ProfileSerializer

class DilerProfile(views.APIView):

    def get(self, request):
        profile = request.user.profile
        diler = DilerSave(profile.diler.logo, profile.diler.organization, profile.diler.warehouse_address, profile.diler.region, Region.objects.all(), profile.fio, profile.email, profile.phone_number)
        serializer = DilerSerializer(diler)
        return Response(serializer.data, status=HTTP_200_OK)

    @swagger_auto_schema(request_body=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'logo': openapi.Schema(type=openapi.TYPE_FILE, description='Логотип'),
                            'organization': openapi.Schema(type=openapi.TYPE_STRING, description='Организация'),
                            'warehouse_address': openapi.Schema(type=openapi.TYPE_STRING, description='Адрес склада'),
                            'region': openapi.Schema(type=openapi.TYPE_INTEGER, description='Регион'),
                        }))
    def patch(self, request):
        serializer = DilerSerializer(instance = request.user.profile.diler,data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)


class ProviderProfile(views.APIView):

    def get(self, request):
        serializer = ProviderSerializer(request.user.profile.provider)
        return Response(serializer.data, status=HTTP_200_OK)

    @swagger_auto_schema(request_body=ProviderSerializer)
    def patch(self, request):
        serializer = ProviderSerializer(instance=request.user.profile.provider, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=HTTP_400_BAD_REQUEST)

    
        
class OrderView(views.APIView):
    
    def get(self, request, *args, **kwargs):
        
        try:
            serializer = OrdersSerializer(Order.objects.get(id=kwargs['pk']))
        except Order.DoesNotExist:
            return Response({'error': 'Order does not exist'}, status=HTTP_404_NOT_FOUND)
        return Response(serializer.data)


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
        serializer = OrdersSerializer(Order.objects.filter(user__region__in=request.user.profile.provider.regions.all()))
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
            serializer = QuantitySerializer(Quantity.objects.filter(Quantity.objects.filter(Q(order__user__id=request.user.profile.diler.id) & Q(isresponse=True) & Q(order__isactive=True))), many=True)
            return Response(serializer.data)
        serializer = QuantitySerializer(Quantity.objects.filter(Quantity.objects.filter(Q(author__id=request.user.profile.profile.id) & Q(isresponse=True) & Q(order__isactive=True))), many=True)
        return Response(serializer.data)


class PriceList(generics.ListAPIView):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer


class ReviewView(generics.ListCreateAPIView):
    serializer_class = ReviewSerializer

    def get_queryset(self, **kwargs):
        return Review.objects.filter(to_id=kwargs['pk'])
    



    






    

