import os
import cloudinary.api
from django.db import transaction
from PIL import Image
from website.models import ProductImage, ProductVideo

# Get all Cloudinary images
resources = []
next_cursor = None

while True:
    kwargs = {
        "type": "upload",
        "resource_type": "image",
        "max_results": 500,
    }
    if next_cursor:
        kwargs["next_cursor"] = next_cursor

    result = cloudinary.api.resources(**kwargs)
    resources.extend(result["resources"])
    next_cursor = result.get("next_cursor")

    if not next_cursor:
        break

# Match images using exact file size + dimensions + format
image_map = {}

for r in resources:
    key = (
        r.get("bytes"),
        r.get("width"),
        r.get("height"),
        r.get("format", "").lower(),
    )
    image_map.setdefault(key, []).append(r)

matched_images = 0
skipped_images = 0

with transaction.atomic():
    for obj in ProductImage.objects.all():
        try:
            path = obj.image.path

            with Image.open(path) as im:
                width, height = im.size
                fmt = (im.format or "").lower()

            size = os.path.getsize(path)

            matches = image_map.get((size, width, height, fmt), [])

            if len(matches) == 1:
                r = matches[0]
                obj.image.name = r["public_id"] + "." + r["format"]
                obj.save(update_fields=["image"])
                matched_images += 1
            else:
                skipped_images += 1

        except Exception:
            skipped_images += 1

# Videos: match by filename/public ID
video_resources = cloudinary.api.resources(
    type="upload",
    resource_type="video",
    max_results=500,
)["resources"]

video_map = {
    r["public_id"].lower(): r
    for r in video_resources
}

matched_videos = 0
skipped_videos = 0

with transaction.atomic():
    for obj in ProductVideo.objects.all():
        try:
            filename = os.path.basename(obj.video.name)
            stem = os.path.splitext(filename)[0].lower()

            r = video_map.get(stem)

            if r:
                obj.video.name = r["public_id"] + "." + r["format"]
                obj.save(update_fields=["video"])
                matched_videos += 1
            else:
                skipped_videos += 1

        except Exception:
            skipped_videos += 1

print()
print("===== CLOUDINARY MIGRATION =====")
print("Images matched :", matched_images)
print("Images skipped :", skipped_images)
print("Videos matched :", matched_videos)
print("Videos skipped :", skipped_videos)
print("================================")