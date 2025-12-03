from django.contrib import admin

from .models import Announcement, Company, Ship, Settings


@admin.register(Ship)
class ShipAdmin(admin.ModelAdmin):
    list_display = ["__str__", ]
    list_filter = ["company", ]

admin.site.register(Announcement)
admin.site.register(Company)
admin.site.register(Settings)




