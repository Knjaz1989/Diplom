from django.contrib.auth.hashers import make_password
from rest_framework.serializers import ModelSerializer

from shop.models import User, Shop, Category


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "password", "first_name", "last_name", "email", "type"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        user = User.objects.create(**validated_data)

        return user


class ShopSerializer(ModelSerializer):
    class Meta:
        model = Shop
        fields = ('id', 'name', 'state',)
        # read_only_fields = ('id',)


class CategorySerializer(ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name',)
        # read_only_fields = ('id',)
