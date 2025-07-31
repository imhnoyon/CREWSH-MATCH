from django.contrib import admin

from .models import (
    Text,
    Photo,
    File
)


admin.site.register(Text)
admin.site.register(Photo)
admin.site.register(File)

