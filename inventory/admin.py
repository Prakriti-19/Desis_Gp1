from django.contrib import admin
from .models import *


admin.site.register(donations)
admin.site.register(ngo)
admin.site.register(Transaction)
admin.site.register(donor)
admin.site.register(pincode)
admin.site.site_header = "Inventory"