import pytest
from django.test import Client
import requests


# @pytest.mark.django_db
class TestAPI:
    user_create_data = [
        ({"email": "knjaz1989@yandex.ru", "password": "abc", "type": "buyer"}, 201, "buyer"),
        # ({"email": "b@b.com", "password": "abc", "username": "Petya"}, 201, "buyer"),
        # ({"email": "c@c.com", "password": "abc", "username": "Dmitriy", "type": "shop"}, 201, "shop"),
        ({}, 400, None)
    ]

    @pytest.mark.parametrize("params, expected, type", user_create_data)
    def test_user_register(self, params, expected, type):
        response = requests.post("http://localhost:8000/api/v1/user/register", data=params)

        assert response.status_code == expected
        assert response.json().get("type") == type
