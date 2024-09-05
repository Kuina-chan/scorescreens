from PIL import Image, ImageDraw, ImageOps

def add_rounded_corners(image, radius):
    # Create a mask for rounded corners
    mask = Image.new("L", image.size, 0)
    draw = ImageDraw.Draw(mask)
    
    # Draw a rounded rectangle on the mask
    draw.rounded_rectangle([0, 0, *image.size], radius=radius, fill=255)
    
    # Apply the mask to the image using ImageOps
    rounded_image = ImageOps.fit(image, mask.size, centering=(0.5, 0.5))
    rounded_image.putalpha(mask)

    return rounded_image