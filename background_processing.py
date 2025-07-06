from PIL import Image, ImageDraw
import os
import numpy as np
def resize_image_to_width_rgba_png(image_path, output_folder, target_width):
    try:
        with Image.open(image_path) as img:
            original_width, original_height = img.size
            
            # Calculate the new height while maintaining aspect ratio
            new_height = int(target_width * original_height / original_width)
            
            # Resize the image
            resized_img = img.resize((target_width, new_height), Image.LANCZOS) # LANCZOS is a high-quality resampling filter
            
            # Convert to RGBA mode if not already. This adds an alpha channel if missing.
            # If the image already has an alpha channel, it remains.
            if resized_img.mode != 'RGBA':
                resized_img = resized_img.convert('RGBA')
            
            # Create output folder if it doesn't exist
            if not os.path.exists(output_folder):
                os.makedirs(output_folder)
            
            # Construct the output path with .png extension
            file_name_base = os.path.splitext(os.path.basename(image_path))[0] # Get filename without extension
            output_path = os.path.join(output_folder, f"{file_name_base}.png")
            
            # Save the resized image as PNG
            resized_img.save(output_path, format='PNG')
            print(f"Resized '{os.path.basename(image_path)}' to {target_width}x{new_height}, converted to RGBA, and saved as '{output_path}'")
        
            
    except Exception as e:
        print(f"Error processing '{image_path}': {e}")

# --- Configuration ---
input_directory = "./background" # <--- IMPORTANT: Change this to your folder
output_directory = "./background_cropped" # <--- Resized images will be saved here
target_width = 1920

# Create the output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)


# Process all images in the input directory
for filename in os.listdir(input_directory):
    # Process common image file types
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
        image_full_path = os.path.join(input_directory, filename)
        resize_image_to_width_rgba_png(image_full_path, output_directory, target_width=1920)

print("\n--- Resizing, RGBA conversion, and PNG saving complete! ---")

#cropping the background:
position = [(0,0), (0, 1080), (1200, 1080), (1450, 0)]
# Open the image
img = Image.open("./background_cropped/Houjuu.Nue.full.168235.png").convert("RGBA") # Ensure image has an alpha channel
width, height = img.size
print(width, height)
# Create a mask image with the same dimensions as the original image
mask = Image.new('L', (width, height), 0) # 'L' for 8-bit pixels, 0 for black

# Draw the polygon on the mask in white (255)
draw = ImageDraw.Draw(mask)
draw.polygon(position, fill=255)

# Apply the mask to the original image
# This will make areas outside the polygon transparent

inverted_mask = Image.eval(mask, lambda x: 255 - x) # <--- NEW LINE

dim_factor = 0.6  # Adjust this value between 0.0 (fully black) and 1.0 (original brightness)
dimmed_img_data = np.array(img) * dim_factor
dimmed_img = Image.fromarray(dimmed_img_data.astype(np.uint8))

# Create a new blank RGBA image (this will be our output image)
# This starts completely transparent
output_img = Image.new("RGBA", img.size)

# Paste the dimmed image using the inverted mask.
# This will put the dimmed 'outside' area onto the transparent background.
output_img.paste(dimmed_img, (0, 0), inverted_mask)

# Save the result
output_img.save(f"./cache/croppedbackground.png")
place_pos_x = (1920-1200)/2
if height < 1080:
    resize_image_to_width_rgba_png("./background_cropped/Houjuu.Nue.full.168235.png", output_directory="./cache", target_width=1920)
