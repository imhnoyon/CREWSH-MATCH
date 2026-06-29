from django.contrib import admin

from .models import Plan, Subscription, PrivateMode


# admin.site.register(Plan)
admin.site.register(Subscription)
admin.site.register(PrivateMode)

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'ship', 'name', 'price_id', 'amount', 'duration', 'description')
    list_filter = ('ship',)
    search_fields = ('name', 'description')
