from PIL import Image, ImageDraw
import numpy as np
def crop(path: str):
    img = Image.open(path)
    resize_img = img.resize(size=(1920, 1080))
    convert = resize_img.convert('RGBA')

    polygon = [(960, 0), (1449, 0), (1449, 1080), (727, 1080)]

    mask = Image.new("L", resize_img.size, 0)
    draw = ImageDraw.Draw(mask)

    draw.polygon(polygon, fill=255)

    image_np = np.array(convert)
    mask_np = np.array(mask)

    image_np[:, :, 3] = mask_np

    final_image = Image.fromarray(image_np)

    cropped_image_path = 'polygon_cropped_image.png'
    final_image.save(cropped_image_path)