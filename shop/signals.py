from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver
from shop.models import User, ConfirmEmailToken


@receiver(post_save, sender=User)
def new_user_registered_signal(sender, instance, created, **kwargs):
    """
    отправляем письмо с подтрердждением почты
    """
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=instance.id)

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


def new_order_signal(email, order_id):
    """
    отправяем письмо при cоздании заказа
    """
    msg = EmailMultiAlternatives(
        # title:
        f"Информация о заказе",
        # message:
        f'Заказ {order_id} сформирован',
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [email]
    )
    msg.send()
