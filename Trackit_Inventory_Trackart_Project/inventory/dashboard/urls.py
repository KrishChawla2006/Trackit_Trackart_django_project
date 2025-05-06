from django.urls import path
from . import views
from dashboard.views import items_view,items_add_view,items_edit_view, items_delete_view,group_item_add,inventory_adjustments,inventory_adjustment_add,group_items,delete_inventory_adjustment,edit_inventory_adjustment,delete_category,purchase_orders_view,add_purchase_order_view,delete_purchase_order,edit_purchase_order_view,purchasehogyi_view,customer_list,add_customer,edit_customer,delete_customer,packages_view,delete_order,edit_order,new_order,sales_order,edit_category
urlpatterns = [
    path('base/', views.base,name='base'),
    path('',views.home,name='home'),
    path('aboutus/',views.aboutus,name='aboutus'),
    path('contactus/',views.contactus,name='contactus'),
    path('faq/', views.faq, name='faq'),
    path('terms/',views.terms,name='terms'),
    path('items/', items_view, name='items'),  
    path('items/add/', items_add_view, name='items_add'),
    path('items/edit/<int:item_id>/', items_edit_view, name='items_edit'),  # Define the URL pattern
    path('items/delete/<int:item_id>/', items_delete_view, name='items_delete'),  # Define the URL pattern
    path('group-items/', group_items, name='group_items'),
    path('group-item/add/', group_item_add, name='group_item_add'),
    path('group-item/edit/<int:category_id>/', edit_category, name='group_item_edit'),
    path('group-item/delete/<int:category_id>/', delete_category, name='group_item_delete'),  # URL for deleting a category
    path('inventory-adjustments/', inventory_adjustments, name='inventory_adjustments'),  # Existing view
    path('inventory-adjustment/add/', inventory_adjustment_add, name='inventory_adjustment_add'),  # New view for adding adjustments
    path('inventory-adjustment/edit/<int:adjustment_id>/', edit_inventory_adjustment, name='edit_inventory_adjustment'),  # Edit view
    path('inventory-adjustment/delete/<int:adjustment_id>/', delete_inventory_adjustment, name='delete_inventory_adjustment'),  # Delete view
    path('vendors/', views.vendors_view, name='vendors'),
    path('vendors/add/', views.add_vendor, name='add_vendor'),
    path('vendors/delete/<int:vendor_id>/', views.delete_vendor, name='delete_vendor'),  # Add this line
    path('vendors/edit/<int:vendor_id>/', views.edit_vendor, name='edit_vendor'),  # Add this line
    path('purchase-orders/', purchase_orders_view, name='purchase_orders'),  # Add this line
    path('purchase-orders/add/', add_purchase_order_view, name='add_purchase_order'),  # Add this line
    path('purchase-orders/delete/<int:order_id>/', delete_purchase_order, name='delete_purchase_order'),  # Add this line
    path('purchase-orders/edit/<int:order_id>/', edit_purchase_order_view, name='edit_purchase_order'),  # Add this line
    path('customer_list', customer_list, name='customer_list'),
    path('add/', add_customer, name='add_customer'),
    path('edit/<int:pk>/', edit_customer, name='edit_customer'),
    path('delete/<int:pk>/', delete_customer, name='delete_customer'),
    path('sales/', sales_order, name='sales_order'),
    path('sales/new/', new_order, name='new_order'),
    path('sales/edit/<int:pk>/', edit_order, name='edit_order'),
    path('sales/delete/<int:pk>/', delete_order, name='delete_order'),
    path('packages/', packages_view, name='packages'),
    path('purchasehogyi/',purchasehogyi_view,name='purchasehogyi'),
    path('top-selling/add/', views.top_selling_create, name='top_selling_create'),
    path('top-selling/<int:pk>/edit/', views.top_selling_edit, name='top_selling_edit'),
    path('top-selling/<int:pk>/delete/', views.top_selling_delete, name='top_selling_delete'),
    path('dashboard/', views.dashboard_view, name='dashboard'),



    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # path('logout/', views.logout_view, name='logout')

    # path('chat/', views.chatbot_view, name='chat'),
     ]