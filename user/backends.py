from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


User = get_user_model()


class EmailAuthenticationBackend(ModelBackend):
    def authenticate(self, request, username, password, **kwargs):
        try:
            user = User.objects.get(email_address=username)
            if user.check_password(password):
                return user
            else:
                return None
            
        except User.DoesNotExist:
            return None
     
    def get_user(self, user_id):
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None
