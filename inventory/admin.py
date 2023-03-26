from django.contrib import admin
from .models import *

admin.site.register(Donations)
admin.site.register(Transaction)
admin.site.register(Transaction_code)
admin.site.register(Ngo)
admin.site.register(Donor)
admin.site.register(Pincode)
admin.site.site_header = "Inventory"