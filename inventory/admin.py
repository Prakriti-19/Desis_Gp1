from django.contrib import admin
from .models import donor,ngo,donations,pincode,Redemption


admin.site.register(donations)
admin.site.register(Redemption)
admin.site.register(ngo)
admin.site.register(donor)
admin.site.register(pincode)
admin.site.site_header = "Inventory"