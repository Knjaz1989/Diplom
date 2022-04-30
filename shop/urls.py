from django.urls import path
from rest_framework.routers import DefaultRouter

from shop.views import UserRegisterView, ShopView, PartnerState, LoginAccount, \
    ConfirmAccount, PartnerUpdate, ContactView, CategoryView, ProductInfoView, \
    BasketView, OrderView

app_name = 'shops'

router = DefaultRouter()
router.register('user/contact', ContactView, basename='user-contact')

urlpatterns = [
    path('user/register/', UserRegisterView.as_view(), name="user-register"),
    path('user/register/confirm/', ConfirmAccount.as_view(),
         name='user-register-confirm'),
    path('user/login/', LoginAccount.as_view(), name='user-login'),
    path('partner/state/', PartnerState.as_view(), name='partner-state'),
    path('partner/update/', PartnerUpdate.as_view(), name='partner-update'),
    path('shops/', ShopView.as_view(), name="shop"),
    path('categories/', CategoryView.as_view(), name='categories'),
    path('products/', ProductInfoView.as_view(), name='shops'),
    path('basket/', BasketView.as_view(), name='basket'),
    path('orders/', OrderView.as_view(), name='order'),
]

urlpatterns += router.urls
