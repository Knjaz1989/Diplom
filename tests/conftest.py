import pytest
from rest_framework.authtoken.models import Token
from shop.models import User, Shop


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
