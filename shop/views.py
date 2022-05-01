from distutils.util import strtobool
from django.db.models import Q, Sum, F
from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.generics import CreateAPIView, ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from yaml import load as load_yaml, Loader
from rest_framework.viewsets import ModelViewSet
from shop.models import User, Shop, Category, ConfirmEmailToken, ProductInfo, \
    Product, Parameter, ProductParameter, Contact, Order, OrderItem
from shop.permissions import IsBuyer, IsShop
from shop.serializers import UserSerializer, ShopSerializer, \
    CategorySerializer, ConfirmAccountSerializer, LoginAccountSerializer, \
    PartnerUpdateSerializer, ContactSerializer, ProductInfoSerializer, \
    OrderSerializer, BasketItemsSerializer, DeleteBasketItemsSerializator, \
    OrderCreateSerializer
from shop.signals import new_order_signal


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
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            token = ConfirmEmailToken.objects.filter(
                user__email=request.data['email'],
                key=request.data['token']
            ).first()
            if token:
                token.user.is_active = True
                token.user.save()
                token.delete()
                return Response({'Status': True})
            return Response({'Errors': 'Неправильно указан токен или email'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors)


class LoginAccount(CreateAPIView):
    """
    Класс для авторизации пользователей
    """
    serializer_class = LoginAccountSerializer

    # Авторизация методом POST
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = authenticate(request,
                                username=request.data['email'],
                                password=request.data['password'])
            if user:
                if user.is_active:
                    token, _ = Token.objects.get_or_create(user=user)
                    return Response({'Token': token.key})
                return Response({'Errors': "Пользователь не подтвержден"},
                                status=status.HTTP_400_BAD_REQUEST)
            return Response({'Errors': 'Неверный логин или пароль'},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors)


class PartnerState(APIView):
    """
    Класс для работы со статусом поставщика
    """
    serializer_class = ShopSerializer
    permission_classes  = [IsAuthenticated, IsShop]
    authentication_classes = [TokenAuthentication]

    # получить текущий статус
    def get(self, request, *args, **kwargs):
        shop = request.user.shop
        serializer = ShopSerializer(shop)
        return Response(serializer.data)

    # изменить текущий статус
    def post(self, request, *args, **kwargs):
        state = request.data.get('state')
        if state and len(request.data) == 1:
            try:
                Shop.objects.filter(
                    user_id=request.user.id
                ).update(state=strtobool(state))
                return Response({'Status': f"Changed on {state}"})
            except ValueError as error:
                return Response({'Status': False, 'Errors': str(error)},
                                status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {'Status': False,
             'Errors': 'Не указаны все необходимые аргументы или переданы '
                       'лишние'},
            status=status.HTTP_400_BAD_REQUEST)


class PartnerUpdate(APIView):
    """
    Класс для обновления прайса от поставщика
    """
    serializer_class = PartnerUpdateSerializer
    permission_classes  = [IsAuthenticated, IsShop]
    authentication_classes = [TokenAuthentication]

    def post(self, request, *args, **kwargs):
        file = request.data.get('file')
        if file:

            try:
                shop_name = request.user.shop.name
            except:
                shop_name = None

            data = load_yaml(file, Loader=Loader)
            if data['shop'] == shop_name or not shop_name:
                shop, _ = Shop.objects.get_or_create(
                    name=data['shop'], user_id=request.user.id
                )
                for category in data['categories']:
                    category_object, _ = Category.objects.get_or_create(
                        id=category['id'], name=category['name']
                    )
                    category_object.shops.add(shop.id)
                    category_object.save()
                ProductInfo.objects.filter(shop_id=shop.id).delete()

                for item in data['goods']:
                    product, _ = Product.objects.get_or_create(
                        name=item['name'], category_id=item['category']
                    )
                    product_info = ProductInfo.objects.create(
                        product_id=product.id,
                        external_id=item['id'],
                        model=item['model'],
                        price=item['price'],
                        price_rrc=item['price_rrc'],
                        quantity=item['quantity'],
                        shop_id=shop.id)

                    for name, value in item['parameters'].items():
                        parameter_object, _ = Parameter.objects.get_or_create(
                            name=name
                        )
                        ProductParameter.objects.create(
                            product_info_id=product_info.id,
                            parameter_id=parameter_object.id,
                            value=value
                        )

                return Response({'Status': "Success"})
            return Response({"Errors": "У вас уже есть другой магазин"},
                            status=status.HTTP_400_BAD_REQUEST)
        return Response({'Errors': 'Не указаны все необходимые аргументы'},
                        status=status.HTTP_400_BAD_REQUEST)


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


class ContactView(ModelViewSet):
    """
    Класс для работы с контактами покупателей
    """
    serializer_class = ContactSerializer
    permission_classes = [IsAuthenticated, IsBuyer]
    authentication_classes = [TokenAuthentication]

    # получить мои контакты
    def get_queryset(self):
        user_contacts = Contact.objects.filter(
            user_id=self.request.user.id)
        return user_contacts

    # добавить новый контакт. не больше 5
    def create(self, request, *args, **kwargs):
        user_contacts = Contact.objects.filter(
            user_id=self.request.user.id)
        if len(user_contacts) == 5:
            return Response({"Status": "У вас уже есть 5 контактов. "
                                       "Удалите или измените любой из них"},
                            status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data,
                        status=status.HTTP_201_CREATED, headers=headers)


class ProductInfoView(APIView):
    """
    Класс для поиска товаров
    """
    def get(self, request, *args, **kwargs):

        query = Q(shop__state=True)
        shop_id = request.query_params.get('shop_id')
        category_id = request.query_params.get('category_id')

        if shop_id:
            query = query & Q(shop_id=shop_id)

        if category_id:
            query = query & Q(product__category_id=category_id)

        # фильтруем и отбрасываем дуликаты
        queryset = ProductInfo.objects.filter(
            query).select_related(
            'shop', 'product__category').prefetch_related(
            'product_parameters__parameter').distinct()

        serializer = ProductInfoSerializer(queryset, many=True)

        return Response(serializer.data)


class BasketView(APIView):
    """
    Класс для работы с корзиной пользователя
    """
    permission_classes = [IsAuthenticated, IsBuyer]
    authentication_classes = [TokenAuthentication]
    # получить корзину
    def get(self, request, *args, **kwargs):
        basket = Order.objects.filter(
            user_id=request.user.id, state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter'
        ).annotate(total_sum=Sum(
            F('ordered_items__quantity') *
            F('ordered_items__product_info__price')
        )).distinct()

        serializer = OrderSerializer(basket, many=True)
        return Response(serializer.data)

    # добавить товары в корзину
    def post(self, request, *args, **kwargs):
        serializer = BasketItemsSerializer(data=request.data)
        if serializer.is_valid():
            basket, _ = Order.objects.get_or_create(user_id=request.user.id,
                                                    state='basket')
            objects_created = 0
            for order_item in request.data["items"]:
                order_item.update({'order': basket.id})
                OrderItem.objects.create(
                    product_info_id=int(order_item['product_info']),
                    order_id=order_item['order'],
                    quantity=int(order_item['quantity'])
                )
            return Response({'Message': 'Товары добавлены в корзину'})
        return Response(serializer.errors)

    # удалить товары из корзины
    def delete(self, request, *args, **kwargs):
        serializer = DeleteBasketItemsSerializator(data=request.data)
        if serializer.is_valid():
            basket, _ = Order.objects.get_or_create(user_id=request.user.id,
                                                    state='basket')
            query = Q()
            objects_deleted = False
            for order_item_id in request.data["items"]:
                query = query | Q(order_id=basket.id, id=int(order_item_id))
                objects_deleted = True

            if objects_deleted:
                deleted_count = OrderItem.objects.filter(query).delete()[0]
                return Response({'Status': True,
                                 'Удалено объектов': deleted_count})
        return Response(serializer.errors)

    # обновить количество товара в корзине
    def put(self, request, *args, **kwargs):
        serializer = BasketItemsSerializer(data=request.data)
        if serializer.is_valid():
            basket, _ = Order.objects.get_or_create(user_id=request.user.id,
                                                    state='basket')
            objects_updated = 0
            for order_item in request.data["items"]:
                    objects_updated += OrderItem.objects.filter(
                        order_id=basket.id, id=int(order_item['id'])
                    ).update(quantity=int(order_item['quantity']))
            return Response({'Status': True,
                             'Обновлено объектов': objects_updated})
        return Response(serializer.errors)


class OrderView(APIView):
    """
    Класс для получения и размещения заказов пользователями
    """
    permission_classes = [IsAuthenticated, IsBuyer]
    authentication_classes = [TokenAuthentication]
    # получить мои оформленные заказы
    def get(self, request, *args, **kwargs):
        order = Order.objects.filter(
            user_id=request.user.id).exclude(state='basket').prefetch_related(
            'ordered_items__product_info__product__category',
            'ordered_items__product_info__product_parameters__parameter'
        ).select_related('contact').annotate(
            total_sum=Sum(
                F('ordered_items__quantity') *
                F('ordered_items__product_info__price')
            )).distinct()

        serializer = OrderSerializer(order, many=True)
        return Response(serializer.data)

    # разместить заказ из корзины
    def post(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        if serializer.is_valid():
            order = Order.objects.filter(user_id=request.user.id,
                                         id=int(request.data['order_id'])
                                         ).first()
            contact = Contact.objects.filter(user_id=request.user.id,
                                             id=int(request.data['contact_id'])
                                             ).first()
            if order and contact:
                order.contact_id = int(request.data['contact_id'])
                order.state = 'new'
                order.save()
                new_order_signal(request.user.email, order.id)
                return Response(
                    {'Message': f"Заказ с номером {order.id} "
                                f"был успешно сформирован"}
                )
            return Response(
                {'Status': False,
                 'Errors': 'Данный заказ или контакт вам не принадлежат'},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors)
