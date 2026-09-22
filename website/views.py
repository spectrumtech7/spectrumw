import csv
import os
import openpyxl
from django.db.models import Q
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import Cart, CartItem, LeadExcelFile, PopupLead, WhatsAppLead, Product, ContactMessage, GalleryCategory,BuyNowClick, ProductCategory


MARKETING_TEAM = ["Hetal Dodhi", "Komal Wagh", "Bhagyashree Sonar", "Mamta Vishwakarma"]  # replace with real names

USERNAME_TO_FULLNAME ={
    "hetal": "Hetal Dodhi",
    "komal": "Komal Wagh",
    "bhagyashree": "Bhagyashree Sonar",
    "mamta": "Mamta Vishwakarma",
    "suraj": "Suraj Jaiswal"
}


def team_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')
        else:
            return render(request, 'website/team_login.html', {'error': 'Invalid username or password'})
    return render(request, 'website/team_login.html')

def staff_access(request):
    if request.method == 'POST':
        code = request.POST.get('code')

        if code == os.getenv('STAFF_ACCESS_CODE'):
            response = redirect('home')
            response.set_cookie(
                'staff_no_popup',
                'true',
                max_age=31536000
            )
            return response

        return render(
            request,
            'website/staff_access.html',
            {'error': 'Invalid staff code'}
        )

    return render(request, 'website/staff_access.html')

def team_logout(request):
    logout(request)
    return redirect('team_login')

