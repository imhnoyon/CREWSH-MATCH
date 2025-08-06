from django.contrib import admin

from .models import Plan, Subscription, PrivateMode


admin.site.register(Plan)
admin.site.register(Subscription)
admin.site.register(PrivateMode)

