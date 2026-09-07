from django.db import models



STATUS_CHOICES={
    ('new', 'New'),
    ('contacted', 'Contacted'),
    ('closed', 'Closed'),
}

class Product(models.Model):
    name = models.CharField(max_length=100)
    model_number = models.IntegerField(default=0)
    category = models.ForeignKey('ProductCategory', on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    image= models.ImageField(upload_to = 'products/')
    is_bestseller = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def cover_image(self):
        cross_image = self.images.filter(angle='cross').first()
        if cross_image:
            return cross_image.image.url
        return self.image.url
    
class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    email = models.EmailField()
    message = models.TextField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    assigned_to = models.CharField(max_length=100, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

class GalleryCategory(models.Model):
    name=models.CharField(max_length=100)
    order=models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name
    
class GalleryItem(models.Model):
    MEDIA_TYPE_CHOICES=[
        ('image', 'Image'),
        ('video', 'Video'),
    ]
    category = models.ForeignKey(GalleryCategory, on_delete=models.CASCADE, related_name='items')
    media_type = models.CharField(max_length=10, choices=MEDIA_TYPE_CHOICES)
    media_file = models.FileField(upload_to='gallery/')
    caption = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ['caption']

    def __str__(self):
            return f"{self.category.name} - {self.caption or self.media_type}"

class BuyNowClick(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    assigned_to = models.CharField(max_length=100, blank=True)
    clicked_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} - {self.assigned_to}"

class ProductImage(models.Model):
    ANGLE_CHOICES=[
        ('front','Front'),
        ('back','Back'),
        ('side','Side'),
        ('cross','Cross-section'),
    ]
    product=models.ForeignKey(Product, on_delete=models.CASCADE,related_name='images')
    angle = models.CharField(max_length=10, choices=ANGLE_CHOICES)
    image = models.ImageField(upload_to='product_images/')

    def __str__(self):
        return f"{self.product.name} - {self.angle}"

class ProductVideo(models.Model):
    product = models.ForeignKey(Product, on_delete = models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='product_videos/')

    def __str__(self):
        return f"{self.product.name} - video"

class ProductSpecification(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='specifications')
    label = models.CharField(max_length=100)
    value = models.CharField(max_length=200)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.product.name} - {self.label}"

class ProductCategory(models.Model):
    name = models.CharField(max_length=100)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.name

