from django.contrib import admin
from .models import LeadExcelFile, Product, ContactMessage, GalleryCategory, GalleryItem, BuyNowClick, ProductImage, ProductVideo, ProductSpecification, ProductCategory, PopupLead

admin.site.register(BuyNowClick)
admin.site.register(ProductImage)
admin.site.register(ProductVideo)
admin.site.register(ProductSpecification)
admin.site.register(PopupLead)
admin.site.register(LeadExcelFile)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 4

class ProductVideoInline(admin.TabularInline):
    model = ProductVideo
    extra = 1

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 4

STANDARD_SPECS = [
    ('Power Consumption', 'W'),
    ('Colour Temperature', 'K'),
    ('Beam Angle', 'Degree'),
    ('Optical Cover', 'Material'),
    ('Light Source', 'Material'),
    ('Housing Material', 'Material'),
    ('Voltage Range', 'V'),
    ('Protection Rating', 'Standard'),
    ('No. of LEDs', 'Number'),
    ('Lumens/LED', 'lm/W'),
    ('Maximum Lumens', 'lm'),
    ('Operating Temperature', '°C'),
    ('Driver', 'Standard'),
    ('Power Factor', ''),
    ('Warranty', 'Years'),
    ('Weight', 'Kg'),
    ('Lifespan', 'Hours'),
    ('Surge Voltage Protection', 'KV'),
    ('Short Circuit Protection', ''),
    ('High Voltage Protection', 'VAC'),
    ('Surge Protector Device', ''),
]


@admin.action(description='Add standard specification rows to selected products')
def add_standard_specifications(modeladmin, request, queryset):
    created = 0
    for product in queryset:
        for index, (label, unit) in enumerate(STANDARD_SPECS, start=1):
            _, was_created = ProductSpecification.objects.get_or_create(
                product=product,
                label__iexact=label,
                defaults={'label': label, 'unit': unit, 'value': '', 'order': index},
            )
            if was_created:
                created += 1
    modeladmin.message_user(request, f'{created} rows added.')

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('sku', 'name', 'category', 'price', 'is_bestseller')
    list_filter = ('category', 'is_bestseller')
    search_fields = ('sku', 'name', 'description')
    ordering = ('sku', 'model_number')
    inlines = [ProductImageInline, ProductVideoInline, ProductSpecificationInline]
    actions = [add_standard_specifications]

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone', 'email', 'message', 'status', 'submitted_at')
    list_filter = ('status', 'submitted_at')
    search_fields = ('name', 'phone', 'email')
    ordering = ('-submitted_at',)
    list_editable = ('status',)

class GalleryItemInline(admin.TabularInline):
    model = GalleryItem
    extra=1

@admin.register(GalleryCategory)
class GalleryCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'order')
    inlines = [GalleryItemInline]

@admin.register(GalleryItem)
class GalleryItemAdmin(admin.ModelAdmin):
    list_display = ('category', 'media_type', 'caption')
    list_filter = ('category', 'media_type')

@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'order')
    

# Register your models here.
