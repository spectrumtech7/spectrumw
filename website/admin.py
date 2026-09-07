from django.contrib import admin
from .models import Product, ContactMessage, GalleryCategory, GalleryItem, BuyNowClick, ProductImage, ProductVideo, ProductSpecification, ProductCategory

admin.site.register(BuyNowClick)
admin.site.register(ProductImage)
admin.site.register(ProductVideo)
admin.site.register(ProductSpecification)


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 4

class ProductVideoInline(admin.TabularInline):
    model = ProductVideo
    extra = 1

class ProductSpecificationInline(admin.TabularInline):
    model = ProductSpecification
    extra = 4

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','category','price','is_bestseller')
    list_filter = ('category','is_bestseller',)
    search_fields = ('name','description')
    ordering = ('model_number',)
    inlines = [ProductImageInline, ProductVideoInline, ProductSpecificationInline]

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
    list_display = ('name', 'order')
    

# Register your models here.
