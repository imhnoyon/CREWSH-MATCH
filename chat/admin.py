from django.contrib import admin

from .models import (
    Inbox,
    Message
)


class MessageAdmin(admin.ModelAdmin):
    list_display = ["__str__", "sender", "receiver", ]


admin.site.register(Inbox)
admin.site.register(Message, MessageAdmin)


