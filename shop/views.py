from rest_framework.generics import CreateAPIView

from shop.models import User
from shop.serializers import UserSerializer


class UserRegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
