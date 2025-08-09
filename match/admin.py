from django.contrib import admin

from .models import Request, Match, Notification, Unliked


admin.site.register(Request)
admin.site.register(Match)
admin.site.register(Notification)
admin.site.register(Unliked)


