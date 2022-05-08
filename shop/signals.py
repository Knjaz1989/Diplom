from django.dispatch import receiver
from django_rest_passwordreset.signals import reset_password_token_created
from shop.tasks import send_password_reset_token


@receiver(reset_password_token_created)
def password_reset_token_created(instance, reset_password_token, **kwargs):
    user = reset_password_token.user.email
    key = reset_password_token.key
    email = reset_password_token.user.email
    send_password_reset_token.delay(user=user, key=key, email=email)
