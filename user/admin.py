from django.contrib import admin

from .models import User, AccountVerificationOtp, Profile, Image, PasswordResetOtp


admin.site.register(User)
admin.site.register(AccountVerificationOtp)
admin.site.register(Profile)
admin.site.register(Image)
admin.site.register(PasswordResetOtp)


