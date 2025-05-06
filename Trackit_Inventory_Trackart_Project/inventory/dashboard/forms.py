from django import forms
from .models import Items, Customer, SalesOrder


class ItemForm(forms.ModelForm):
    class Meta:
        model = Items
        fields = [
            'item_name',
            'item_remarks',
            'item_category',
            'item_colour',
            'item_size',
            'purchase_rate',
            'sales_rate',
            'quantity',
            'reference_number',
        ]


class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = [
            'name',
            'company_name',
            'email',
            'work_phone',
            'receivables',
            'unused_credits',
            'address',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Full Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'example@email.com'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }


class SalesOrderForm(forms.ModelForm):
    order_date = forms.DateField(
        widget=forms.SelectDateWidget,
        required=True,
        label='Date of Order'
    )

    class Meta:
        model = SalesOrder
        fields = [
            'customer',
            'sales_order_no',
            'reference_no',
            'order_status',
            'shipment_status',
            'total_amount',
            'amount_received',
            'order_date',
        ]
        widgets = {
            'order_status': forms.Select(choices=SalesOrder.ORDER_STATUS_CHOICES),
            'shipment_status': forms.Select(choices=SalesOrder.SHIPMENT_STATUS_CHOICES),
        }




from .models import TopSellingItem
class TopSellingItemForm(forms.ModelForm):
    class Meta:
        model=TopSellingItem
        fields=['name','quantity_sold','image_url']



