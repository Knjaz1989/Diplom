import pytest
from django.test import Client
from django.urls import reverse

client = Client()
partner_update_url = reverse("shops:partner-update")


@pytest.mark.django_db
class TestPartnerUpdate:

    data = [
        (pytest.lazy_fixture("supplier_token"), 200),
        (pytest.lazy_fixture("other_supplier_token"), 400),
        (pytest.lazy_fixture("buyer_token"), 403),
    ]

    @pytest.mark.parametrize("token, status_code", data)
    def test_upload_data(self, token, status_code, other_supplier_shop):
        header = f"Token {token}"
        with open("../../shop1.yaml", "rb") as file:
            response = client.post(partner_update_url,
                                   HTTP_AUTHORIZATION=header,
                                   data={"file": file})

        assert response.status_code == status_code
