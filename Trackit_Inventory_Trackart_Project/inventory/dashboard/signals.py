# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Purchasehogyi,PurchaseOrder

# @receiver(post_save, sender=Purchasehogyi)
# def update_purchase_order_status(sender, instance, **kwargs):
#     try:
#         purchase_order = PurchaseOrder.objects.get(purchase_order_no=instance.purchase_order_no)
#         purchase_order.status = instance.status
#         purchase_order.save()
#     except PurchaseOrder.DoesNotExist:
#         pass  # Optional: log warning or raise exception if needed
# yourapp/signals.py

