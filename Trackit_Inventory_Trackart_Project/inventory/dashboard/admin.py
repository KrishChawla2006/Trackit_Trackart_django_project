from django.contrib import admin

from .models import  SalesOrder, Package, InventoryAdjustment, Vendor, PurchaseOrder, Items, ItemCategory, PurchaseReceive
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser
# Register your models here
admin.site.register(CustomUser, UserAdmin)
# admin.site.register(User)
# admin.site.register(Student)
admin.site.register(SalesOrder)
admin.site.register(Package)
admin.site.register(InventoryAdjustment)
admin.site.register(Vendor)
admin.site.register(PurchaseOrder)
admin.site.register(Items)
admin.site.register(ItemCategory)
admin.site.register(PurchaseReceive)
