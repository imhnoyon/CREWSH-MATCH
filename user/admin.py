from django.contrib import admin

from .models import User, AccountVerificationOtp, Profile, Image, PasswordResetOtp


class ImageAdmin(admin.ModelAdmin):
    list_display = ["__str__", "image", "user"]

admin.site.register(User)
admin.site.register(AccountVerificationOtp)
admin.site.register(Profile)
admin.site.register(Image, ImageAdmin)
admin.site.register(PasswordResetOtp)


