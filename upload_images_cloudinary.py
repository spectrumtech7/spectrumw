import os
import cloudinary
import cloudinary.uploader

from django.conf import settings
from website.models import ProductImage


print("\n===== CLOUDINARY IMAGE UPLOAD =====")

uploaded = 0
errors = 0

images = ProductImage.objects.all()

for obj in images:

    try:
        # Get actual local file path
        file_path = os.path.join(
            settings.BASE_DIR,
            obj.image.name
        )

        if not os.path.exists(file_path):
            print(f"NOT FOUND: {obj.image.name}")
            errors += 1
            continue

        # Filename without extension = Public ID
        filename = os.path.basename(obj.image.name)
        public_id = os.path.splitext(filename)[0]

        # Upload / overwrite using filename as Public ID
        result = cloudinary.uploader.upload(
            file_path,
            public_id=public_id,
            asset_folder="SPECTRUM/PRODUCT IMAGES",
            resource_type="image",
            overwrite=True
        )

        print(f"UPLOADED: {obj.image.name} -> {result['public_id']}")
        uploaded += 1

    except Exception as e:
        print(f"ERROR: {obj.image.name} | {e}")
        errors += 1


print("\n===== DONE =====")
print(f"Uploaded : {uploaded}")
print(f"Errors   : {errors}")