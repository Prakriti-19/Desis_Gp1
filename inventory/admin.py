from django.contrib import admin
from .models import donor,ngo,location,stats,chat,inventory


@admin.register(donor)
class ProductAdmin(admin.ModelAdmin):
    pass


admin.site.register(inventory)
admin.site.register(ngo)
admin.site.register(location)
admin.site.register(stats)
admin.site.register(chat)
admin.site.site_header = "Inventory"