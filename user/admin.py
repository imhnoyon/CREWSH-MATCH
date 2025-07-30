from django.contrib import admin

from .models import User, Otp, Profile, Image


admin.site.register(User)
admin.site.register(Otp)
admin.site.register(Profile)
admin.site.register(Image)
