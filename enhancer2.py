import os
import torch
from PIL import Image
import numpy as np
from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
import random  # <-- Import the random module


def enhance_image(model_path, input_path, output_path, scale=4):
    """
    Enhances a low-resolution image using a pre-trained Real-ESRGAN model.
    """
    print("Setting up the Real-ESRGAN model...")

    # Determine the device to use (GPU if available, otherwise CPU)
    if torch.cuda.is_available():
        device = torch.device("cuda")
    elif torch.backends.mps.is_available():  # For Apple Silicon
        device = torch.device("mps")
    else:
        device = torch.device("cpu")

    print(f"Using device: {device}")

    # Define the model architecture (x4 model)
    model = RRDBNet(
        num_in_ch=3,
        num_out_ch=3,
        num_feat=64,
        num_block=23,
        num_grow_ch=32,
        scale=scale,
    )

    # Set up the upsampler
    upsampler = RealESRGANer(
        scale=scale,
        model_path=model_path,
        model=model,
        dni_weight=None,
        tile=0,
        tile_pad=10,
        pre_pad=0,
        half=False,  # Set to True for faster GPU inference if you have enough VRAM
        device=device,
    )

    print(f"Loading image from: {input_path}")
    try:
        # Open the input image
        img = Image.open(input_path).convert("RGB")
        img_np = np.array(img)
    except FileNotFoundError:
        print(f"Error: Input image not found at {input_path}")
        return
    except Exception as e:
        print(f"Error loading image: {e}")
        return

    print("Enhancing image... This may take a moment.")
    try:
        # Use the upsampler to enhance the image
        output_np, _ = upsampler.enhance(img_np, outscale=scale)

        # Convert the output from a numpy array back to a PIL image
        output_img = Image.fromarray(output_np)

        # Save the enhanced image
        output_img.save(output_path)
        print(f"Successfully saved enhanced image to: {output_path}")

    except Exception as e:
        print(f"An error occurred during the enhancement process: {e}")


if __name__ == "__main__":
    # --- Define File Paths ---

    # 1. Model Path
    model_file = os.path.join("weights", "RealESRGAN_x4plus.pth")

    # 2. Input Path (Pick a RANDOM image from the lr folder)
    lr_folder = "test_images_lr"
    try:
        # Get all files and filter for valid image extensions
        all_lr_images = [
            f
            for f in os.listdir(lr_folder)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]

        if not all_lr_images:
            raise IndexError("No valid image files found.")

        # Select a random image from the list
        random_lr_image = random.choice(all_lr_images)
        input_file = os.path.join(lr_folder, random_lr_image)
        print(f"Randomly selected image: {random_lr_image}")

    except (FileNotFoundError, IndexError):
        print(f"Error: No images found in '{lr_folder}'.")
        print("Please run 'prepare_data.py' first.")
        exit()

    # 3. Output Path
    #    Let's create a new folder for our results
    output_folder = "test_images_output"
    os.makedirs(output_folder, exist_ok=True)

    # Create a matching output name, ensuring it's a .png
    output_filename = f"result_{os.path.splitext(random_lr_image)[0]}.png"
    output_file = os.path.join(output_folder, output_filename)

    # --- Run the Enhancement ---
    if not os.path.exists(model_file):
        print(f"Error: Model file not found at '{model_file}'.")
    else:
        enhance_image(
            model_path=model_file, input_path=input_file, output_path=output_file
        )
