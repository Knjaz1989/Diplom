from django.urls import path

from shop.views import UserRegisterView

app_name = 'shops'

urlpatterns = [
    path('user/register/', UserRegisterView.as_view(), name="user-register"),
]
