# Trackart/urls.py
from django.urls import path
from . import views
from django.contrib.auth.decorators import user_passes_test, login_required

# Only allow non-managers
not_manager = user_passes_test(lambda u: getattr(u, 'role', '').lower() != 'staff')



urlpatterns = [
    path('', views.home_view, name='trackart_home'),
    # path('wishlist/delete/<int:item_id>/', views.delete_from_wishlist, name='delete_from_wishlist'),
    # path('allitemsf/', views.allitemsf, name='itemsf'),
    # path('add-to-wishlist/<int:product_id>/', views.add_to_wishlist, name='add_to_wishlist'),
    # path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    # path('all-items/', views.all_items_view, name='all_items'),
    # path('cart/', views.cart_view, name='cart'),  # New URL for the cart
    # path('remove-from-cart/<int:item_id>/', views.remove_from_cart_view, name='remove_from_cart'),
    # path('update-cart/<int:item_id>/', views.update_cart_view, name='update_cart'),  # URL for updating item quantity in cart
    # path('checkout/', views.checkout_view, name='checkout'),
    path('products/', views.products_view,name='products'),
    path('products/detail/<int:product_id>', views.productDetail_view,name='productdetail'),
    path('cart/<int:product_id>', views.cart_view,name='product_cart'),
    path('wishlist/<int:product_id>', views.wishlist_view,name='wishlist'),
    path('products/delete/<int:product_id>', views.delete_product, name='delete'),
    path('products/edit/<int:product_id>', views.edit_product, name='edit'),
    path('wishlist/delete/<int:item_id>', views.delete_from_wishlist, name='delete_from_wishlist'),
    path('cart/checkout', views.cart_to_product_checkout,name='order_proceed'),
    path('history/', views.purchase_history, name='purchase_history'),
path('product/<int:product_id>/', views.productDetail_view, name='product_detail'),
# chatbot
path('chatbot/chat/', views.chat_view, name='chatbot_chat'),
    path('chatbot/speak/', views.speak_view, name='chatbot_speak'),
    path('wishlist/', views.wishlist_button, name='wishlist_button'),
    path('cart/', views.cart_button, name='cart_button'),
    path('cart/delete/<int:item_id>', views.delete_from_cart, name='delete_from_cart'),
    path('cart/quantity/', views.item_quantity, name='item_quantity'),
    path('wishlist/go/cart/<int:product_id>',views.wishlist_cart_btn, name='wishlist_cart_btn'),

    path('search/', views.product_search, name='product_search'),
    
    path('furniture/',views.view_furniture,name="furniture"),
    path('furniture/livingroom/',views.view_living_room,name="livingroom"),
    path('furniture/diningroom/',views.view_dining_room,name="diningroom"),
    path('furniture/bedroom/',views.view_bed_room,name="bedroom"),
    path('furniture/outdoor/',views.view_outdoor,name="outdoor"),
    path('furniture/bathroom_furniture/',views.view_bathroom_furniture,name="bathroom_furniture"),
    path('furniture/home_office_furniture/',views.view_home_office_furniture,name="home_office_furniture"),
    path('furniture/entry_way_furniture/',views.entry_way_furniture,name="entry_way_furniture"),

    path('tabletop_bar/',views.tabletop_bar,name="tabletop_bar"),
    path('tabletop_bar/dinnerware',views.dinnerware,name="dinnerware"),
    path('tabletop_bar/serveware',views.serveware,name="serveware"),
    path('tabletop_bar/drinkware',views.drinkware,name="drinkware"),
path('tabletop_bar/bar_tools_accessories',views.bar_tools_accessories,name="bar_tools_accessories"),
path('tabletop_bar/table_linnens',views.table_linnens,name="table_linnens"),

path('kitchen/',views.kitchen,name="kitchen"),
path('kitchen/kitchen_appliences_electronics',views.kitchen_appliences_electronics,name="kitchen_appliences_electronics"),
path('kitchen/coffee_espresso_tea',views.coffee_espresso_tea,name="coffee_espresso_tea"),
path('kitchen/cookware_bakeware',views.cookware_bakeware,name="cookware_bakeware"),
path('kitchen/cutlury_knive',views.cutlury_knive,name="cutlury_knive"),


path('bedding/',views.bedding,name="bedding"),
path('bedding/bedding_essentials',views.bedding_essentials,name="bedding_essentials"),

path('Bath/',views.Bath,name="Bath"),
path('Bath/bath_linnens_towels',views.bath_linnens_towels,name="bath_linnens_towels"),
path('Bath/bath_accessories_storage',views.bath_accessories_storage,name="bath_accessories_storage"),
path('Bath/bath_hardware',views.bath_hardware,name="bath_hardware"),
path('Bath/bath_furniture',views.bath_furniture,name="bath_furniture"),
path('Bath/bath_sent',views.bath_sent,name="bath_sent"),


path('Decor_Pillow/',views.Decor_Pillow,name="Decor_Pillow"),
path('Decor_Pillow/pillows_cushions',views.pillows_cushions,name="pillows_cushions"),
path('Decor_Pillow/wall_art_frames',views.bath_sent,name="wall_art_frames"),
path('Decor_Pillow/mirrors',views.mirrors,name="mirrors"),
path('Decor_Pillow/botanicals_vases',views.botanicals_vases,name="botanicals_vases"),
path('Decor_Pillow/candles_fragrance',views.candles_fragrance,name="candles_fragrance"),
path('Decor_Pillow/decorative_objects ',views.decorative_objects,name="decorative_objects"),

path('lighting/',views.lighting,name="lighting"),
path('lighting/ceiling_lights ',views.ceiling_lights,name="ceiling_lights"),
path('lighting/table_floor_lamps ',views.table_floor_lamps,name="table_floor_lamps"),
path('lighting/wall_light_sconces ',views.wall_light_sconces ,name="wall_light_sconces"),


path('window/',views.window,name="window"),
path('window/all_window_curtains ',views.all_window_curtains ,name="all_window_curtains"),
path('window/blackout_curtains',views.blackout_curtains ,name="blackout_curtains"),
path('window/sheer_curtains ',views.sheer_curtains ,name="sheer_curtains"),
path('window/window_curtain_hardware ',views.window_curtain_hardware ,name="window_curtain_hardware"),

]