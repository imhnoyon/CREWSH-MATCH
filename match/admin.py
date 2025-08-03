from django.contrib import admin

from .models import Request, Match


admin.site.register(Request)
admin.site.register(Match)

