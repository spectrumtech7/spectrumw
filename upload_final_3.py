import os
import cloudinary
import cloudinary.uploader
from django.conf import settings
from website.models import Product

# Upload only these 2 images
files = [
    "product_images/FV_depFFKS.png",
    "product_images/BV_NmNDjwS.png",
]

for file in files:
    path = os.path.join(settings.MEDIA_ROOT, file)

    if not os.path.exists(path):
        print(f"NOT FOUND: {file}")
        continue

    public_id = os.path.splitext(os.path.basename(file))[0]

    try:
        result = cloudinary.uploader.upload(
            path,
            public_id=public_id,
            overwrite=True,
            resource_type="image"
        )
        print(f"UPLOADED: {file} -> {result['public_id']}")
    except Exception as e:
        print(f"ERROR: {file} | {e}")

# Fix ST-103 to use the EXISTING Cloudinary image
product = Product.objects.filter(name__icontains="ST-103").first()

if product:
    product.image.name = "ST_no._103.jpg"
    product.save(update_fields=["image"])
    print("ST-103 UPDATED -> Cloudinary: ST_no._103.jpg")
else:
    print("ST-103 PRODUCT NOT FOUND")