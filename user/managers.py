from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password


class UserManager(BaseUserManager):
    use_in_migrations = True
    
    def _create_user(self, full_name, email_address, password, **extra_fields):
        if not full_name:
            raise ValueError("Name must be set")
        if not full_name:
            raise ValueError("Email must be set")
        
        email = self.normalize_email(email_address)
        user = self.model(full_name=full_name, email_address=email_address, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, full_name, email_address, password, **extra_fields):
        user = self._create_user(
            full_name=full_name, email_address=email_address, password=password,
            is_staff=True, is_active=True, is_superuser=True,
            **extra_fields
        )
        return user

