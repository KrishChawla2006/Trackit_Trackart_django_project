from django.shortcuts import render,redirect
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from Trackart.models import Products,Wishlist,Purchase
from dashboard.models import CustomUser
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from gtts import gTTS
import logging
from io import BytesIO
import json
import requests
from django.db.models import Q
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from email.mime.image import MIMEImage
from django.core.mail import EmailMultiAlternatives
from django.conf import settings

# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
# d=Products.objects.all()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define the template for the chatbot
template = """
You are a helpful assistant for the Trackart ecommerce website.
Answer questions briefly,shortly and accurately based on the information provided.

CONTEXT:
{context}

USER QUESTION:
{question}

If the question is about products and product data is provided in the context, include details about those products.
The price of products should be in Indian Rupees (₹).
dont's say add to cart.
If the user asks about something unrelated to Trackart or ecommerce, politely redirect them to topics related to shopping or our products.
Keep responses concise, professional and helpful.
"""

# Initialize the LLM and chain
try:
    # Test Ollama server connection
    response = requests.get("http://localhost:11434", timeout=5)
    if response.status_code != 200:
        logger.error("Ollama server not running or inaccessible at http://localhost:11434")
        raise Exception("Ollama server not running")
    
    logger.info("Ollama server is running")
    model = OllamaLLM(model="llama3", num_thread=4)
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model
except Exception as e:
    logger.error("Failed to initialize OllamaLLM: %s", str(e), exc_info=True)
    raise


