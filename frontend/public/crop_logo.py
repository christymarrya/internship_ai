from PIL import Image
import os

img_path = 'logo.png'

try:
    img = Image.open(img_path).convert("RGBA")
    alpha = img.split()[-1]
    bbox = alpha.getbbox()
    
    if bbox:
        # Add a tiny little bit of padding (e.g., 5% of width) for safety so it's not touching edge
        padding = int((bbox[2] - bbox[0]) * 0.05)
        new_bbox = (
            max(0, bbox[0] - padding),
            max(0, bbox[1] - padding),
            min(img.width, bbox[2] + padding),
            min(img.height, bbox[3] + padding)
        )
        
        cropped = img.crop(new_bbox)
        # We save it as the same file to instantly update it!
        cropped.save(img_path)
        print("Logo has been successfully cropped and scaled!")
    else:
        print("Image is entirely transparent.")

except Exception as e:
    print(f"Error: {e}")
