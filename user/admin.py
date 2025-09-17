from django.contrib import admin

from .models import User, AccountVerificationOtp, Profile, Image, PasswordResetOtp


class ImageAdmin(admin.ModelAdmin):
    list_display = ["__str__", "image", "user"]


class ImageTabular(admin.StackedInline):
    model = Image


class UserAdmin(admin.ModelAdmin):
    inlines = [ImageTabular, ]
    list_display = ["__str__", "is_subscribed", "is_private", ]


admin.site.register(User, UserAdmin)
admin.site.register(AccountVerificationOtp)
admin.site.register(Profile)
admin.site.register(Image, ImageAdmin)
admin.site.register(PasswordResetOtp)


