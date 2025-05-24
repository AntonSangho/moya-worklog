#!/usr/bin/env python3
"""
Image converter for Moya Worklog ESP32
Converts PNG images to binary format for thermal printer
"""

import os
import sys
from PIL import Image
import struct

def png_to_thermal_binary(png_path, output_path, target_width=480, target_height=1000):
    """
    Convert PNG image to binary format for thermal printer
    
    Args:
        png_path: Path to input PNG file
        output_path: Path to output binary file
        target_width: Target width for thermal printer (default 480)
        target_height: Target height for thermal printer (default 1000)
    """
    try:
        # Open and process image
        img = Image.open(png_path)
        
        # Resize image
        img_resized = img.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Convert to grayscale if not already
        if img_resized.mode != 'L':
            img_resized = img_resized.convert('L')
        
        # Convert to monochrome (1-bit)
        # Use dithering for better quality
        img_mono = img_resized.convert('1', dither=Image.Dither.FLOYDSTEINBERG)
        
        # Convert to bytes array for thermal printer
        width, height = img_mono.size
        bytes_per_line = (width + 7) // 8
        
        binary_data = bytearray()
        
        for y in range(height):
            line_data = bytearray(bytes_per_line)
            for x in range(width):
                pixel = img_mono.getpixel((x, y))
                if pixel == 0:  # Black pixel
                    byte_index = x // 8
                    bit_index = 7 - (x % 8)
                    line_data[byte_index] |= (1 << bit_index)
            
            binary_data.extend(line_data)
        
        # Write binary data to file
        with open(output_path, 'wb') as f:
            f.write(binary_data)
        
        print(f"Converted {png_path} -> {output_path}")
        print(f"Size: {width}x{height}, Data: {len(binary_data)} bytes")
        
        return True
        
    except Exception as e:
        print(f"Error converting {png_path}: {e}")
        return False

def convert_all_images(image_dir, output_dir):
    """
    Convert all PNG images in directory to binary format
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    png_files = [f for f in os.listdir(image_dir) if f.endswith('.png')]
    
    if not png_files:
        print(f"No PNG files found in {image_dir}")
        return
    
    print(f"Found {len(png_files)} PNG files to convert")
    
    for png_file in png_files:
        png_path = os.path.join(image_dir, png_file)
        output_name = png_file.replace('.png', '.bin')
        output_path = os.path.join(output_dir, output_name)
        
        convert_png_to_thermal_binary(png_path, output_path)

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 image_converter.py <png_file> [output_file]")
        print("  python3 image_converter.py --batch <image_dir> [output_dir]")
        sys.exit(1)
    
    if sys.argv[1] == '--batch':
        if len(sys.argv) < 3:
            print("Error: --batch requires image directory")
            sys.exit(1)
        
        image_dir = sys.argv[2]
        output_dir = sys.argv[3] if len(sys.argv) > 3 else 'converted'
        convert_all_images(image_dir, output_dir)
    
    else:
        png_path = sys.argv[1]
        output_path = sys.argv[2] if len(sys.argv) > 2 else png_path.replace('.png', '.bin')
        
        if not os.path.exists(png_path):
            print(f"Error: File {png_path} not found")
            sys.exit(1)
        
        png_to_thermal_binary(png_path, output_path)

if __name__ == '__main__':
    main()