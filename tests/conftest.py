import pytest
from django.test import Client
from django.urls import reverse
from rest_framework.authtoken.models import Token
from shop.models import User, Shop

client = Client()
partner_update_url = reverse("shops:partner-update")


@pytest.fixture
def supplier():
    shop = User.objects.create(
        email="shop@mail.ru", password="Shop_password",
        first_name="Dmitriy", type="shop", is_active=True
    )
    return shop


@pytest.fixture
def supplier_token(supplier):
    token = Token.objects.get_or_create(user=supplier)[0]
    return token.key


@pytest.fixture
def shop(supplier):
    shop = Shop.objects.create(user_id=supplier.id, name="Связной")
    return shop


@pytest.fixture
def upload_shop_products(supplier_token):
    header = f"Token {supplier_token}"
    with open("shop1.yaml", "rb") as file:
        response = client.post(partner_update_url,
                               HTTP_AUTHORIZATION=header,
                               data={"file": file})


@pytest.fixture
def other_supplier():
    user = User.objects.create(
        email="other_shop@mail.ru", password="Other_shop_password",
        first_name="Dmitriy", type="shop", is_active=True
    )
    return user


@pytest.fixture
def other_supplier_token(other_supplier):
    token = Token.objects.get_or_create(user=other_supplier)[0]
    return token.key


@pytest.fixture
def other_supplier_shop(other_supplier):
    shop = Shop.objects.create(user_id=other_supplier.id, name="Евросеть")
    return shop


@pytest.fixture
def buyer():
    buyer = User.objects.create(
        email="buyer_user@mail.ru", password="Buyer_password",
        first_name="Vasiliy", type="buyer", is_active=True
    )
    return buyer


@pytest.fixture
def buyer_token(buyer):
    token = Token.objects.get_or_create(user=buyer)[0]
    return token.key


@pytest.fixture
def other_buyer():
    buyer = User.objects.create(
        email="other_buyer_user@mail.ru", password="Other_buyer_password",
        first_name="Evgeniy", type="buyer", is_active=True
    )
    return buyer


@pytest.fixture
def other_buyer_token(other_buyer):
    token = Token.objects.get_or_create(user=other_buyer)[0]
    return token.key
