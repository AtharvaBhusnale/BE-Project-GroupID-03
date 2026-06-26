import os
import torch
from PIL import Image
import numpy as np
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
import random
import shutil

def enhance_image(model_path, input_path, output_path, scale=4):
    """Enhances a low-resolution image using a pre-trained Real-ESRGAN model."""
    print("Setting up the Real-ESRGAN model...")

    # Determine the device to use (GPU if available, otherwise CPU)
    if torch.cuda.is_available():
        device = torch.device('cuda')
    elif torch.backends.mps.is_available(): 
        device = torch.device('mps')
    else:
        device = torch.device('cpu')
    
    print(f"Using device: {device}")

    # Define the model architecture (RRDBNet is the architecture used by Real-ESRGAN)
    model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=scale)

    # Set up the upsampler object which handles the file loading and processing
    upsampler = RealESRGANer(
        scale=scale,
        model_path=model_path,
        model=model,
        dni_weight=None, tile=0, tile_pad=10, pre_pad=0, half=False, device=device
    )

    print(f"Loading image from: {input_path}")
    try:
        # Load image and convert to NumPy array (RGB format is necessary)
        img = Image.open(input_path).convert('RGB')
        img_np = np.array(img)
        print(f"  -> Original dimensions: {img.width}x{img.height}")
        
    except FileNotFoundError:
        print(f"Error: Input image not found at {input_path}")
        return
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    print("Enhancing image... This may take a moment.")
    try:
        # Run the enhancement model (this is the core AI step)
        output_np, _ = upsampler.enhance(img_np, outscale=scale)
        
        # Convert the high-resolution array back to a PIL Image
        output_img = Image.fromarray(output_np)
        print(f"  -> Enhanced dimensions: {output_img.width}x{output_img.height}")
        
        output_img.save(output_path)
        print(f"Successfully saved enhanced image to: {output_path}")

    except Exception as e:
        print(f"An error occurred during the enhancement process: {e}")

if __name__ == '__main__':
    # --- Define Paths ---
    model_file = os.path.join('weights', 'RealESRGAN_x4plus.pth')
    lr_folder = 'test_images_lr'
    hr_folder = 'test_images_hr'  
    
    output_folder_base = 'test_images_output'
    output_folder_hr = os.path.join(output_folder_base, 'original_ground_truth')
    output_folder_enhanced = os.path.join(output_folder_base, 'enhanced_result')
    
    os.makedirs(output_folder_hr, exist_ok=True)
    os.makedirs(output_folder_enhanced, exist_ok=True)

    # --- Select a Random Low-Res Image ---
    try:
        scale_factor = 2 # Assumes inputs were scaled down by 2x in prepare_data.py
        suffix = f'_LR_x{scale_factor}.png'
        
        # Get list of files ending in the correct suffix
        all_lr_images = [f for f in os.listdir(lr_folder) if f.lower().endswith(suffix.lower())]

        if not all_lr_images:
            raise IndexError(f"No files ending in '{suffix}' found in '{lr_folder}'.")
        
        random_lr_image_name = random.choice(all_lr_images)
        input_file_lr = os.path.join(lr_folder, random_lr_image_name)
        
        print(f"Randomly selected image: {random_lr_image_name}")

    except (FileNotFoundError, IndexError) as e:
        print(f"Error: {e}")
        print("Please run 'prepare_data.py' first.")
        exit()
        
    # --- Find Matching High-Res Image (Ground Truth) ---
    try:
        # Remove the '_LR_x2.png' suffix to find the original base name
        index = random_lr_image_name.lower().find(suffix.lower())
        if index != -1:
            base_name = random_lr_image_name[:index]
        else:
            base_name = random_lr_image_name.replace(suffix, '')

        hr_filename = f"{base_name}_HR.png"
        input_file_hr = os.path.join(hr_folder, hr_filename)
        
        if not os.path.exists(input_file_hr):
            raise FileNotFoundError(f"Matching HR file not found at: {input_file_hr}")
            
    except Exception as e:
        print(f"Error finding matching HR file: {e}")
        exit()

    # --- Run Enhancement & Comparison ---
    output_file_enhanced = os.path.join(output_folder_enhanced, f"{base_name}_Enhanced.png")
    output_file_hr_copy = os.path.join(output_folder_hr, hr_filename) 

    try:
        # Copy original HR file to the output folder for comparison
        shutil.copyfile(input_file_hr, output_file_hr_copy)
        print(f"Copied original HR image to: {output_file_hr_copy}")
    except Exception as e:
        print(f"Error copying original HR file: {e}")
        exit()
        
    if not os.path.exists(model_file):
        print(f"Error: Model file not found at '{model_file}'.")
    else:
        enhance_image(model_path=model_file, input_path=input_file_lr, output_path=output_file_enhanced)
        print(f"\nComparison files are ready in '{output_folder_base}'.")