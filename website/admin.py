from django.contrib import admin
from .models import LeadExcelFile, Product, ContactMessage, GalleryCategory, GalleryItem, BuyNowClick, ProductImage, ProductVideo, ProductSpecification, ProductCategory, PopupLead

admin.site.register(BuyNowClick)
admin.site.register(ProductImage)
admin.site.register(ProductVideo)

@admin.register(ProductSpecification)
class ProductSpecificationAdmin(admin.ModelAdmin):
    fields = ('product', 'label', 'value', 'order')

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
    fields = ('label', 'value', 'order')
    extra = 4

STANDARD_SPECS = [
    ('Pipe ID', 'mm'),
    ('Master Box', 'Pcs'),
    ('Overall Size', 'mm'),
    ('Model', ''),
    ('Certification', ''),
    ('Number of LEDs', 'Nos'),
    ('Wattage', 'W'),
    ('Dimension', 'mm'),
    ('Optical lens', ''),
    ('Weight', 'Kg'),
    ('LED Brand', ''),
    ('Power Consumption', 'W'),
    ('LED Lumens Efficiency', 'lm/W'),
    ('Maximum Lumens', 'lm'),
    ('Beam Angle', 'Degree'),
    ('LED Working Voltage', 'VDC'),
    ('LED Working Current', 'mA'),
    ('Input Voltage', 'VAC'),
    ('Operating Frequency', 'Hz'),
    ('Power Factor', ''),
    ('Ambient Temp (Ta)', '°C'),
    ('Case Temp (Tc)', '°C'),
    ('CRI', ''),
    ('Efficiency', '%'),
    ('Color', ''),
    ('Color Temperature', 'K'),
    ('Body Type', ''),
    ('IP rating', ''),
    ('Working Hours', 'Hours'),
    ('Surge Protection', 'KV'),
    ('Electrical Protections for LED Driver', ''),
    ('LED PCB Detail', ''),
    ('Additional Features', ''),
    ('Terminology', ''),
]


@admin.action(description='Reset standard specification rows (keeps rows that have values)')
def add_standard_specifications(modeladmin, request, queryset):
    created = 0
    removed = 0
    for product in queryset:
        removed += product.specifications.filter(value='').delete()[0]
        for index, (label, unit) in enumerate(STANDARD_SPECS, start=1):
            spec, was_created = ProductSpecification.objects.get_or_create(
                product=product,
                label__iexact=label,
                defaults={'label': label, 'unit': unit, 'value': '', 'order': index},
            )
            if was_created:
                created += 1
            elif spec.order != index:
                spec.order = index
                spec.save(update_fields=['order'])
    modeladmin.message_user(request, f'{removed} blank rows removed, {created} rows added.')

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
