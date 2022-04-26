from django.conf import settings
from django.core.mail import EmailMultiAlternatives, send_mail
from django.db.models.signals import post_save
from django.dispatch import receiver

from shop.models import User, ConfirmEmailToken


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def new_user_registered_signal(sender, instance, created, **kwargs):
    """
    отправляем письмо с подтрердждением почты
    """
    # send an e-mail to the user
    token, _ = ConfirmEmailToken.objects.get_or_create(user_id=instance.id)

    msg = EmailMultiAlternatives(
        # title:
        f"Password Reset Token for {token.user.email}",
        # message:
        token.key,
        # from:
        settings.EMAIL_HOST_USER,
        # to:
        [token.user.email]
    )
    msg.send()
    # send_mail("Confirm token", f"Password Reset Token for {token.user.email}", 'admin@admin.ru', [token.user.email], fail_silently=False)