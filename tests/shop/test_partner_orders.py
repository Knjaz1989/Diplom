import pytest
from django.test import Client
from django.urls import reverse

client = Client()
partner_orders_url = reverse("shops:partner-orders")


@pytest.mark.django_db
class TestPartnerOrders:

    data = [
        (pytest.lazy_fixture("supplier_token"), 200),
        (pytest.lazy_fixture("buyer_token"), 403),
    ]

    @pytest.mark.parametrize("token, status_code", data)
    def test_ger_orders(self, token, status_code):
        header = f"Token {token}"
        response = client.get(partner_orders_url,
                              HTTP_AUTHORIZATION=header)

        assert response.status_code == status_code
