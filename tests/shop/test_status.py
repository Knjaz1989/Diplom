import pytest
from django.test import Client
from django.urls import reverse

client = Client()
partner_state_url = reverse("shops:partner-state")


@pytest.mark.django_db
class TestShopStatus:

    data = [
        (pytest.lazy_fixture("supplier_token"), 200),
        (pytest.lazy_fixture("other_supplier_token"), 400),
        (pytest.lazy_fixture("buyer_token"), 403),
    ]

    @pytest.mark.parametrize("token, status_code", data)
    def test_get_shop_status(self, token, status_code, shop):
        header = f"Token {token}"
        response = client.get(partner_state_url, HTTP_AUTHORIZATION=header)

        assert response.status_code == status_code

    @pytest.mark.parametrize("token, status_code", data)
    def test_change_shop_status(self, token, status_code, shop):
        header = f"Token {token}"
        response = client.post(partner_state_url,
                               HTTP_AUTHORIZATION=header,
                               data={"state": False})

        assert response.status_code == status_code
