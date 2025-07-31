from django.contrib import admin

from .models import (
    Inbox,
    Message,
    BlockedInbox,
    DeletedConversation
)


class MessageAdmin(admin.ModelAdmin):
    list_display = ["__str__", "sender", "receiver", "message_type", "extension", ]


admin.site.register(Inbox)
admin.site.register(Message, MessageAdmin)
admin.site.register(BlockedInbox)
admin.site.register(DeletedConversation)

