#!/usr/bin/env python3
"""
Image Cropping Utility
Crops the center 16:9 area from a square (1:1) image.
Usage: python3 crop_utils.py <input_path>
"""

import sys
import os

try:
    from PIL import Image
except ImportError:
    print("Error: Pillow library not found. Please run 'pip install Pillow'")
    sys.exit(1)

def crop_center_16x9(input_path):
    try:
        img = Image.open(input_path)
        width, height = img.size
        
        # Target height for 16:9 ratio based on width
        # h = w * (9/16)
        target_height = int(width * 9 / 16)
        
        if target_height > height:
             # If calculated height is bigger than actual height, it means width is too small?
             # actually if image is 1:1, width=height. 
             # target_height = width * 0.5625. So target_height will always be smaller than height.
             # This check is just for safety if input is already weird.
             print(f"Warning: Image height {height} is smaller than target {target_height}. Skipping.")
             return

        # Calculate margins
        top_margin = (height - target_height) // 2
        bottom_margin = top_margin + target_height
        
        # Crop
        cropped = img.crop((0, top_margin, width, bottom_margin))
        
        # Save
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_cropped{ext}"
        
        cropped.save(output_path, quality=95)
        print(f"Success: Cropped {input_path} to {output_path} ({cropped.size[0]}x{cropped.size[1]})")
        return output_path

    except Exception as e:
        print(f"Error processing {input_path}: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 crop_utils.py <input_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        sys.exit(1)
        
    crop_center_16x9(input_file)
