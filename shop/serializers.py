from django.contrib.auth.hashers import make_password
from rest_framework.serializers import ModelSerializer

from shop.models import User


class UserSerializer(ModelSerializer):

    class Meta:
        model = User
        fields = ["username", "password", "first_name", "last_name", "email", "type"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        user = User.objects.create(**validated_data)

        return user