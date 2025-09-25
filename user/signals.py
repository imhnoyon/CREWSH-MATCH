from django.conf import settings
from django.dispatch import receiver
from django.core.mail import send_mail
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model

from .utils import generate_otp

from .models import AccountVerificationOtp, Profile

User = get_user_model()


@receiver(post_save, sender=User)
def send_otp(instance, created, *args, **kwargs):
    if created:
        if not instance.is_superuser:
            otp, _ = AccountVerificationOtp.objects.update_or_create(
                user=instance,
                defaults={
                    'code': generate_otp(),
                }
            )
            send_mail(
                subject="Account Verification OTP for Crew Match",
                message=f"Your account verification opt is {otp.code}. Please enter this otp to verify your account",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[instance.email_address],
                fail_silently=True
            )
