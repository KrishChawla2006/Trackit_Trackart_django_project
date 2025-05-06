
from django.db import models
from dashboard.models import CustomUser

from django.conf import settings
# Create your models here.
class Products(models.Model):
    id = models.AutoField(primary_key=True)
    category=models.CharField(max_length = 100)
    sub_category=models.CharField(max_length=100)
    image_link=models.URLField()
    description=models.TextField()
    offer_price=models.IntegerField()
    original_price=models.IntegerField()
    discount=models.IntegerField()
    quantity=models.IntegerField(default=1)
    chooser=models.ManyToManyField(CustomUser)

    def to_dict(self):
        return {
            'id': self.id,
            'category': self.category,
            'sub_category': self.sub_category,
            'image_link': self.image_link,
            'description': self.description,
            'offer_price': self.offer_price,
            'original_price': self.original_price,
            'discount': self.discount,
            'quantity': self.quantity,
        }
    

class Purchase(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey('Products', on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    price = models.FloatField()
    # description = models.TextField()
    # image_link = models.URLField()
    purchase_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} bought {self.product.name}"


class Wishlist(models.Model):
    id = models.AutoField(primary_key=True)
    category=models.CharField(max_length = 100)
    sub_category=models.CharField(max_length=100)
    image_link=models.URLField()
    description=models.TextField()
    offer_price=models.IntegerField()
    original_price=models.IntegerField()
    discount=models.IntegerField()
    quantity=models.IntegerField(default=1)
    chooser=models.ManyToManyField(CustomUser)



    def __str__(self):
        return self.category

