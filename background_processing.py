from PIL import Image
import os

def resize_image_to_width_rgba_png(image_path, output_folder, target_width=1920):
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
output_directory = "" # <--- Resized images will be saved here
target_width = 1920

# Create the output directory if it doesn't exist
if not os.path.exists(output_directory):
    os.makedirs(output_directory)

# Process all images in the input directory
for filename in os.listdir(input_directory):
    # Process common image file types
    if filename.lower().endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp', '.tiff')):
        image_full_path = os.path.join(input_directory, filename)
        resize_image_to_width_rgba_png(image_full_path, output_directory, target_width)

print("\n--- Resizing, RGBA conversion, and PNG saving complete! ---")