from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from shop.models import User, Shop, Category, Contact, Product, Order, \
    ProductParameter, ProductInfo, OrderItem
from shop.signals import user_register


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["password", "first_name", "last_name", "email", "type"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        user = User.objects.create(**validated_data)
        user_register.send(sender=self.__class__, user_id=user.id) # Вызываем сигнал

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


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ('id', 'product_info', 'quantity',)
        read_only_fields = ('id',)


class BasketItemsSerializer(serializers.Serializer):
    items = serializers.ListField(child=OrderItemSerializer(), allow_empty=False)


class DeleteBasketItemsSerializator(serializers.Serializer):
    items = serializers.ListField(child=serializers.IntegerField(), allow_empty=False)


class OrderItemCreateSerializer(OrderItemSerializer):
    product_info = ProductInfoSerializer(read_only=True)


class OrderSerializer(serializers.ModelSerializer):
    ordered_items = OrderItemCreateSerializer(read_only=True, many=True)

    total_sum = serializers.IntegerField()
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'ordered_items', 'state', 'dt', 'total_sum', 'contact',)
        read_only_fields = ('id',)
        # extra_kwargs = {"password": {"write_only": True}}


class OrderCreateSerializer(serializers.Serializer):
    order_id = serializers.IntegerField()
    contact_id = serializers.IntegerField()
