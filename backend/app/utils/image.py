import os
from PIL import Image
from uuid import uuid4


def crop_resize_save_image(in_file, out_dir, file_name, size=512):
    """
    Crop image to square, resize to given size and save to out_path
    """

    img = Image.open(in_file.stream).convert("RGB")
    width, height = img.size

    cropped_size = min(width, height)
    left = (width - cropped_size) // 2
    upper = (height - cropped_size) // 2

    img = img.crop((left, upper, left + cropped_size, upper + cropped_size))
    img = img.resize((size, size))

    os.makedirs(out_dir, exist_ok=True)

    out_file = f"{file_name}-{uuid4().hex}.webp"
    out_path = os.path.join(out_dir, out_file)
    img.save(out_path, "WEBP")

    return out_file, out_path
