from distutils.util import strtobool

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate
from django.http import JsonResponse
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from yaml import load as load_yaml, Loader
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError
from requests import get
from rest_framework.viewsets import ModelViewSet

from shop.models import User, Shop, Category, ConfirmEmailToken, ProductInfo, Product, Parameter, ProductParameter
from shop.serializers import UserSerializer, ShopSerializer, CategorySerializer, \
    ConfirmAccountSerializer, LoginAccountSerializer, PartnerUpdateSerializer


class UserRegisterView(CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ConfirmAccount(CreateAPIView):
    """
    Класс для подтверждения почтового адреса
    """
    serializer_class = ConfirmAccountSerializer
    # Регистрация методом POST
    def post(self, request, *args, **kwargs):

        # проверяем обязательные аргументы
        if {'email', 'token'}.issubset(request.data):

            token = ConfirmEmailToken.objects.filter(user__email=request.data['email'],
                                                     key=request.data['token']).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return Response({'Status': True})
            else:
                return Response({'Status': False, 'Errors': 'Неправильно указан токен или email'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}, status=status.HTTP_400_BAD_REQUEST)


class LoginAccount(CreateAPIView):
    """
    Класс для авторизации пользователей
    """
    serializer_class = LoginAccountSerializer
    # Авторизация методом POST
    def post(self, request, *args, **kwargs):

        if {'email', 'password'}.issubset(request.data):
            user = authenticate(request, username=request.data['email'], password=request.data['password'])

            if user:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)

                    return Response({'Status': True, 'Token': token.key})

            return Response({'Status': False, 'Errors': 'Не удалось авторизовать'}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}, status=status.HTTP_400_BAD_REQUEST)


class PartnerState(APIView):
    """
    Класс для работы со статусом поставщика
    """
    serializer_class = ShopSerializer
    permission_classes  = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]
    # получить текущий статус
    def get(self, request, *args, **kwargs):

        if request.user.type != 'shop':
            return Response({'Status': False, 'Error': 'Только для магазинов'}, status=status.HTTP_403_FORBIDDEN)

        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    # изменить текущий статус
    def post(self, request, *args, **kwargs):

        if request.user.type != 'shop':
            return JsonResponse({'Status': False, 'Error': 'Только для магазинов'}, status=status.HTTP_403_FORBIDDEN)
        state = request.data.get('state')
        if state and len(request.data) == 1:
            try:
                Shop.objects.filter(user_id=request.user.id).update(state=strtobool(state))
                return Response({'Status': f"Changed on {state}"})
            except ValueError as error:
                return Response({'Status': False, 'Errors': str(error)}, status=status.HTTP_400_BAD_REQUEST)

        return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы или переданы лишние'}, status=status.HTTP_400_BAD_REQUEST)


class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от поставщика
    """
    serializer_class = PartnerUpdateSerializer
    permission_classes  = [IsAuthenticated]
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        if request.user.type != 'shop':
            return Response({'Status': False, 'Error': 'Только для магазинов'}, status=403)

        file = request.data.get('file')
        if file:

            try:
                shop_name = request.user.shop.name
            except:
                shop_name = None

            data = load_yaml(file, Loader=Loader)
            if data['shop'] == shop_name or not shop_name:
                shop, _ = Shop.objects.get_or_create(name=data['shop'], user_id=request.user.id)
                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
                    category_object.shops.add(shop.id)
                    category_object.save()
                ProductInfo.objects.filter(shop_id=shop.id).delete()
                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

                    product_info = ProductInfo.objects.create(product_id=product.id,
                                                              external_id=item['id'],
                                                              model=item['model'],
                                                              price=item['price'],
                                                              price_rrc=item['price_rrc'],
                                                              quantity=item['quantity'],
                                                              shop_id=shop.id)
                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(name=name)
                        ProductParameter.objects.create(product_info_id=product_info.id,
                                                        parameter_id=parameter_object.id,
                                                        value=value)

                return Response({'Status': "Success"})
            return Response({"Status": False, "Errors": "У вас уже есть другой магазин"}, status=status.HTTP_400_BAD_REQUEST)
        return Response({'Status': False, 'Errors': 'Не указаны все необходимые аргументы'}, status=status.HTTP_400_BAD_REQUEST)



class ShopView(ListAPIView):
    """
    Класс для просмотра списка магазинов
    """
    queryset = Shop.objects.filter(state=True)
    serializer_class = ShopSerializer


class CategoryView(ListAPIView):
    """
    Класс для просмотра категорий
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
