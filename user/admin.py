from django.contrib import admin

from .models import User, Otp, Profile, Image, Friend


admin.site.register(User)
admin.site.register(Otp)
admin.site.register(Profile)
admin.site.register(Image)
admin.site.register(Friend)
