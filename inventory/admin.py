from django.contrib import admin
from .models import donor,ngo,stats,chat,invent


# @admin.register(donor)
# class ProductAdmin(admin.ModelAdmin):
#     pass

from .models import Image

admin.site.register(Image)
admin.site.register(invent)
admin.site.register(ngo)
admin.site.register(donor)
admin.site.register(stats)
admin.site.register(chat)
admin.site.site_header = "Inventory"