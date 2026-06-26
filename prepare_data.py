import os
import shutil
from PIL import Image

def prepare_dataset(dataset_folders, hr_dir, lr_dir, scale_factor=4):
    """
    Recursively finds images in multiple source directories,
    converts them into high-res (HR) .png ground truth files,
    and creates matching low-res (LR) .png test inputs.
    """
    
    # Ensure output directories exist
    os.makedirs(hr_dir, exist_ok=True)
    os.makedirs(lr_dir, exist_ok=True)
    
    print(f"Starting dataset preparation (Scale Factor: 1/{scale_factor})...")
    
    total_processed = 0

    # Loop through each dataset folder provided in the list
    for source_base_dir in dataset_folders:
        print(f"\nScanning folder: {source_base_dir} ...")
        
        if not os.path.exists(source_base_dir):
            print(f"⚠️ Warning: Folder '{source_base_dir}' not found. Skipping.")
            continue

        # os.walk will go through every subfolder
        for root, _, files in os.walk(source_base_dir):
            for filename in files:
                # Check for common image formats
                if filename.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp', '.gif')):
                    try:
                        source_path = os.path.join(root, filename)
                        
                        with Image.open(source_path) as img:
                            # Convert to 'RGB' to ensure 3 channels for the model
                            hr_image = img.convert('RGB')
                            
                            # --- Create Unique Filename ---
                            # Use folder name as prefix to avoid collisions
                            rel_path = os.path.relpath(root, start=source_base_dir)
                            if rel_path == ".":
                                dataset_prefix = os.path.basename(source_base_dir)
                            else:
                                # Replace path separators (/) with underscores (_)
                                dataset_prefix = f"{os.path.basename(source_base_dir)}_{rel_path.replace(os.sep, '_')}"
                            
                            clean_name = os.path.splitext(filename)[0]
                            unique_name = f"{dataset_prefix}_{clean_name}"
                            
                            # --- Create the High-Res Ground Truth ---
                            hr_filename = f"{unique_name}_HR.png"
                            hr_path = os.path.join(hr_dir, hr_filename)
                            hr_image.save(hr_path)
                            
                            # --- Create the Low-Res Test Input (Downscaling) ---
                            # Calculate new dimensions
                            lr_width = hr_image.width // scale_factor
                            lr_height = hr_image.height // scale_factor
                            
                            # Resize using high-quality Lanczos resampling
                            lr_image = hr_image.resize((lr_width, lr_height), Image.LANCZOS)
                            
                            # Save the LR image
                            lr_filename = f"{unique_name}_LR_x{scale_factor}.png"
                            lr_path = os.path.join(lr_dir, lr_filename)
                            
                            # --- FIX IS HERE: Use lr_path, not lr_image ---
                            lr_image.save(lr_path) 
                            
                        total_processed += 1
                        
                        if total_processed % 500 == 0:
                            print(f"Processed {total_processed} images...")

                    except Exception as e:
                        print(f"Failed to process {filename}: {e}")
    
    print(f"\n✅ Preparation complete. Total images processed: {total_processed}")
    print(f"HR images are in: '{hr_dir}'")
    print(f"LR images are in: '{lr_dir}'")

if __name__ == '__main__':
    # --- 1. DEFINE YOUR DATASET FOLDERS HERE ---
    DATASET_FOLDERS = [
        os.path.join('oasis_original_gifs', 'Data'),        # OASIS (Alzheimer's)
        'brain_tumor_dataset',                              # Figshare (General Tumors)
        os.path.join('brats_dataset', 'converted_images'),  # BraTS 2020 (Converted PNGs from H5)
    ]
    
    HR_FOLDER = 'test_images_hr' 
    LR_FOLDER = 'test_images_lr' 
    
    SCALE_FACTOR = 2 
    
    # Clear old folders to start fresh
    print("Clearing old test image folders...")
    for folder in [HR_FOLDER, LR_FOLDER]:
        if os.path.exists(folder):
            shutil.rmtree(folder)
            os.makedirs(folder)
    print("Old test images cleared. Creating new folders...")
    
    # Run the preparation function
    prepare_dataset(DATASET_FOLDERS, HR_FOLDER, LR_FOLDER, scale_factor=SCALE_FACTOR)