def chat_view(request):
    """Handle chat requests and responses"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    try:
        # Parse request data
        data = json.loads(request.body)
        user_input = data.get('message')
        if not user_input:
            logger.error("No message provided in request")
            return JsonResponse({'error': 'No message provided'}, status=400)

        # Get conversation history from session
        conversation_context = request.session.get('conversation_context', [])
        context_limit = 5
        recent_context = "\n".join([f"User: {exchange['user']}\nAI: {exchange['ai']}" 
                                   for exchange in conversation_context[-context_limit:]])
        
        # Prepare context with product information if applicable
        context = recent_context
        product_info = ""
        
        # Check if this is a product-related query
        product_keywords = ['product', 'item', 'buy', 'purchase', 'shop', 'category', 'price', 
                           'available', 'stock', 'sale', 'discount', 'offer', 'show me']
        
        is_product_query = any(keyword in user_input.lower() for keyword in product_keywords)
        
        # Add product search functionality
        if is_product_query:
            # Use the exact fields from your Products model
            # This matches the model you provided with fields:
            # id, category, sub_category, image_link, description, offer_price, original_price, discount, quantity
            products = Products.objects.filter(
                Q(description__icontains=user_input) |
                Q(category__icontains=user_input) |
                Q(sub_category__icontains=user_input)
            )[:5]  # Limit to 5 products
            
            logger.info(f"Search query: '{user_input}'")
            logger.info(f"Total products in database: {Products.objects.count()}")
            
            # For debugging, count matches in each field separately
            desc_matches = Products.objects.filter(description__icontains=user_input).count()
            cat_matches = Products.objects.filter(category__icontains=user_input).count()
            subcat_matches = Products.objects.filter(sub_category__icontains=user_input).count()
            logger.info(f"Matches - Description: {desc_matches}, Category: {cat_matches}, Subcategory: {subcat_matches}")
            
            # Log the SQL query for debugging (optional)
            logger.info(f"SQL Query: {str(products.query)}")
            logger.info(f"Found {products.count()} products")
            
            if products:
                product_details = []
                for product in products:
                    # Using fields from your Products model
                    product_url = f"/products/detail/{product.id}/"
                    
                    # Log each product found (for debugging)
                    logger.info(f"Found product: {product.description} in category {product.category}")
                    
                    # Use the to_dict method from your model
                    product_dict = product.to_dict()
                    product_dict["url"] = request.build_absolute_uri(product_url)
                    product_details.append(product_dict)
                
                # Format product information for the context
                product_list = []
                for product in product_details:
                    product_list.append(
                        f"Product: {product['name']}\n"
                        f"Price: ₹{product['price']}\n"
                        f"Category: {product['category']}\n"
                        f"URL: {product['url']}"
                    )
                
                product_info = "PRODUCT INFORMATION:\n" + "\n\n".join(product_list)
                
                # Add product information to context
                context = f"{recent_context}\n\n{product_info}"
                logger.info(f"Found {len(products)} products matching query")
            else:
                # If no products were found with the initial query, try a broader search
                # This is especially helpful for partial matches or typos
                search_terms = user_input.lower().split()
                if len(search_terms) > 1:
                    broader_query = Q()
                    for term in search_terms:
                        if len(term) > 3:  # Only use terms longer than 3 characters
                            broader_query |= Q(description__icontains=term)
                            broader_query |= Q(category__icontains=term)
                            broader_query |= Q(sub_category__icontains=term)
                    
                    products = Products.objects.filter(broader_query)[:5]
                    logger.info(f"Broader search found {products.count()} products")
                    
                    if products:
                        # Same product formatting as above
                        product_details = []
                        for product in products:
                            product_url = f"/products/detail/{product.id}/"
                            product_details.append({
                                "name": product.description,
                                "price": product.offer_price,
                                "category": product.category,
                                "url": request.build_absolute_uri(product_url)
                            })
                        
                        product_list = []
                        for product in product_details:
                            product_list.append(
                                f"Product: {product['name']}\n"
                                f"Price: ${product['price']}\n"
                                f"Category: {product['category']}\n"
                                f"URL: {product['url']}"
                            )
                        
                        product_info = "PRODUCT INFORMATION:\n" + "\n\n".join(product_list)
                        context = f"{recent_context}\n\n{product_info}"
                    else:
                        context = f"{recent_context}\n\nNo products found matching your query. Please try different keywords."
                        logger.info("No products found with broader search")
                else:
                    context = f"{recent_context}\n\nNo products found matching your query. Please try different keywords."
                    logger.info("No products found with initial search")
        
        # Generate response using the LLM
        logger.info(f"Generating response for: {user_input}")
        result = chain.invoke({"context": context, "question": user_input})
        ai_response = str(result) if result is not None else "I'm sorry, I couldn't process your request."
        
        # Update conversation context
        conversation_context.append({"user": user_input, "ai": ai_response})
        request.session['conversation_context'] = conversation_context[-context_limit:]
        request.session.modified = True
        
        return JsonResponse({'response': ai_response})
    
    except Exception as e:
        logger.error("Error in chat_view: %s", str(e), exc_info=True)
        return JsonResponse({'error': f'Internal server error: {str(e)}'}, status=500)      
# Function to load products data for pre-initialization if needed























def speak_view(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    try:
        data = json.loads(request.body)
        text = data.get('text')
        if not text:
            logger.error("No text provided for speak")
            return JsonResponse({'error': 'No text provided'}, status=400)
        logger.info("Generating audio for text: %s", text[:50] + "...")
        tts = gTTS(text=text, lang='en', slow=False)
        audio_buffer = BytesIO()
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        logger.info("Audio generated successfully.")
        return HttpResponse(
            audio_buffer,
            content_type='audio/mp3',
            headers={'Content-Disposition': 'inline; filename="response.mp3"'}
        )
    except Exception as e:
        logger.error("Error in speak_view: %s", str(e), exc_info=True)
        return JsonResponse({'error': 'Failed to generate audio speech.'}, status=500)

def not_manager(user):
    return getattr(user, 'role', '').lower() != 'staff'

def block_role(role_name):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if getattr(request.user, 'role', None) == role_name:
                return HttpResponseForbidden("You are not allowed to access this page.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
# Create your views here.

@login_required
def purchase_history(request):
    purchases = Purchase.objects.filter(user=request.user).order_by('-purchase_date')
    return render(request, 'purchase_history.html', {'purchases': purchases})

def product_search(request):
    user_role = getattr(request.user, 'role', None)  # Safely get the role
    query = request.GET.get('q')
    if not query.isspace():
        products = Products.objects.filter(
            Q(category__icontains=query) |
            Q(sub_category__icontains=query) |
            Q(description__icontains=query)
        )
    else:
        return redirect('products')
    return render(request, 'products.html', {'products': products,'user_role': user_role,"value":query})

def home_view(request):
    user_role = getattr(request.user, 'role', None) 
    return render(request,'trackart/home.html',{'user_role': user_role})

def products_view(request):
    products = Products.objects.all()
    user_role = getattr(request.user, 'role', None)  # Safely get the role
    if request.method == 'POST':
        
            # Get form data
        product_category = request.POST.get('category')
        product_sub_category = request.POST.get('sub_category')
        image_link = request.POST.get('image_link')
        description = request.POST.get('description')
        selling_price = request.POST.get('offer_price')
        original_price = request.POST.get('original_price')
        discount = request.POST.get('discount')

        # Validate required fields
        

        # Create product
        Products.objects.create(
            category=product_category,
            sub_category=product_sub_category,
            image_link=image_link,
            description=description,
            offer_price=selling_price,
            original_price=original_price,
            discount=discount
        )
        products = Products.objects.all()

        return render(request, 'products.html', {'products': products,'user_role': user_role}) 
        
        
        
    return render(request, 'products.html', {'products': products,'user_role': user_role})


def delete_product(request, product_id):
    product= Products.objects.get(id=product_id)
    
    product.delete()
   
       
    return redirect('products')   


# def productDetail_view(request,product_id):
#     user_role = getattr(request.user, 'role', None)
   
#     product= Products.objects.get(id=product_id)
        
#     return render(request,'productDetail.html',{'product':product,'user_role': user_role})

def productDetail_view(request, product_id):
    user_role = getattr(request.user, 'role', None)
    product = Products.objects.get(id=product_id)

    # Session-based Recently Viewed Logic
    recently_viewed = request.session.get('recently_viewed', [])

    if product.id in recently_viewed:
        recently_viewed.remove(product.id)
    recently_viewed.insert(0, product.id)

    request.session['recently_viewed'] = recently_viewed[:5]  # Store max 5

    recently_viewed_products = Products.objects.filter(id__in=recently_viewed).exclude(id=product.id)

    return render(request, 'productDetail.html', {
        'product': product,
        'user_role': user_role,
        'recently_viewed_products': recently_viewed_products
    })

@login_required
def cart_view(request, product_id):
    user_role = getattr(request.user, 'role', None)

    product = Products.objects.get(id=product_id)
    current_user = CustomUser .objects.get(id=request.user.id)
    product.chooser.add(current_user)
    product.save()

    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        item_id = request.POST.get('item_id')
        item = Products.objects.get(id=item_id)
        item.quantity = quantity
        item.save()
        return render(request, 'cart.html', {'user': current_user, 'user_role': user_role})

    return render(request, 'cart.html', {"user": current_user, 'user_role': user_role})

def cart_button(request):
    user_role = getattr(request.user, 'role', None)  # Define user_role at the beginning
    if user_role and user_role.lower() == 'user':
        current_user = CustomUser.objects.get(id=request.user.id)
        if request.method == 'POST':
            quantity = request.POST.get('quantity')
            item_id = request.POST.get('item_id')
            item = Products.objects.get(id=item_id)
            item.quantity = quantity
            item.save()
            return render(request, 'cart.html', {'user': current_user})

        return render(request, 'cart.html', {'user': current_user})
    return HttpResponseForbidden("Access Denied: you are not user.")

def item_quantity(request):
    current_user = CustomUser.objects.get(id=request.user.id)
    if request.method == 'POST':
      
        quantity = request.POST.get('quantity')
        item_id = request.POST.get('item_id')
        item = Products.objects.get(id=item_id)
        item.quantity = quantity
        item.save()
        return render(request, 'cart.html', {'user': current_user})
        
        # Update the quantity of the cart item
       
    current_user = CustomUser.objects.get(id=request.user.id)
    cart_items = Products.objects.filter(chooser=current_user)
    total_price = sum(item.offer_price*item.quantity for item in cart_items)
    return render(request, 'cart.html', {'user': current_user, 'total_price': total_price,"total":total_price+248})

def wishlist_view(request,product_id):
    user_role = getattr(request.user, 'role', None)  # Define user_role at the beginning
    if user_role and user_role.lower() == 'user':
        current_user = CustomUser.objects.get(id=request.user.id)
    product = Products.objects.get(id=product_id)
    try:
        existing_item = Wishlist.objects.get(
            description=product.description,
            chooser=current_user
        )
        messages.warning(request, 'Product already exists in your wishlist!')
    except Wishlist.DoesNotExist:
        # Create new wishlist item only if it doesn't exist
        wishlist_product = Wishlist.objects.create(
            category=product.category,
            sub_category=product.sub_category,
            image_link=product.image_link,
            description=product.description,
            offer_price=product.offer_price,
            original_price=product.original_price,
            discount=product.discount,
        )
        wishlist_product.chooser.add(current_user)
        wishlist_product.save()
        messages.success(request, 'Product added to wishlist successfully!')

        return render(request,'wishlist.html', {"user":current_user}) 
    

    return render(request,'wishlist.html', {"user":current_user,'user_role': user_role}) 
      

def wishlist_button(request):      
    user_role = getattr(request.user, 'role', None)  # Define user_role at the beginning
    if user_role and user_role.lower() == 'user':
        current_user = CustomUser.objects.get(id=request.user.id)
        return render(request, 'wishlist.html', {'user': current_user})
    # Check if the user is a staff member
    else:
        return HttpResponseForbidden("Access Denied: you are not allowed to access this page.")

    

def delete_from_wishlist(request, item_id):
    current_user = CustomUser.objects.get(id=request.user.id)
        
        # Get wishlist item for this specific user
    wishlist_item = Wishlist.objects.filter(id=item_id, chooser=current_user)
        
        # Delete the item
    wishlist_item.delete()
        
        # Get remaining wishlist items for this user
    
        
    return redirect('wishlist_button')
        
def delete_from_cart(request, item_id):
    current_user = CustomUser.objects.get(id=request.user.id)
   
        # Get cart item for this specific user
    cart_item = Products.objects.get(id=item_id)
        
        # Delete the item
    cart_item.chooser.remove(current_user)
        
        # Get remaining cart items for this user
    
        
    return redirect('cart_button')

def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        # Validate required fields
        if not username or not password or not email:
            messages.error(request, 'All fields are required.')
            return redirect('signup')

        # Create user
      
        
      
        return redirect('home')

    return render(request, 'signup.html')


def cart_to_product_checkout(request):
    current_user = request.user
    cart_items = current_user.products_set.all()

    product_list = []
    total = 0
    cid_map = {}

    for index, product in enumerate(cart_items):
        quantity = getattr(product, 'quantity', 1)
        item_total = product.offer_price * quantity
        total += item_total

        # Record purchase
        Purchase.objects.create(
            user=current_user,
            product=product,
            quantity=quantity,
            price=product.offer_price,
            description=product.description,
            image_link=product.image_link
        )

        cid = f'image{index}'
        product_list.append({
            'name': product.description,
            'price': product.offer_price,
            'quantity': quantity,
            'total': item_total,
            'cid': cid  # used in HTML <img src="cid:image0">
        })

        # Download image and prepare for inline embedding
        try:
            response = requests.get(product.image_link)
            if response.status_code == 200:
                image = MIMEImage(response.content)
                image.add_header('Content-ID', f'<{cid}>')
                image.add_header('Content-Disposition', 'inline')
                cid_map[cid] = image
        except Exception as e:
            print(f"Error loading image for {product.description}: {e}")
    
    # Render HTML email with embedded image CIDs
    html_message = render_to_string('checkout_template.html', {
        'username': current_user.username,
        'products': product_list,
        'total': total,
       
    })

    email = EmailMultiAlternatives(
        subject='Thanks for Shopping with Us!',
        body='',
        from_email=settings.EMAIL_HOST_USER,
        to=[current_user.email]
    )
    email.attach_alternative(html_message, "text/html")

    # Attach images
    for cid, image in cid_map.items():
        email.attach(image)

    email.send()

    # Clear cart
    for product in cart_items:
        product.chooser.remove(current_user)

    return redirect('products')


def edit_product(request, product_id):
    item = Products.objects.get(id=product_id)
    products= Products.objects.all()
    user_role = getattr(request.user, 'role', None)
    
    if request.method == 'POST':
        # Get form data
        item.category = request.POST.get('category')
        item.sub_category = request.POST.get('sub_category')
        item.image_link = request.POST.get('image_link')
        item.description = request.POST.get('description')
        item.offer_price = request.POST.get('offer_price')
        item.original_price = request.POST.get('original_price')
        item.discount = request.POST.get('discount')

        # Save the updated product
        item.save()

       

        return redirect('products')
    return render(request, 'products.html', {'product_detail':item,'products': products,"user_role":user_role,"status":True})

def item_quantity(request):
    if request.method == 'POST':
      
        quantity = request.POST.get('quantity')
        item_id = request.POST.get('item_id')
        item = Products.objects.get(id=item_id)
        item.quantity = quantity
        item.save()

        # Update the quantity of the cart item
       
    current_user = CustomUser.objects.get(id=request.user.id)
    cart_items = Products.objects.filter(chooser=current_user)
    total_price = sum(item.offer_price*item.quantity for item in cart_items)
    return render(request, 'cart.html', {'user': current_user, 'total_price': total_price,"total":total_price+248})


def wishlist_cart_btn(request,product_id):
    try:
        # Get current user
        current_user = CustomUser.objects.get(id=request.user.id)
        
        # Get wishlist item
        wishlist_item = Wishlist.objects.get(id=product_id)
        
        # Find corresponding product in Products table
        product = Products.objects.get(description=wishlist_item.description)
        
        # Add product to user's cart
        product.chooser.add(current_user)
        product.save()
        
        # Remove item from wishlist
       
        
        # Get updated cart items
        
        return redirect('cart_button')
            
     
        
    except Wishlist.DoesNotExist:
        messages.error(request, 'Wishlist item not found!')
        return redirect('wishlist')
    except Products.DoesNotExist:
        messages.error(request, 'Product not found!')
        return redirect('wishlist')

   

def view_furniture(request):
    products=Products.objects.filter(category="furniture")
    user_role = getattr(request.user, 'role', None)

    return render(request,'products.html',{"products":products,"user_role":user_role})
def view_living_room(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="furniture",sub_category="livingroom")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def view_dining_room(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="furniture",sub_category="dining_room")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def view_bed_room(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="furniture",sub_category="bedroom")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def view_outdoor(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="furniture",sub_category="outdoor")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def view_bathroom_furniture(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="furniture",sub_category="bathroom_furniture")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def view_home_office_furniture(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="furniture",sub_category="home_office_furniture")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def entry_way_furniture(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="furniture",sub_category="entry_way_furniture")
    return render(request,'products.html',{"products":products,"user_role":user_role})

def tabletop_bar(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="tabletop_bar")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def dinnerware(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="tabletop_bar",sub_category="dinnerware")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def serveware(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="tabletop_bar",sub_category="serveware")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def drinkware(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="tabletop_bar",sub_category="drinkware")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def bar_tools_accessories(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="tabletop_bar",sub_category="bar_tools_accessories")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def table_linnens(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="tabletop_bar",sub_category="table_linnens")
    return render(request,'products.html',{"products":products,"user_role":user_role})


def kitchen(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="kitchen")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def kitchen_appliences_electronics(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="kitchen",sub_category="kitchen_appliences_electronics")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def coffee_espresso_tea(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="kitchen",sub_category="coffee_espresso_tea")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def cookware_bakeware(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="kitchen",sub_category="cookware_bakeware")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def cutlury_knive(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="kitchen",sub_category="cutlury_knive")
    return render(request,'products.html',{"products":products,"user_role":user_role})

def bedding(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="bedding")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def bedding_essentials(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="bedding",sub_category="bedding_essentials")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def Bath(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="bath")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def bath_linnens_towels(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="bath",sub_category="bath_linnens_towels")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def bath_accessories_storage(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="bath",sub_category="bath_accessories_storage")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def bath_hardware(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="bath",sub_category="bath_hardware")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def bath_furniture(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="bath",sub_category="bath_furniture")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def bath_sent(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="bath",sub_category="bath_sent")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def Decor_Pillow(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="decor_pillow")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def pillows_cushions(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="decor_pillow",sub_category="pillows_cushions")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def wall_art_frames(request):
    products=Products.objects.filter(category="decor_pillow",sub_category="wall_art_frames")
    user_role = getattr(request.user, 'role', None)
    return render(request,'products.html',{"products":products,"user_role":user_role})
def mirrors(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="decor_pillow",sub_category="mirrors")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def botanicals_vases(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="decor_pillow",sub_category="botanicals_vases")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def candles_fragrance(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="decor_pillow",sub_category="candles_fragrance")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def decorative_objects(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="decor_pillow",sub_category="decorative_objects")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def lighting(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="lighting")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def ceiling_lights(request):
    products=Products.objects.filter(category="lighting",sub_category="ceiling_lights")
    user_role = getattr(request.user, 'role', None)
    return render(request,'products.html',{"products":products,"user_role":user_role})
def table_floor_lamps(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="lighting",sub_category="table_floor_lamps")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def wall_light_sconces(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="lighting",sub_category="wall_light_sconces")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def window(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="window")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def all_window_curtains(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="window",sub_category="all_window_curtains")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def blackout_curtains(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="window",sub_category="blackout_curtains")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def sheer_curtains(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="window",sub_category="sheer_curtains")
    return render(request,'products.html',{"products":products,"user_role":user_role})
def window_curtain_hardware(request):
    user_role = getattr(request.user, 'role', None)
    products=Products.objects.filter(category="window",sub_category="window_curtain_hardware")
    return render(request,'products.html',{"products":products,"user_role":user_role})


