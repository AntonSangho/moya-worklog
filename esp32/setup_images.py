#!/usr/bin/env python3
"""
Image setup script for Moya Worklog ESP32
Converts PNG images and creates SPIFFS data for upload
"""

import os
import sys
import shutil
from image_converter import png_to_thermal_binary

def setup_spiffs_data():
    """
    Setup SPIFFS data directory with converted images
    """
    # Paths
    source_image_dir = "../image"
    spiffs_data_dir = "data"
    
    # Create data directory
    if os.path.exists(spiffs_data_dir):
        shutil.rmtree(spiffs_data_dir)
    os.makedirs(spiffs_data_dir)
    
    print("Setting up SPIFFS data directory...")
    
    # Find PNG files in source directory
    if not os.path.exists(source_image_dir):
        print(f"Error: Source image directory {source_image_dir} not found")
        return False
    
    png_files = [f for f in os.listdir(source_image_dir) if f.endswith('.png')]
    
    if not png_files:
        print(f"No PNG files found in {source_image_dir}")
        return False
    
    print(f"Found {len(png_files)} PNG files to convert:")
    
    # Convert each PNG to binary format
    for png_file in png_files:
        png_path = os.path.join(source_image_dir, png_file)
        bin_name = png_file.replace('.png', '.bin')
        bin_path = os.path.join(spiffs_data_dir, bin_name)
        
        print(f"  Converting {png_file}...")
        
        if png_to_thermal_binary(png_path, bin_path):
            print(f"    -> {bin_name} ({os.path.getsize(bin_path)} bytes)")
        else:
            print(f"    -> Failed to convert {png_file}")
    
    # Create file list for ESP32
    file_list_path = os.path.join(spiffs_data_dir, "filelist.txt")
    with open(file_list_path, 'w') as f:
        for png_file in png_files:
            bin_name = png_file.replace('.png', '.bin')
            f.write(f"/{bin_name}\n")
    
    print(f"\nSPIFFS data directory created: {spiffs_data_dir}")
    print("Files included:")
    for file in os.listdir(spiffs_data_dir):
        size = os.path.getsize(os.path.join(spiffs_data_dir, file))
        print(f"  {file} ({size} bytes)")
    
    total_size = sum(os.path.getsize(os.path.join(spiffs_data_dir, f)) 
                     for f in os.listdir(spiffs_data_dir))
    print(f"\nTotal size: {total_size} bytes ({total_size/1024:.1f} KB)")
    
    return True

def create_upload_script():
    """
    Create script to upload SPIFFS data to ESP32
    """
    script_content = '''#!/bin/bash
# Upload SPIFFS data to ESP32-P4-Nano
echo "Uploading SPIFFS data to ESP32..."

# Check if PlatformIO is available
if ! command -v pio &> /dev/null; then
    echo "Error: PlatformIO CLI not found. Please install PlatformIO."
    exit 1
fi

# Upload filesystem
pio run --target uploadfs

echo "SPIFFS upload complete!"
'''
    
    with open('upload_spiffs.sh', 'w') as f:
        f.write(script_content)
    
    os.chmod('upload_spiffs.sh', 0o755)
    print("Created upload_spiffs.sh script")

def main():
    print("Moya Worklog ESP32 Image Setup")
    print("==============================")
    
    if setup_spiffs_data():
        create_upload_script()
        print("\nSetup complete!")
        print("\nNext steps:")
        print("1. Build and upload the main program:")
        print("   pio run --target upload")
        print("2. Upload the SPIFFS data:")
        print("   ./upload_spiffs.sh")
        print("   or: pio run --target uploadfs")
    else:
        print("Setup failed!")
        sys.exit(1)

if __name__ == '__main__':
    main()