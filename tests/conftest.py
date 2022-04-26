import pytest

from shop.models import User


@pytest.fixture
def shop():
    shop = User.objects.create(
        email="shop_user@mail.ru", password="Password-shop-user",
        first_name="Dmitriy", type="shop"
    )
    return shop


@pytest.fixture
def othet_shop():
    shop = User.objects.create(
        email="shop_user@mail.ru", password="Password-shop-user",
        first_name="Dmitriy", type="shop"
    )
    return shop


@pytest.fixture
def buyer():
    buyer = User.objects.create(
        email="buyer_user@mail.ru", password="Password-buyer-user",
        first_name="Vasiliy", type="buyer"
    )
    return buyer
