import pytest
from django.test import Client
import requests
from django.urls import reverse
from pytest_lazyfixture import lazy_fixture
# from rest_framework.authtoken.models import Token
from shop.models import ConfirmEmailToken, User

register_url = reverse("shops:user-register")
register_confirm_url = reverse("shops:user-register-confirm")
client = Client()


def get_register_confirm_data(email):
    user = ''
    confirm_token = ConfirmEmailToken.objects.filter(user_id='')
    return {"email": email, "token": confirm_token}


@pytest.mark.django_db(transaction=True)
class TestAPI:
    user_create_data = [
        ({"email": "knjaz1989@y.ru", "password": "abc"}, 201, "buyer"),
        ({"email": "ccc@c.com", "password": "abc", "username": "Dmitriy",
          "type": "shop"}, 201, "shop"),
        ({}, 400, None)
    ]

    @pytest.mark.parametrize("params, expected, type", user_create_data)
    def test_user_register(self, params, expected, type):
        response = client.post(register_url, data=params)

        assert response.status_code == expected
        assert response.json().get("type") == type
