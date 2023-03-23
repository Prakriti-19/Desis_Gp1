from django.contrib import admin
from .models import donor,ngo,donations,pincode, BaseTransaction, NGODonation_t


admin.site.register(donations)
admin.site.register(BaseTransaction)
admin.site.register(NGODonation_t)
admin.site.register(ngo)
admin.site.register(donor)
admin.site.register(pincode)
admin.site.site_header = "Inventory"