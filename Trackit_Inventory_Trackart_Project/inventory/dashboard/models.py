from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('manager', 'Manager'),
        ('staff', 'Staff'),
        ('user', 'User'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='user')

# User Model
# class User(models.Model):
#     email = models.EmailField(unique=True)
#     company_name = models.CharField(max_length=100)
#     role = models.CharField(max_length=100, default="user")
#     first_name = models.CharField(max_length=30, blank=True)
#     last_name = models.CharField(max_length=30, blank=True)
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)

#     def __str__(self):
#         return self.email

# # Student Model
# class Student(models.Model):
#     roll_no = models.AutoField(primary_key=True)
#     name = models.CharField(max_length=100)
#     company_name = models.CharField(max_length=100)
#     email = models.EmailField(max_length=100)
#     work_phone = models.IntegerField()
#     receivables = models.IntegerField()
#     unused_credits = models.IntegerField()

# SalesOrder Model

# class SalesOrder(models.Model):
#     sales_order_no = models.CharField(max_length=20, unique=True)
#     customer = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='sales_orders')
#     reference_no = models.CharField(max_length=50, null=True)
#     order_status = models.CharField(max_length=20, default='Draft')
#     shipment_status = models.CharField(max_length=20, default='Not Shipped')
#     total_amount = models.FloatField()
#     amount_received = models.FloatField(default=0.0)

#     @property
#     def amount_due(self):
#         return self.total_amount - self.amount_received

# Package Model
class Package(models.Model):
    customer = models.CharField(max_length=100)
    reference = models.CharField(max_length=50, unique=True)
    sales_order = models.CharField(max_length=50)
    amount = models.FloatField()
    carrier = models.CharField(max_length=100, null=True)
    shipping_date = models.CharField(max_length=20, null=True)
    status = models.CharField(max_length=20, default="Not Shipped")

# InventoryAdjustment Model
class InventoryAdjustment(models.Model):
    date = models.DateField()  # Change from CharField to DateField
    reason = models.CharField(max_length=100)
    description = models.CharField(max_length=200, null=True)
    item_name = models.CharField(max_length=100)
    quantity_available = models.IntegerField()
    new_quantity_on_hand = models.IntegerField()
    quantity_adjusted = models.IntegerField()
    account = models.CharField(max_length=50)
    reference_number = models.CharField(max_length=100, blank=True, null=True,default='default_value')
    

# Vendor Model
class Vendor(models.Model):
    salutation = models.CharField(max_length=10, null=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company_name = models.CharField(max_length=100)
    vendor_display_name = models.CharField(max_length=100, null=True)
    vendor_email = models.EmailField(max_length=100, unique=True)
    work_phone = models.CharField(max_length=20)
    mobile = models.CharField(max_length=20, null=True)

class PurchaseOrder(models.Model):
    purchase_order_no = models.CharField(max_length=50, unique=True)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    reference_no = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20)

    def save(self, *args, **kwargs):
        if not self.purchase_order_no:  # Only set if it's not already set
            self.purchase_order_no = self.generate_purchase_order_no()
        super().save(*args, **kwargs)

    def generate_purchase_order_no(self):
        existing_numbers = PurchaseOrder.objects.values_list('purchase_order_no', flat=True)
        new_number = 1
        while f"{new_number}/" in existing_numbers:
            new_number += 1
        return f"{new_number}/"
# ItemCategory Model
from django.db import models

class ItemCategory(models.Model):
    category_name = models.CharField(max_length=100)
    category_remarks = models.TextField(blank=True)
    unit = models.CharField(max_length=50)
    reference_number = models.CharField(max_length=50, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.reference_number:  # Only set if it's not already set
            self.reference_number = self.generate_reference_number()
        super().save(*args, **kwargs)

    def generate_reference_number(self):
        existing_numbers = ItemCategory.objects.values_list('reference_number', flat=True)
        if existing_numbers:
            max_number = max(int(num.split('-')[1]) for num in existing_numbers if num.startswith('REF-'))
            new_number = max_number + 1
        else:
            new_number = 1
        return f"REF-{new_number:03d}"
class Items(models.Model):
    item_name = models.CharField(max_length=30)
    item_remarks = models.CharField(max_length=80)
    # item_category = models.IntegerField()
    item_category = models.ForeignKey(ItemCategory, on_delete=models.CASCADE)  # ForeignKey field
    item_colour = models.CharField(max_length=20)
    item_size = models.CharField(max_length=10)
    purchase_rate = models.FloatField()
    sales_rate = models.FloatField()
    quantity = models.IntegerField()
    reference_number = models.CharField(max_length=30)



# PurchaseReceive Model
class PurchaseReceive(models.Model):
    date = models.DateField()
    purchase_order = models.ForeignKey(PurchaseOrder, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    status = models.CharField(max_length=50)
    quantity = models.IntegerField()



from django.db import models

class Customer(models.Model):
    name = models.CharField(max_length=100)
    company_name = models.CharField(max_length=100)
    email = models.EmailField()
    work_phone = models.CharField(max_length=15)
    receivables = models.DecimalField(max_digits=10, decimal_places=2)
    unused_credits = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.TextField()  
    def __str__(self):
        return self.name


class SalesOrder(models.Model):
    ORDER_STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('canceled', 'Canceled'),
    ]

    SHIPMENT_STATUS_CHOICES = [
        ('not_shipped', 'Not Shipped'),
        ('in_transit', 'In Transit'),
        ('delivered', 'Delivered'),
    ]

    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    sales_order_no = models.CharField(max_length=20)
    reference_no = models.CharField(max_length=20)
    order_status = models.CharField(max_length=20, choices=ORDER_STATUS_CHOICES)
    shipment_status = models.CharField(max_length=20, choices=SHIPMENT_STATUS_CHOICES)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    amount_received = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    @property
    def amount_due(self):
        return self.total_amount - self.amount_received

    def __str__(self):
        return f"Order {self.sales_order_no} - {self.customer.name}"
    
class TopSellingItem(models.Model):
    name = models.CharField(max_length=255)
    quantity_sold = models.IntegerField()
    image_url = models.URLField(max_length=100000,blank=True,default='https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRWK9GUpJGn7l4a9yq31T085a5DtpdnBQ-KCw&s')

    def __str__(self):
        return self.name
class PurchaseReceiveItem(models.Model):
    purchase_receive = models.ForeignKey(PurchaseReceive, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Items, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    rate = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.item.item_name} - {self.quantity}"

class Purchasehogyi(models.Model):
    purchase_order_no = models.CharField(max_length=50, unique=True)
    reference_no = models.CharField(max_length=50, null=True)
    vendor = models.CharField(max_length=100)
    status = models.CharField(max_length=20, default='pending')

from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=Purchasehogyi)
def update_purchase_order_status(sender, instance, **kwargs):
    try:
        purchase_order = PurchaseOrder.objects.get(purchase_order_no=instance.purchase_order_no)
        purchase_order.status = instance.status
        purchase_order.save()
    except PurchaseOrder.DoesNotExist:
        pass

