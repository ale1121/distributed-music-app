import os
from PIL import Image

def crop_resize_save_image(in_file, out_path, size=512):
    img = Image.open(in_file.stream).convert("RGB")
    width, height = img.size

    cropped_size = min(width, height)
    left = (width - cropped_size) // 2
    upper = (height - cropped_size) // 2
    img = img.crop((left, upper, left + cropped_size, upper + cropped_size))

    img = img.resize((size, size))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "JPEG")
