# views.py
from django.shortcuts import render, redirect,get_object_or_404
from .models import Items, ItemCategory ,InventoryAdjustment,Vendor,PurchaseOrder,PurchaseReceive,PurchaseReceiveItem
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Sum
from django.db.models import Count
from collections import defaultdict
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from .models import CustomUser
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
import requests
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives


FLASK_API_URL = "https://shau12.pythonanywhere.com/"

def logout_view(request):
    logout(request)
    return redirect('login')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        role = request.POST.get('role')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            return redirect('signup')

        if CustomUser.objects.filter(username=username).exists():
            return redirect('signup')

        try:
            user = CustomUser.objects.create_user(username=username, email=email, password=password, role=role)
            user.save()

            # Send HTML email
            subject = "New User Signup"
            from_email = settings.EMAIL_HOST_USER
            to_email = [email]  # your email

            context = {
                'username': username,
                'email': email,
                'role': role
            }

            html_content = render_to_string("signup_template.html", context)
            text_content = f"Username: {username}\nEmail: {email}\nRole: {role}"  # fallback plain text

            msg = EmailMultiAlternatives(subject, text_content, from_email, to_email)
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            return redirect('login')

        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
            return redirect('signup')

    return render(request, 'signup.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            
            return redirect('home')  # Redirect to the home page after login
         
        else:
            return redirect('login')

    return render(request, 'login.html')

def home(request):
    user_role = getattr(request.user, 'role', None) 
    return render(request,'home.html',{'user_role': user_role})  # Pass the user role to the template
def base(request):
    return render(request, 'base.html')  # Adjust the template name as needed
def  aboutus(request):
    return render(request,'aboutus.html')
def  contactus(request):
    return render(request,'contactus.html')
def terms(request):
    return render(request,'terms.html')
def faq(request):
    return render(request,'faq.html')
def items_view(request):
    items = Items.objects.all()  # Fetch all items from the database
    user_role = getattr(request.user, 'role', None)  # Safely get the role
    low_stock_items = items.filter(quantity__lt=22)  # Get items with quantity less than 22

    # Add a message if there are low stock items
    if low_stock_items.exists():
        messages.warning(request, 'Some items are low in stock! Please check the inventory.')
    return render(request, 'items.html', {'items': items, 'low_stock_items': low_stock_items,'user_role': user_role})  # Render the items template
def items_add_view(request):
    if request.method == 'POST':
        # Retrieve form data
        item_name = request.POST.get('item_name')
        item_remarks = request.POST.get('item_remarks')
        item_category_id = int(request.POST.get('item_category') ) # Get the ID directly
        
        # Debugging line to check the category ID
        print(f"Item Category ID: {item_category_id}")  # This will print the ID to the console

        item_colour = request.POST.get('item_colour')
        item_size = request.POST.get('item_size')
        purchase_rate = request.POST.get('purchase_rate')
        sales_rate = request.POST.get('sales_rate')
        quantity = request.POST.get('quantity')
        reference_number = request.POST.get('reference_number')

        # Convert item_category_id to an integer
        item_category_id = int(item_category_id)

        # Fetch the ItemCategory instance using the ID
        item_category = get_object_or_404(ItemCategory, id=item_category_id)

        # Create a new item instance and save it to the database
        new_item = Items(
            item_name=item_name,
            item_remarks=item_remarks,
            item_category=item_category,  # Assign the ItemCategory instance
            item_colour=item_colour,
            item_size=item_size,
            purchase_rate=purchase_rate,
            sales_rate=sales_rate,
            quantity=quantity,
            reference_number=reference_number
        )
        new_item.save()  # Save the new item to the database
        return redirect('items')  # Redirect to the items page after saving

    # If GET request, render the add item form
    categories = ItemCategory.objects.all()  # Fetch all categories for the dropdown
    return render(request, 'items_add.html', {'categories': categories})  # Render the add item template

def items_edit_view(request, item_id):
    item = get_object_or_404(Items, id=item_id)
    if request.method == 'POST':
        # Handle form submission and update the item
        # ...
        return redirect('items')  # Redirect to the items list or another page
    return render(request,'items_edit.html', {'item': item})  # Render the edit form

def items_delete_view(request, item_id):
    item = get_object_or_404(Items, id=item_id)
    if request.method == 'POST':
        item.delete()  # Delete the item
        return redirect('items')  # Redirect to the items list or another page
    return render(request, 'items_delete_confirm.html', {'item': item})  # Render confirmation page

# def group_items_view(request):
#     group_items = ItemCategory.objects.all()  # Fetch all item categories    5873468576745637845634876538637465
#     return render(request, 'groups_item.html', {'group_items': group_items})


def group_items(request):
    user_role = getattr(request.user, 'role', None) 
    categories = ItemCategory.objects.all()  # Fetch all categories
    return render(request, 'groups_item.html', {'group_items': categories  ,  'user_role': user_role})  # Pass categories to the template
def generate_reference_number(self):
    # Get the highest existing reference number
    existing_numbers = ItemCategory.objects.values_list('reference_number', flat=True)
    if existing_numbers:
        # Extract the numeric part and find the maximum
        max_number = max(int(num.split('-')[1]) for num in existing_numbers if num.startswith('REF-'))
        new_number = max_number + 1
    else:
        new_number = 1  # Start from 1 if no categories exist
    
    return f"REF-{new_number:03d}"  # Format as REF-001, REF-002, etc.

def edit_category(request, category_id):
    category = get_object_or_404(ItemCategory, id=category_id)

    if request.method == 'POST':
        category.category_name = request.POST['category_name']
        category.category_remarks = request.POST.get('category_remarks', '')
        category.unit = request.POST.get('category_units', '')
        category.save()
        return redirect('group_items')

    return render(request, 'group_item_edit.html', {'category': category})

def inventory_adjustments(request):
    user_role = getattr(request.user, 'role', None)
    adjustments = InventoryAdjustment.objects.all()  # Fetch all adjustments
    
    if request.method == 'POST':
        # Handle form submission to create a new adjustment
        date = request.POST.get('date')
        account = request.POST.get('account')
        reason = request.POST.get('reason')
        description = request.POST.get('description')
        item_name = request.POST.get('item_name')
        quantity_available = request.POST.get('quantity_available')
        new_quantity_on_hand = request.POST.get('new_quantity_on_hand')
        quantity_adjusted = request.POST.get('quantity_adjusted')
        reference_number = request.POST.get('reference_number')

        # Create a new InventoryAdjustment instance
        adjustment = InventoryAdjustment(
            date=date,
            account=account,
            reason=reason,
            description=description,
            item_name=item_name,
            quantity_available=quantity_available,
            new_quantity_on_hand=new_quantity_on_hand,
            quantity_adjusted=quantity_adjusted,
            reference_number=reference_number
        )
        adjustment.save()  # Save the new adjustment to the database
      
        return redirect('inventory_adjustments')  # Redirect to the same page to avoid resubmission

    return render(request, 'inventory_adjustments.html', {'adjustments': adjustments,'user_role': user_role })
        

def inventory_adjustments(request):
    user_role = getattr(request.user, 'role', None)
    response = requests.get(f"{FLASK_API_URL}/inventory_adjustments")
  # Fetch all adjustments
    
    
    adjustments = response.json()
    
    return render(request, 'inventory_adjustments.html', {'adjustments': adjustments,'user_role': user_role })
        

    # return render(request, 'inventory_adjustments.html', {'adjustments': adjustments})
def inventory_adjustment_add(request):
    if request.method == 'POST':
        date = request.POST.get('date')
        account = request.POST.get('account')
        reason = request.POST.get('reason')
        description = request.POST.get('description')
        item_name = request.POST.get('item_name')
        quantity_available = request.POST.get('quantity_available')
        new_quantity_on_hand = request.POST.get('new_quantity_on_hand')
        quantity_adjusted = request.POST.get('quantity_adjusted')
        reference_number = request.POST.get('reference_number')  # If you have this field
        
        data={
            'date': date,
            'reason': reason,
            'description': description,
            'item_name': item_name,
            'quantity_available': quantity_available,
            'new_quantity_on_hand': new_quantity_on_hand,
            'quantity_adjusted': quantity_adjusted,
            'account': account,
            'reference_number': reference_number
        }
        response = requests.post(f"{FLASK_API_URL}/inventory_adjustments", json=data)

        if response.status_code == 200:
            messages.success(request, "Product added successfully!")
            return redirect('inventory_adjustments')  # Redirect to the inventory adjustments page
        else:
            messages.error(request, "Failed to add product.")
            return redirect('inventory_adjustments')  # Redirect to the inventory adjustments page
        
    return render(request, 'inventory_adjustment_add.html')  # Render the form template



def edit_inventory_adjustment(request, adjustment_id):
    # adjustment = get_object_or_404(InventoryAdjustment, id=adjustment_id)
    response = requests.get(f"{FLASK_API_URL}/inventory_adjustments/{adjustment_id}")  # Fetch the specific adjustment
  # Fetch all adjustments
    
    if response.status_code == 200:
        adjustment = response.json()
    else:
        messages.error(request, "Failed to fetch products.")
        adjustment = []
    if request.method == 'POST':
        # Update the adjustment with the new data from the form
        date = request.POST.get('date')
        reason = request.POST.get('reason')
        description = request.POST.get('description')
        item_name = request.POST.get('item_name')
        quantity_available = request.POST.get('quantity_available')
        new_quantity_on_hand = request.POST.get('new_quantity_on_hand')
        quantity_adjusted = request.POST.get('quantity_adjusted')
        account = request.POST.get('account')
        reference_number = request.POST.get('reference_number')

        data = {
            'date': date,
            'reason': reason,
            'description': description,
            'item_name': item_name,
            'quantity_available': quantity_available,
            'new_quantity_on_hand': new_quantity_on_hand,
            'quantity_adjusted': quantity_adjusted,
            'account': account,
            'reference_number': reference_number
        }
        # Send the updated data to the Flask API
        requests.put(f"{FLASK_API_URL}/inventory_adjustments/{adjustment_id}", json=data)      
        return redirect('inventory_adjustments')  # Redirect to the inventory adjustments list

    return render(request, 'edit_inventory_adjustment.html', {'adjustment': adjustment})  # Render the edit form


def delete_inventory_adjustment(request, adjustment_id):
    response = requests.get(f"{FLASK_API_URL}/inventory_adjustments/")  # Fetch the specific adjustment
  # Fetch all adjustments
    
    if response.status_code == 200:
        adjustment = response.json()
    else:
        messages.error(request, "Failed to fetch products.")
        adjustment = []
    if request.method == 'POST':
          # Delete the adjustment
        requests.delete(f"{FLASK_API_URL}/inventory_adjustments/{adjustment_id}")
        return redirect('inventory_adjustments')  # Redirect to the inventory adjustments list
    return render(request, 'inventory_adjustments.html', {'adjustments': adjustment})  # Render the list again

def items_edit_view(request, item_id):
    item = get_object_or_404(Items, id=item_id)
    
    if request.method == 'POST':
        # Update the item with the new data from the form
        item.item_name = request.POST.get('item_name', item.item_name)
        item.item_remarks = request.POST.get('item_remarks', item.item_remarks)
        item.item_category = request.POST.get('item_category', item.item_category_id)  # Update category
        item.item_colour = request.POST.get('item_colour', item.item_colour)
        item.item_size = request.POST.get('item_size', item.item_size)
        item.purchase_rate = request.POST.get('purchase_rate', item.purchase_rate)
        item.sales_rate = request.POST.get('sales_rate', item.sales_rate)
        item.quantity = request.POST.get('quantity', item.quantity)
        item.reference_number = request.POST.get('reference_number', item.reference_number)

        item.save()  # Save the updated item
     
        return redirect('items')  # Redirect to the items list

    # If GET request, render the edit form with the current item data
    categories = ItemCategory.objects.all()  # Fetch all categories for the dropdown
    return render(request, 'items_edit.html', {'item': item, 'categories': categories})

#     # return render(request, 'inventory_adjustments.html', {'adjustments': adjustments})
# def inventory_adjustment_add(request):
#     if request.method == 'POST':
#         date = request.POST.get('date')
#         account = request.POST.get('account')
#         reason = request.POST.get('reason')
#         description = request.POST.get('description')
#         item_name = request.POST.get('item_name')
#         quantity_available = request.POST.get('quantity_available')
#         new_quantity_on_hand = request.POST.get('new_quantity_on_hand')
#         quantity_adjusted = request.POST.get('quantity_adjusted')
#         reference_number = request.POST.get('reference_number')  # If you have this field
#         adjustment = InventoryAdjustment(
#             date=date,
#             account=account,
#             reason=reason,
#             description=description,
#             item_name=item_name,
#             quantity_available=quantity_available,
#             new_quantity_on_hand=new_quantity_on_hand,
#             quantity_adjusted=quantity_adjusted,
#             reference_number=reference_number  # Save the reference number if applicable
#         )
#         adjustment.save()  # Save the new adjustment to the database
      
#         return redirect('inventory_adjustments')  # Redirect to the inventory adjustments page

#     return render(request, 'inventory_adjustment_add.html')  # Render the form template


# def items_edit_view(request, item_id):
#     item = get_object_or_404(Items, id=item_id)
    
#     if request.method == 'POST':
#         # Update the item with the new data from the form
#         item.item_name = request.POST.get('item_name', item.item_name)
#         item.item_remarks = request.POST.get('item_remarks', item.item_remarks)
#         item.item_category_id = request.POST.get('item_category', item.item_category_id)  # Update category
#         item.item_colour = request.POST.get('item_colour', item.item_colour)
#         item.item_size = request.POST.get('item_size', item.item_size)
#         item.purchase_rate = request.POST.get('purchase_rate', item.purchase_rate)
#         item.sales_rate = request.POST.get('sales_rate', item.sales_rate)
#         item.quantity = request.POST.get('quantity', item.quantity)
#         item.reference_number = request.POST.get('reference_number', item.reference_number)

#         item.save()  # Save the updated item
     
#         return redirect('items')  # Redirect to the items list

#     # If GET request, render the edit form with the current item data
#     categories = ItemCategory.objects.all()  # Fetch all categories for the dropdown
#     return render(request, 'items_edit.html', {'item': item, 'categories': categories})


def group_item_add(request):
    if request.method == 'POST':
        category = ItemCategory(
            category_name=request.POST['category_name'],
            category_remarks=request.POST.get('category_remarks', ''),
            unit=request.POST.get('category_units', '')
        )
        
        try:
            category.save()  # This will generate a unique reference number automatically
            messages.success(request, 'Category added successfully.')
            return redirect('group_items')  # Redirect to the group items view after saving
        except Exception:
            messages.error(request, 'Error: Category with this reference number already exists.')
            return render(request, 'group_item_add.html', {'category': category})

    return render(request, 'group_item_add.html')  



def vendors_view(request):
    user_role = getattr(request.user, 'role', None)
    vendors = Vendor.objects.all()  # Fetch all vendors from the database
    return render(request, 'vendors.html', {'vendors': vendors,'user_role': user_role })

def add_vendor_view(request):
    # Logic for adding a new vendor
    return render(request,'add_vendor.html')
def list_vendors(request):
    vendors = Vendor.objects.all()  # Fetch all vendors
    return render(request, 'vendors.html', {'vendors': vendors})

def add_vendor(request):
    if request.method == 'POST':
        salutation = request.POST.get('salutation')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        company_name = request.POST.get('company_name')
        vendor_display_name = request.POST.get('vendor_display_name')
        vendor_email = request.POST.get('vendor_email')
        work_phone = request.POST.get('work_phone')
        mobile = request.POST.get('mobile')

        # Create and save the new Vendor instance
        vendor = Vendor(
            salutation=salutation,
            first_name=first_name,
            last_name=last_name,
            company_name=company_name,
            vendor_display_name=vendor_display_name,
            vendor_email=vendor_email,
            work_phone=work_phone,
            mobile=mobile
        )
        vendor.save()
      
        return redirect('vendors')  # Redirect to the vendor list page

    return render(request, 'add_vendor.html')  # Render the form if GET request

def delete_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    if request.method == 'POST':
        vendor.delete()  # Delete the vendor
       
        return redirect('vendors')  # Redirect to the vendors list
    return render(request, 'vendors.html', {'vendors': Vendor.objects.all()})  # Render the vendors list again




def edit_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    
    if request.method == 'POST':
        # Update the vendor with the new data from the form
        vendor.salutation = request.POST.get('salutation', vendor.salutation)
        vendor.first_name = request.POST.get('first_name', vendor.first_name)
        vendor.last_name = request.POST.get('last_name', vendor.last_name)
        vendor.company_name = request.POST.get('company_name', vendor.company_name)
        vendor.vendor_display_name = request.POST.get('vendor_display_name', vendor.vendor_display_name)
        vendor.vendor_email = request.POST.get('vendor_email', vendor.vendor_email)
        vendor.work_phone = request.POST.get('work_phone', vendor.work_phone)
        vendor.mobile = request.POST.get('mobile', vendor.mobile)

        vendor.save()  # Save the updated vendor

        return redirect('vendors')  # Redirect to the vendors list

    return render(request, 'edit_vendor.html', {'vendor': vendor})  # Render the edit form

# def edit_inventory_adjustment(request, adjustment_id):
#     adjustment = get_object_or_404(InventoryAdjustment, id=adjustment_id)
    
#     if request.method == 'POST':
#         # Update the adjustment with the new data from the form
#         adjustment.date = request.POST.get('date', adjustment.date)
#         adjustment.reason = request.POST.get('reason', adjustment.reason)
#         adjustment.description = request.POST.get('description', adjustment.description)
#         adjustment.item_name = request.POST.get('item_name', adjustment.item_name)
#         adjustment.quantity_available = request.POST.get('quantity_available', adjustment.quantity_available)
#         adjustment.new_quantity_on_hand = request.POST.get('new_quantity_on_hand', adjustment.new_quantity_on_hand)
#         adjustment.quantity_adjusted = request.POST.get('quantity_adjusted', adjustment.quantity_adjusted)
#         adjustment.account = request.POST.get('account', adjustment.account)
#         adjustment.reference_number = request.POST.get('reference_number', adjustment.reference_number)

#         adjustment.save()  # Save the updated adjustment
      
#         return redirect('inventory_adjustments')  # Redirect to the inventory adjustments list

#     return render(request, 'edit_inventory_adjustment.html', {'adjustment': adjustment})  # Render the edit form


# def delete_inventory_adjustment(request, adjustment_id):
#     adjustment = get_object_or_404(InventoryAdjustment, id=adjustment_id)
#     if request.method == 'POST':
#         adjustment.delete()  # Delete the adjustment
        
#         return redirect('inventory_adjustments')  # Redirect to the inventory adjustments list
#     return render(request, 'inventory_adjustments.html', {'adjustments': InventoryAdjustment.objects.all()})  # Render the list again




def delete_category(request, category_id):
    category = get_object_or_404(ItemCategory, id=category_id)
    if request.method == 'POST':
        category.delete()  
        
        return redirect('group_items') 
    return redirect('group_items')  

def purchase_orders_view(request):
    user_role = getattr(request.user, 'role', None)
    purchase_orders = PurchaseOrder.objects.all()  # Fetch all purchase orders
    vendors = Vendor.objects.all()  # Fetch all vendors for the dropdown
    return render(request, 'purchaseorders.html', {'purchase_orders': purchase_orders, 'vendors': vendors,'user_role': user_role })


def add_purchase_order_view(request):
    vendors = Vendor.objects.all()  # Fetch all vendors
    if request.method == 'POST':
        vendor_id = request.POST['vendor_id']  # Get the vendor ID from the form
        vendor = get_object_or_404(Vendor, id=vendor_id)  # Fetch the Vendor instance

        new_order = PurchaseOrder(
            vendor=vendor,  # Use the correct field name here
            reference_no=request.POST['reference_no'],
            amount=request.POST['amount'],
            status=request.POST['status']
        )
        
        try:
            new_order.save()  # This will generate a unique purchase order number automatically
      
            return redirect('purchase_orders')  # Redirect to the purchase orders view after saving
        except Exception:
            return render(request, 'addpurchaseorder.html', {'vendors': vendors})

    return render(request, 'addpurchaseorder.html', {'vendors': vendors})

def delete_purchase_order(request, order_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)
    order.delete()
    
    return redirect('purchase_orders')  # Redirect to the purchase orders page



from django.shortcuts import render, redirect, get_object_or_404
from .models import PurchaseOrder, Vendor
from django.contrib import messages

def edit_purchase_order_view(request, order_id):
    order = get_object_or_404(PurchaseOrder, id=order_id)
    vendors = Vendor.objects.all()  # Fetch all vendors for the dropdown

    if request.method == 'POST':
        order.purchase_order_no = request.POST.get('purchase_order_no')
        order.vendor_id = request.POST.get('vendor_id')
        order.reference_no = request.POST.get('reference_no')
        order.amount = request.POST.get('amount')
        order.status = request.POST.get('status')
        order.save()  # Save the updated order

        messages.success(request, 'Purchase Order updated successfully!')
        return redirect('purchase_orders')  # Redirect to the purchase orders page

    return render(request, 'edit_purchase_order.html', {'order': order, 'vendors': vendors})






from django.shortcuts import render, redirect, get_object_or_404
from .models import Customer
from .forms import CustomerForm
from .models import SalesOrder
from .forms import SalesOrderForm

def customer_list(request):
    user_role = getattr(request.user, 'role', None)
    customers = Customer.objects.all()
    return render(request, 'customer_list.html', {'customers': customers,'user_role': user_role })

def add_customer(request):
    if request.method == 'POST':
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm()
    return render(request, 'add_customer.html', {'form': form})

def edit_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
    else:
        form = CustomerForm(instance=customer)
    return render(request, 'edit_customer.html', {'form': form})

def delete_customer(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == 'POST':
        customer.delete()
        return redirect('customer_list')
    return render(request, 'delete_customer.html', {'customer': customer})


def sales_order(request):
    user_role = getattr(request.user, 'role', None)
    orders = SalesOrder.objects.all()
    total_orders = orders.count()
    return render(request, 'sales_order.html', {'orders': orders, 'total_orders': total_orders,'user_role': user_role })

def new_order(request):
    if request.method == 'POST':
        form = SalesOrderForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('sales_order')  # Redirect to the sales order list after saving
    else:
        form = SalesOrderForm()
    return render(request, 'new_order.html', {'form': form})

def edit_order(request, pk):
    order = get_object_or_404(SalesOrder, pk=pk)
    if request.method == 'POST':
        form = SalesOrderForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            return redirect('sales_order')  # Redirect to the sales order list after saving
    else:
        form = SalesOrderForm(instance=order)
    return render(request, 'edit_order.html', {'form': form, 'order': order})

def delete_order(request, pk):
    order = get_object_or_404(SalesOrder, pk=pk)
    if request.method == 'POST':
        order.delete()
        return redirect('sales_order')  # Redirect to the sales order list after deletion
    return render(request, 'delete_order.html', {'order': order})

def packages_view(request):
    not_shipped_orders = SalesOrder.objects.filter(shipment_status='not_shipped')
    shipped_orders = SalesOrder.objects.filter(shipment_status='in_transit')
    delivered_orders = SalesOrder.objects.filter(shipment_status='delivered')

    context = {
        'not_shipped_orders': not_shipped_orders,
        'shipped_orders': shipped_orders,
        'delivered_orders': delivered_orders,
        'not_shipped_count': not_shipped_orders.count(),
        'shipped_count': shipped_orders.count(),
        'delivered_count': delivered_orders.count(),
    }
    return render(request, 'packages.html', context)

def purchasehogyi_view(request):
    Pending= PurchaseOrder.objects.filter(status='pending')
    Approved = PurchaseOrder.objects.filter(status='approved')
    Received = PurchaseOrder.objects.filter(status='received')
    Paid = PurchaseOrder.objects.filter(status='paid')
   

    context = {
        'Pending': Pending,
        'Approved': Approved,
        'Received': Received,
        'Paid':Paid,
        'Pending_count': Pending.count(),
        'Approved_count': Approved.count(),
        'Received_count': Received.count(),
        'Paid_count':Paid.count(),
        
    }
    return render(request, 'purchasereceives.html', context)

def dashboard_view(request):
    user_role = getattr(request.user, 'role', None)
    # Sales Activity
    sales_orders = SalesOrder.objects.all()
    
    total_sales_amount = SalesOrder.objects.aggregate(Sum('total_amount'))['total_amount__sum'] or 0

    # Count total sales orders, excluding drafts
    total_sales_orders = sales_orders.exclude(order_status='Draft').count() 

    # Count specific statuses  
    total_to_ship = sales_orders.filter(shipment_status='not_shipped').count()
    total_to_deliver = sales_orders.filter(shipment_status='in_transit').count()

    # Inventory Summary
    total_inventory = Items.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
    
    # Product Details
    low_stock_items = Items.objects.filter(quantity__lt=22).count()
    all_item_groups = ItemCategory.objects.count()
    all_items = Items.objects.count()

    # Purchase Order Summary
    total_purchase_orders = PurchaseOrder.objects.aggregate(Sum('amount'))['amount__sum'] or 0
    quantity_ordered = PurchaseReceiveItem.objects.aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    total_quantity_received = PurchaseReceiveItem.objects.aggregate(Sum('quantity'))['quantity__sum'] or 0
    purchase_order_count = PurchaseOrder.objects.count()
    # Sales Summary
    sales_summary = sales_orders.values('order_status').annotate(count=Count('id'))
    
  
    items = TopSellingItem.objects.all()
    # Render Template
    context = {
        'total_to_ship': total_to_ship,
        'total_to_deliver': total_to_deliver,
        'total_inventory': total_inventory,
        'low_stock_items': low_stock_items,
        'all_item_groups': all_item_groups,
        'all_items': all_items,
        'total_purchase_orders': total_purchase_orders,
        'purchase_order_count': purchase_order_count,
        'quantity_ordered': quantity_ordered,
        'sales_summary': sales_summary,
        'customer_count': Customer.objects.count(),
        'total_sales_orders': total_sales_orders,
        'total_sales_amount': total_sales_amount,
        'items': items,
        'user_role': user_role,  
    }
    
    
    return render(request, 'dashboard.html',context)

# views.py
from django.shortcuts import render, redirect, get_object_or_404
from .models import TopSellingItem
from .forms import TopSellingItemForm

def top_selling_list(request):
    items = TopSellingItem.objects.all()
    return render(request, 'dashboard.html', {'items': items})

def top_selling_create(request):
    if request.method == 'POST':
        form = TopSellingItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TopSellingItemForm()
    return render(request, 'top_selling_form.html', {'form': form})

def top_selling_edit(request, pk):
    item = get_object_or_404(TopSellingItem, pk=pk)
    if request.method == 'POST':
        form = TopSellingItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = TopSellingItemForm(instance=item)
    return render(request, 'top_selling_form.html', {'form': form})

def top_selling_delete(request, pk):
    item = get_object_or_404(TopSellingItem, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('dashboard')
    return render(request, 'top_selling_confirm_delete.html', {'item': item})




# import openai
# from django.shortcuts import render
# from .forms import ChatForm


# openai.api_key = 'YOUR_OPENAI_API_KEY'

# def chatbot_view(request):
#     response = ""
#     if request.method == 'POST':
#         form = ChatForm(request.POST)
#         if form.is_valid():
#             user_message = form.cleaned_data['message']

            
#             chat_completion = openai.ChatCompletion.create(
#                 model="gpt-3.5-turbo",
#                 messages=[
#                     {"role": "user", "content": user_message}
#                 ]
#             )
#             response = chat_completion.choices[0].message['content']
#     else:
#         form = ChatForm()

#     return render(request, 'chat.html', {'form': form, 'response': response})

