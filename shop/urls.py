from django.urls import path
from rest_framework.routers import DefaultRouter

from shop.views import UserRegisterView, ShopView, PartnerState

app_name = 'shops'


urlpatterns = [
    path('user/register/', UserRegisterView.as_view(), name="user-register"),
    path('shop/', ShopView.as_view(), name="shop"),
    path('partner/state', PartnerState.as_view(), name='partner-state'),
]
