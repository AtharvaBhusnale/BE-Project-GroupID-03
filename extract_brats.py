import os
import h5py
import numpy as np
from PIL import Image
import shutil

# --- CONFIGURATION ---
# 1. Verify this path matches your BraTS folder structure exactly:
SOURCE_DIR = os.path.join('brats_dataset', 'BraTS2020_training_data', 'content', 'data')

# 2. This is where the converted PNGs will go, ready for prepare_data.py
OUTPUT_DIR = os.path.join('brats_dataset', 'converted_images')

def extract_h5_images():
    print(f"Current Working Directory: {os.getcwd()}")
    
    if not os.path.exists(SOURCE_DIR):
        print(f"🔴 Error: Source directory not found at: {SOURCE_DIR}")
        print("Please check that your 'brats_dataset' folder structure matches the code.")
        return

    # Create output folder (clears it first to be safe)
    if os.path.exists(OUTPUT_DIR):
        shutil.rmtree(OUTPUT_DIR)
    os.makedirs(OUTPUT_DIR)

    print(f"Scanning for .h5 files in: {SOURCE_DIR}")
    files = [f for f in os.listdir(SOURCE_DIR) if f.endswith('.h5')]
    
    if not files:
        print("🔴 No .h5 files found! Check the folder path.")
        return

    print(f"Found {len(files)} files. Extracting first 5000...")
    
    count = 0
    limit = 5000
    
    for filename in files:
        if count >= limit:
            break
            
        filepath = os.path.join(SOURCE_DIR, filename)
        
        try:
            with h5py.File(filepath, 'r') as f:
                # Check keys
                keys = list(f.keys())
                
                img_data = None
                mask_data = None
                
                if 'image' in keys: img_data = f['image'][:]
                elif 'data' in keys: img_data = f['data'][:]
                
                if 'mask' in keys: mask_data = f['mask'][:]
                elif 'seg' in keys: mask_data = f['seg'][:]
                
                if img_data is None: continue

                # img_data expected shape: (240, 240, 4) or (4, 240, 240)
                # We want 2D slice.
                
                slice_img = None
                
                if img_data.ndim == 3:
                    if img_data.shape[0] <= 4: # (Channels, H, W)
                        slice_img = img_data[2, :, :] # Channel 2
                    else: # (H, W, Channels)
                        slice_img = img_data[:, :, 2] # Channel 2
                elif img_data.ndim == 2:
                    slice_img = img_data
                
                if slice_img is None: continue
                
                # Mask
                slice_mask = None
                if mask_data is not None:
                    if mask_data.ndim == 3:
                        if mask_data.shape[0] <= 4:
                            slice_mask = mask_data[0, :, :] # Channel 0
                        else:
                            slice_mask = mask_data[:, :, 0]
                    elif mask_data.ndim == 2:
                        slice_mask = mask_data

                # Normalize Image
                slice_img = slice_img.astype(float)
                if np.max(slice_img) > np.min(slice_img): 
                    slice_img = (slice_img - np.min(slice_img)) / (np.max(slice_img) - np.min(slice_img)) * 255.0
                slice_img = slice_img.astype(np.uint8)
                
                # Save Image
                img_pil = Image.fromarray(slice_img)
                output_filename = filename.replace('.h5', '.png')
                img_path = os.path.join(OUTPUT_DIR, output_filename)
                img_pil.save(img_path)
                
                # Save Mask
                if slice_mask is not None:
                     slice_mask = slice_mask.astype(np.uint8)
                     slice_mask[slice_mask > 0] = 255
                     
                     mask_pil = Image.fromarray(slice_mask)
                     mask_filename = filename.replace('.h5', '_mask.png')
                     mask_pil.save(os.path.join(OUTPUT_DIR, mask_filename))
                
                count += 1
                if count % 500 == 0:
                    print(f"Converted {count} pairs...")
                    
        except Exception as e:
            print(f"Error converting {filename}: {e}")

    print(f"✅ Success! Extracted {count} pairs.")

if __name__ == "__main__":
    extract_h5_images()