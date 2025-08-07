from django.contrib import admin

from .models import Announcement, Company, Ship, Settings


admin.site.register(Announcement)
admin.site.register(Company)
admin.site.register(Ship)
admin.site.register(Settings)




