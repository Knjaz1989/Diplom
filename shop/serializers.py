from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from shop.models import User, Shop, Category, ConfirmEmailToken, Contact, Product, ProductParameter, ProductInfo
from rest_framework.exceptions import ValidationError, bad_request


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["password", "first_name", "last_name", "email", "type"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        user = User.objects.create(**validated_data)

        return user


class ConfirmAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    token = serializers.CharField(max_length=150)


class LoginAccountSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(max_length=150)


class PartnerUpdateSerializer(serializers.Serializer):
    # url = serializers.URLField()
    file = serializers.FileField()


class ShopSerializer(serializers.ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'state')
        read_only_fields = ('id',)


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)
        read_only_fields = ('id',)


class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        exclude = ['user']
        read_only_fields = ('id',)

    def create(self, validated_data):
        validated_data["user"] = self.context["request"].user
        return Contact.objects.create(**validated_data)


class ProductSerializer(serializers.ModelSerializer):
    category = serializers.StringRelatedField()

    class Meta:
        model = Product
        fields = ('name', 'category',)


class ProductParameterSerializer(serializers.ModelSerializer):
    parameter = serializers.StringRelatedField()

    class Meta:
        model = ProductParameter
        fields = ('parameter', 'value',)


class ProductInfoSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_parameters = ProductParameterSerializer(read_only=True, many=True)

    class Meta:
        model = ProductInfo
        fields = ('id', 'model', 'product', 'shop', 'quantity', 'price', 'price_rrc', 'product_parameters',)
        read_only_fields = ('id',)
