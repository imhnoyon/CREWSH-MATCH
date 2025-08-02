from django.contrib import admin

from .models import User, AccountVerificationOtp, Profile, Image, Friend, PasswordResetOtp


admin.site.register(User)
admin.site.register(AccountVerificationOtp)
admin.site.register(Profile)
admin.site.register(Image)
admin.site.register(Friend)
admin.site.register(PasswordResetOtp)


