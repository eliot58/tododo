import re
from rest_framework import serializers
from core.models import *
from django.contrib.auth.hashers import check_password

class UserSigninSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        try:
            user = User.objects.get(username=data['email'])
        except User.DoesNotExist:
            raise serializers.ValidationError('Неверный email или пароль')
        else:
            if not(check_password(data['password'], user.password)):
                raise serializers.ValidationError('Неверный email или пароль')
        return data

class UserSignupSerializer(serializers.Serializer):
    ch = [
        ('D', 'Дилер'),
        ('P', 'Поставщик окон')
    ]
    spec = serializers.ChoiceField(choices=ch)
    fullName = serializers.CharField(max_length = 100)
    email = serializers.EmailField()
    phoneNumber = serializers.CharField(max_length=20)


    def validate(self, data):
        error = {}
        try:
            User.objects.get(username=data['email'])
        except User.DoesNotExist:
            pass
        else:
            error['email'] = ['Пользователь с такой почтой уже есть']
        regx = re.match(r'^(\+7|7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$',data['phoneNumber'])
        try:
            regx.start()
        except AttributeError:
            error['phone'] = ['Введите правильный номер (+79855310868)']
        try:
            Profile.objects.get(phone_number=data['phoneNumber'])
        except Profile.DoesNotExist:
            pass
        else:
            error['phone'] = ['Пользователь с таким номером уже есть']
            

        if len(error.items()) != 0:
            raise serializers.ValidationError(error)

        return data
    

class ShapeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shape
        fields = '__all__'

class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ['data']

class ImplementSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Implement
        fields = '__all__'


class DilerSerializer(serializers.Serializer):
    fullName = serializers.CharField(max_length=100)
    phone = serializers.CharField(max_length=12)
    email = serializers.EmailField()
    organization = serializers.CharField(max_length=200)
    warehouse_address = serializers.CharField(max_length=200)
    practice = serializers.IntegerField()
    logo = serializers.FileField(required=False, allow_null=True)
    region = serializers.IntegerField()
    regions = RegionSerializer(many = True, read_only = True)


class ProviderSerialiazer(serializers.ModelSerializer):
    shapes_select = ShapeSerializer(many=True, read_only = True)
    implements_select = ImplementSerializer(many=True, read_only = True)
    regions_select = RegionSerializer(many=True, read_only = True)

    def update(self, instance, validated_data):
        instance.company = validated_data.get('company', instance.company)
        instance.legal_entity = validated_data.get('legal_entity', instance.legal_entity)
        instance.product_address = validated_data.get('product_address', instance.product_address)
        instance.contact_entity = validated_data.get('contact_entity', instance.contact_entity)
        instance.contact_phone = validated_data.get('contact_phone', instance.contact_phone)
        instance.service_entity = validated_data.get('service_entity', instance.service_entity)
        instance.service_phone = validated_data.get('service_phone', instance.service_phone)
        instance.service_email = validated_data.get('service_email', instance.service_email)
        instance.shapes.clear()
        for shape in validated_data['shapes']:
            instance.shapes.add(shape)
        instance.implements.clear()
        for implement in validated_data['implements']:
            instance.implements.add(implement)
        instance.regions.clear()
        for region in validated_data['regions']:
            instance.regions.add(region)
        instance.logo = validated_data.get('logo', instance.logo)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance

    class Meta:
        model = Provider
        fields = ['company', 'legal_entity', 'product_address', 'contact_entity', 'contact_phone', 'service_entity', 'service_phone', 'service_email', 'shapes', 'regions', 'implements', 'logo', 'description', 'shapes_select', 'implements_select', 'regions_select']



class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['user', 'shape', 'implement', 'address', 'type_pay', 'type_delivery', 'amount_window', 'price', 'comment', 'date', 'file' ]


class OrderCreateSerializer(serializers.ModelSerializer):
    files = serializers.ListField(child=serializers.FileField())

    class Meta:
        model = Order
        fields = ['shape', 'implement', 'address', 'type_pay', 'type_delivery', 'amount_window', 'price', 'comment', 'files']


class QuantitySerializer(serializers.ModelSerializer):
    order = OrderSerializer()
    class Meta:
        model = Quantity
        fields = '__all__'


class OrdersSerializer(serializers.ModelSerializer):
    shape = serializers.SlugRelatedField(slug_field='data', read_only = True)
    implement = serializers.SlugRelatedField(slug_field='data', read_only = True)
    quantity_set = QuantitySerializer(many=True)


    def update(self, instance, validated_data):
        instance.isactive = validated_data.get('isactive', instance.isactive)
        instance.save()
        return instance


    class Meta:
        model = Order
        fields = ['user', 'shape', 'implement', 'address', 'type_pay', 'type_delivery', 'amount_window', 'price', 'comment', 'date', 'file' ,'isactive', 'quantity_set']


class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = '__all__'

class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Review
        fields = '__all__'