@login_required
def dashboard(request):
    full_name = USERNAME_TO_FULLNAME.get(request.user.username)

    search_query = request.GET.get('q', '').strip()

    leads = ContactMessage.objects.filter(
        assigned_to=full_name
    )

    if search_query:
        leads = leads.filter(
            Q(name__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(message__icontains=search_query)
        )

    leads = leads.order_by('-submitted_at')

    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        new_status = request.POST.get('new_status')
        lead = ContactMessage.objects.get(id=lead_id)
        lead.status = new_status
        lead.save()
        return redirect('dashboard')

    for lead in leads:
        digits = ''.join(filter(str.isdigit, lead.phone))
        if len(digits) == 10:
            lead.whatsapp_number = '91' + digits
        else:
            lead.whatsapp_number = digits

    return render(
        request,
        'website/dashboard.html',
        {
            'leads': leads,
            'name': full_name,
            'search_query': search_query,
        }
    )

    
@login_required
def add_lead(request):
    full_name = USERNAME_TO_FULLNAME.get(request.user.username)

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        location = request.POST.get('location')

        WhatsAppLead.objects.create(
            name=name,
            phone=phone,
            location=location,
            added_by=full_name
        )

        return redirect('whatsapp_leads')

    return render(
        request,
        'website/add_lead.html',
        {'name': full_name}
    )

@login_required
def whatsapp_leads(request):
    full_name = USERNAME_TO_FULLNAME.get(request.user.username)

    leads = WhatsAppLead.objects.filter(
        added_by=full_name
    ).order_by('-added_at')

    if request.method == 'POST':
        lead_id = request.POST.get('lead_id')
        new_status = request.POST.get('new_status')

        lead = WhatsAppLead.objects.get(
            id=lead_id,
            added_by=full_name
        )

        lead.status = new_status
        lead.save()

        return redirect('whatsapp_leads')

    for lead in leads:
        digits = ''.join(filter(str.isdigit, lead.phone))

        if len(digits) == 10:
            lead.whatsapp_number = '91' + digits
        else:
            lead.whatsapp_number = digits

    return render(
        request,
        'website/whatsapp_leads.html',
        {
            'leads': leads,
            'name': full_name,
        }
    )

@login_required
def delete_whatsapp_lead(request, lead_id):
    full_name = USERNAME_TO_FULLNAME.get(request.user.username)

    WhatsAppLead.objects.filter(
        id=lead_id,
        added_by=full_name
    ).delete()

    return redirect('whatsapp_leads')
    
@login_required
def export_leads(request):
    full_name = USERNAME_TO_FULLNAME.get(request.user.username)
    leads = ContactMessage.objects.filter(assigned_to=full_name).order_by('-submitted_at')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{full_name}leads.csv"'

    writer =  csv.writer(response)
    writer.writerow(['Name', 'Phone', 'Email', 'Message', 'Status', 'Submitted At'])

    for lead in leads:
        writer.writerow([lead.name, lead.phone, lead.email, lead.message, lead.status, lead.submitted_at])

    return response

def home(request):
    bestsellers = Product.objects.filter(is_bestseller=True).order_by('model_number')
    return render(request, 'website/home.html', {'bestsellers': bestsellers})

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        email = request.POST.get('email', '').strip()
        message = request.POST.get('message', '').strip()
        location = request.POST.get('location', '').strip()

        if not name.replace(' ', '').isalpha():
            return render(request, 'website/contact.html', {
                'error': 'Name should contain letters and spaces only.'
            })

        if not phone.isdigit() or len(phone) != 10:
            return render(request, 'website/contact.html', {
                'error': 'Enter a valid 10-digit phone number.'
            })

        if len(location) > 255:
            return render(request, 'website/contact.html', {
                'error': 'Location is too long.'
            })

        total_so_far = ContactMessage.objects.count()
        assigned_person = MARKETING_TEAM[total_so_far % len(MARKETING_TEAM)]

        ContactMessage.objects.create(
            name=name,
            phone=phone,
            email=email,
            message=message,
            location=location,
            assigned_to=assigned_person
        )

        number = MARKETING_WHATSAPP.get(assigned_person)
        whatsapp_message = f"Hi, I'm {name} from {location or 'unknown location'}, I submitted an inquiry: {message or 'General inquiry'}"
        whatsapp_url = f"https://wa.me/{number}?text={whatsapp_message}"

        return render(
            request,
            'website/contact_success.html',
            {'whatsapp_url': whatsapp_url}
        )

    return render(request, 'website/contact.html')

# def contact(request):
#     if request.method == 'POST':
#         name = request.POST.get('name')
#         phone = request.POST.get('phone')
#         email = request.POST.get('email')
#         message = request.POST.get('message')
#         location = request.POST.get('location')

#         total_so_far = ContactMessage.objects.count()
#         assigned_person = MARKETING_TEAM[total_so_far % len(MARKETING_TEAM)]

#         ContactMessage.objects.create(
#             name=name, phone=phone, email=email,
#             message=message, location=location, assigned_to=assigned_person
#         )

#         number = MARKETING_WHATSAPP.get(assigned_person)
#         whatsapp_message = f"Hi, I'm {name} from {location or 'unknown location'}, I submitted an inquiry: {message or 'General inquiry'}"
#         whatsapp_url = f"https://wa.me/{number}?text={whatsapp_message}"

#         # Email notification goes here once app password is ready
#         return render(request,'website/contact_success.html', {'whatsapp_url': whatsapp_url})
#         # return redirect('contact_success')

#     return render(request, 'website/contact.html')

def contact_success(request):
    return render(request, 'website/contact_success.html')

def gallery(request):
    categories = GalleryCategory.objects.prefetch_related('items').all()
    return render(request, 'website/gallery.html', {'categories': categories})


MARKETING_WHATSAPP = {
    "Hetal Dodhi": "917859905601",
    "Komal Wagh" : "917285814369",
    "Bhagyashree Sonar": "919313244024",
    "Mamta Vishwakarma": "918401107805",
    "Suraj Jaiswal": "918866264064",
}

def buy_now(request, product_id):
    product = Product.objects.get(id=product_id)

    total_so_far = BuyNowClick.objects.count()
    assigned_person = MARKETING_TEAM[total_so_far % len(MARKETING_TEAM)]

    BuyNowClick.objects.create(product=product, assigned_to=assigned_person)

    number = MARKETING_WHATSAPP.get(assigned_person)
    message = f"Hi, I'm interested in buying: {product.name}"
    whatsapp_url = f"https://wa.me/{number}?text={message}"

    return redirect(whatsapp_url)

def product_detail(request, product_id):
    product = Product.objects.get(id=product_id)
    angle_order = ['front','back','side','cross']
    images = sorted(product.images.all(), key=lambda img: angle_order.index(img.angle)if img.angle in angle_order else 99)
    videos = product.videos.all()
    specifications = product.specifications.all()
    return render(request, 'website/product_detail.html',{
        'product':product,
        'images':images,
        'videos':videos,
        'specifications':specifications,
    })

def products_list(request):
    categories = ProductCategory.objects.prefetch_related('products').all()
    return render(request, 'website/products.html', {'categories': categories})

def category_products(request, category_id):
    category = ProductCategory.objects.get(id=category_id)
    products = category.products.all().order_by('model_number')
    return render(request, 'website/category_products.html', {'category': category, 'products': products})

def about(request):
    return render(request, 'website/about.html')


def add_to_cart(request, product_id):
    cart_id = request.COOKIES.get('cart_id')

    if cart_id:
        try:
            cart = Cart.objects.get(cart_id=cart_id)
        except Cart.DoesNotExist:
            cart = Cart.objects.create()
    else:
        cart = Cart.objects.create()

    item, created = CartItem.objects.get_or_create(
        cart=cart,
        product_id=product_id
    )

    if created:
        item.quantity = 1
    elif item.quantity < 3000:
        item.quantity += 1

    item.save()

    response = redirect('view_cart')
    response.set_cookie(
        'cart_id',
        str(cart.cart_id),
        max_age=60 * 60 * 24 * 365
    )

    return response
# def add_to_cart(request, product_id):
#     cart = request.session.get('cart', {})
#     product_id_str = str(product_id)

#     current_quantity = cart.get(product_id_str, 0)

#     if current_quantity < 3000:
#         cart[product_id_str] = current_quantity + 1

#     request.session['cart'] = cart
#     return redirect('view_cart')

def view_cart(request):
    cart_id = request.COOKIES.get('cart_id')
    cart_items = []
    total = 0

    if cart_id:
        try:
            cart = Cart.objects.get(cart_id=cart_id)

            for item in cart.items.select_related('product'):
                subtotal = item.product.price * item.quantity
                total += subtotal

                cart_items.append({
                    'product': item.product,
                    'quantity': item.quantity,
                    'subtotal': subtotal
                })

        except Cart.DoesNotExist:
            pass

    return render(
        request,
        'website/cart.html',
        {
            'cart_items': cart_items,
            'total': total
        }
    )

# def view_cart(request):
#     cart = request.session.get('cart', {})
#     cart_items = []
#     total = 0

#     for product_id, quantity in cart.items():
#         try:
#             product = Product.objects.get(id=product_id)
#             subtotal = product.price * quantity
#             total += subtotal
#             cart_items.append({'product': product, 'quantity': quantity, 'subtotal': subtotal})
#         except Product.DoesNotExist:
#             continue

#     return render(request, 'website/cart.html', {'cart_items': cart_items, 'total': total})

def remove_from_cart(request, product_id):
    cart_id = request.COOKIES.get('cart_id')

    if cart_id:
        try:
            cart = Cart.objects.get(cart_id=cart_id)
            CartItem.objects.filter(
                cart=cart,
                product_id=product_id
            ).delete()
        except Cart.DoesNotExist:
            pass

    return redirect('view_cart')
# def remove_from_cart(request, product_id):
#     cart = request.session.get('cart', {})
#     cart.pop(str(product_id), None)
#     request.session['cart'] = cart
#     return redirect('view_cart')



# def update_cart_quantity(request, product_id):
#     if request.method == 'POST':
#         cart = request.session.get('cart', {})

#         try:
#             quantity = int(request.POST.get('quantity', 1))
#         except (ValueError, TypeError):
#             quantity = 1

#         if quantity > 3000:
#             quantity = 3000

#         if quantity >= 1:
#             cart[str(product_id)] = quantity
#         else:
#             cart.pop(str(product_id), None)

#         request.session['cart'] = cart
#         request.session.modified = True

#     return redirect('view_cart')

def update_cart_quantity(request, product_id):
    if request.method == 'POST':
        cart_id = request.COOKIES.get('cart_id')

        if cart_id:
            try:
                cart = Cart.objects.get(cart_id=cart_id)
                item = CartItem.objects.get(
                    cart=cart,
                    product_id=product_id
                )

                quantity = int(request.POST.get('quantity', 1))

                if quantity > 3000:
                    quantity = 3000

                if quantity >= 1:
                    item.quantity = quantity
                    item.save()
                else:
                    item.delete()

            except (Cart.DoesNotExist, CartItem.DoesNotExist, ValueError):
                pass

    return redirect('view_cart')

def checkout_cart(request):
    cart_id = request.COOKIES.get('cart_id')

    if not cart_id:
        return redirect('view_cart')

    try:
        cart = Cart.objects.get(cart_id=cart_id)
    except Cart.DoesNotExist:
        return redirect('view_cart')

    items = cart.items.select_related('product')

    if not items.exists():
        return redirect('view_cart')

    total_so_far = BuyNowClick.objects.count()
    assigned_person = MARKETING_TEAM[total_so_far % len(MARKETING_TEAM)]

    lines = []

    for item in items:
        lines.append(f"{item.product.name} x{item.quantity}")

        BuyNowClick.objects.create(
            product=item.product,
            assigned_to=assigned_person
        )

    message = "Hi, I'm interested in ordering:\n" + "\n".join(lines)

    number = MARKETING_WHATSAPP.get(assigned_person)
    whatsapp_url = f"https://wa.me/{number}?text={message}"

    cart.delete()

    return redirect(whatsapp_url)

# def checkout_cart(request):
#     cart = request.session.get('cart', {})
#     if not cart:
#         return redirect('view_cart')

#     total_so_far = BuyNowClick.objects.count()
#     assigned_person = MARKETING_TEAM[total_so_far % len(MARKETING_TEAM)]

#     lines = []
#     for product_id, quantity in cart.items():
#         try:
#             product = Product.objects.get(id=product_id)
#             lines.append(f"{product.name} x{quantity}")
#             BuyNowClick.objects.create(product=product, assigned_to=assigned_person)
#         except Product.DoesNotExist:
#             continue

#     message = "Hi, I'm interested in ordering:\n" + "\n".join(lines)
#     number = MARKETING_WHATSAPP.get(assigned_person)
#     whatsapp_url = f"https://wa.me/{number}?text={message}"

#     request.session['cart'] = {}
#     return redirect(whatsapp_url)

import openpyxl

@login_required
def import_excel(request):
    full_name = USERNAME_TO_FULLNAME.get(request.user.username)

    if request.method == 'POST':
        excel_file = request.FILES.get('excel_file')

        if not excel_file:
            return redirect('dashboard')

        LeadExcelFile.objects.create(file=excel_file)

    files = LeadExcelFile.objects.order_by('-uploaded_at')

    return render(
        request,
        'website/import_excel.html',
        {'name': full_name, 'files': files}
    )

@login_required
def delete_excel(request, file_id):
    file = LeadExcelFile.objects.get(id=file_id)

    if request.method == 'POST':
        file.delete()

    return redirect('import_excel')

# @login_required
# def import_excel(request):
#     full_name = USERNAME_TO_FULLNAME.get(request.user.username)

#     if request.method == 'POST':
#         excel_file = request.FILES.get('excel_file')
#         if not excel_file:
#             return redirect('dashboard')

#         LeadExcelFile.objects.create(file=excel_file)
#         # excel_file.seek(0)

#         # wb = openpyxl.load_workbook(excel_file)
#         # sheet = wb.active

#         # for row in sheet.iter_rows(min_row=2, values_only=True):
#         #     name, phone, email, location, message = (row + (None,) * 5)[:5]
#         #     if not name:
#         #         continue
#         #     ContactMessage.objects.create(
#         #         name=str(name),
#         #         phone=str(phone) if phone else '',
#         #         email=str(email) if email else '',
#         #         location=str(location) if location else '',
#         #         message=str(message) if message else 'Imported from Excel',
#         #         assigned_to=full_name,
#         #         status='new'
#         #     )

#         return redirect('dashboard')

#     return render(request, 'website/import_excel.html', {'name': full_name, 'files':files})

@login_required
def delete_lead(request, lead_id):
    full_name = USERNAME_TO_FULLNAME.get(request.user.username)
    try:
        lead = ContactMessage.objects.get(id=lead_id, assigned_to=full_name)
        lead.delete()
    except ContactMessage.DoesNotExist:
        pass
    return redirect('dashboard')


def submit_popup(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        profession = request.POST.get('profession', '').strip()
        interested_in = request.POST.get('interested_in', '').strip()

        if not name.replace(' ', '').isalpha():
            return redirect('home')

        if not phone.isdigit() or len(phone) != 10:
            return redirect('home')

        if not PopupLead.objects.filter(phone=phone).exists():
            PopupLead.objects.create(
                name=name,
                phone=phone,
                profession=profession,
                interested_in=interested_in,
            )

        response = redirect('home')
        response.set_cookie(
            'popup_submitted',
            'true',
            max_age=60 * 60 * 24 * 365
        )
        return response

    return redirect('home')
# def submit_popup(request):
#     if request.method == 'POST':
#         name = request.POST.get('name', '').strip()
#         phone = request.POST.get('phone', '').strip()
#         profession = request.POST.get('profession', '').strip()
#         interested_in = request.POST.get('interested_in', '').strip()

#         if not name.replace(' ', '').isalpha():
#             return redirect('home')

#         if not phone.isdigit() or len(phone) != 10:
#             return redirect('home')

#         PopupLead.objects.create(
#             name=name,
#             phone=phone,
#             profession=profession,
#             interested_in=interested_in,
#         )

#     return redirect('home')


def privacy_policy(request):
    return render(request,'website/privacy_policy.html')

def terms_conditions(request):
    return render (request,'website/terms_conditions.html')