from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.hashers import make_password


class UserManager(BaseUserManager):
    use_in_migrations = True
    
    def _create_user(self, name, email, password, **extra_fields):
        if not name:
            raise ValueError("Name must be set")
        if not email:
            raise ValueError("Email must be set")
        
        email = self.normalize_email(email)
        user = self.model(name=name, email=email, **extra_fields)
        user.password = make_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, name, email, password, **extra_fields):
        user = self._create_user(
            name=name, email=email, password=password,
            is_staff=True, is_active=True, is_superuser=True,
            **extra_fields
        )
        user.is_superuser = True
        user.is_active = True
        user.is_staff = True
        user.save()
