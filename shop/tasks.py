from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from shop.models import ConfirmEmailToken
from orders.celery import app


@app.task
def new_user_register(user_id):
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


@app.task
def send_password_reset_token(user, key, email):
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
        f"Password Reset Token for {user}",
        # message:
        key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [email]
    )
    msg.send()


@app.task
def new_order(email, order_id):
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
