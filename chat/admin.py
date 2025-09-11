from django.contrib import admin

from .models import (
    Inbox,
    Message,
    BlockedInbox
)


class MessageAdmin(admin.ModelAdmin):
    list_display = ["__str__", "sender", "receiver", "inbox__match"]


class InboxAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'match', "blocked", ]


admin.site.register(Inbox, InboxAdmin)
admin.site.register(Message, MessageAdmin)
admin.site.register(BlockedInbox)
