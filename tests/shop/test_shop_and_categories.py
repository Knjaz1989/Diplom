import pytest
from django.test import Client
from django.urls import reverse

client = Client()
shop_url = reverse("shops:shop")
category_url = reverse("shops:categories")


@pytest.mark.django_db
class TestShopsCategories:

    data = [
        (pytest.lazy_fixture("supplier_token"), 400),
        (pytest.lazy_fixture("other_supplier_token"), 201),
        (pytest.lazy_fixture("buyer_token"), 403),
    ]

    @pytest.mark.parametrize("token, status_code", data)
    def test_create_shop(self, token, status_code, shop):
        header = f"Token {token}"
        response = client.post(shop_url,
                               HTTP_AUTHORIZATION=header,
                               data={"state": False,
                                     "name": "Евросеть"})
        assert response.status_code == status_code

    def test_get_shop(self):
        response = client.get(shop_url)

        assert response.status_code == 200

    def test_category(self):
        response = client.get(category_url)

        assert response.status_code == 200
