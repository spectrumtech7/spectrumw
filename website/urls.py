from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('contact/',views.contact, name='contact'),
    path('contact/success/', views.contact_success, name='contact_success'),
    path('team-login/', views.team_login, name='team_login'),
    path('team-logout/', views.team_logout, name='team_logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/add-lead/', views.add_lead, name='add_lead'),
    path('dashboard/export/',views.export_leads, name='export_leads'),
    path('gallery/', views.gallery, name='gallery'),
    path('buy-now/<int:product_id>/',views.buy_now, name='buy_now'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/',views.products_list, name='products_list'),
    path('products/category/<int:category_id>/', views.category_products, name='category_products'),
    path('about/', views.about, name='about'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('cart/update/<int:product_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/checkout/', views.checkout_cart, name='checkout_cart'),
    path('dashboard/import/',views.import_excel, name='import_excel'),
    path('dashboard/delete-lead/<int:lead_id>/', views.delete_lead, name='delete_lead'),
    path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),
]