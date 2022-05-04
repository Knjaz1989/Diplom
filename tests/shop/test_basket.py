import pytest
from django.test import Client
from django.urls import reverse

client = Client()
basket_url = reverse("shops:basket")


@pytest.mark.django_db
class TestBasket:

    data = [
        (pytest.lazy_fixture("supplier_token"), 403),
        (pytest.lazy_fixture("buyer_token"), 200),
    ]

    @pytest.mark.parametrize("token, status_code", data)
    def test_put_to_basket(self, token, status_code, upload_shop_products):
        header = f"Token {token}"
        response = client.post(basket_url,
                               HTTP_AUTHORIZATION=header,
                               data={"items": [
                                   {
                                       "product_info": 1,
                                       "quantity": 3
                                   },
                                   {
                                       "product_info": 2,
                                       "quantity": 1
                                   }
                               ]})
        assert response.status_code == status_code

    @pytest.mark.parametrize("token, status_code", data)
    def test_get_basket(self, token, status_code, upload_shop_products):
        header = f"Token {token}"
        response = client.post(basket_url,
                               HTTP_AUTHORIZATION=header)

        assert response.status_code == status_code
