from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created
from shop.models import ConfirmEmailToken

user_register = Signal()

new_order = Signal()


@receiver(user_register)
def new_user_registered_signal(user_id, **kwargs):
    """
    отправляем письмо с подтрердждением почты
    """
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=user_id)

    msg = EmailMultiAlternatives(
        # title:
        f"Confirm Token for {token.user.email}",
        # message:
        token.key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [token.user.email]
    )
    msg.send()


@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    """
    Отправляем письмо с токеном для сброса пароля
    When a token is created, an e-mail needs to be sent to the user
    :param sender: View Class that sent the signal
    :param instance: View Instance that sent the signal
    :param reset_password_token: Token Model Object
    :param kwargs:
    :return:
    """
    msg = EmailMultiAlternatives(
        # title:
        f"Password Reset Token for {reset_password_token.user}",
        # message:
        reset_password_token.key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [reset_password_token.user.email]
    )
    msg.send()


@receiver(new_order)
def new_order_signal(email, order_id, **kwargs):
    """
    отправяем письмо при cоздании заказа
    """
    msg = EmailMultiAlternatives(
        # title:
        f"Информация о заказе",
        # message:
        f'Заказ с номером {order_id} сформирован',
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [email]
    )
    msg.send()
