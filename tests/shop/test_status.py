import pytest
from django.test import Client

@pytest.mark.django_db
class TestShopStatus:

    get_data = [
        (pytest.lazy_fixture("shop"), 200),
        (pytest.lazy_fixture("other_shop"), 403),
        (pytest.lazy_fixture("buyer"), 403)
    ]

    @pytest.mark.parametrize("user, status_code", get_data)
    def test_get_shop_status(self, user, status_code):
        params = {"name": "Связной"}
        response = Client().get("shop/", data=params)

        assert response.status_code == status_code