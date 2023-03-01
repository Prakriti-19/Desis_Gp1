from django.contrib import admin
from .models import donor,ngo,chat,donations,location


admin.site.register(donations)
admin.site.register(ngo)
admin.site.register(donor)
admin.site.register(location)
admin.site.register(chat)
admin.site.site_header = "Inventory"