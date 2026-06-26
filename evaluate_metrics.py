import os
import random

import lpips  # For LPIPS
import numpy as np
import torch
from PIL import Image
from skimage.metrics import peak_signal_noise_ratio as psnr
from skimage.metrics import structural_similarity as ssim


def load_image(path):
    """Loads an image and converts it to a NumPy array [0, 255]."""
    img = Image.open(path).convert("RGB")
    return np.array(img)


def np_to_tensor(img_np):
    """
    Converts a NumPy image [H, W, C] to a PyTorch tensor [1, C, H, W]
    and normalizes it to the [-1, 1] range which LPIPS expects.
    """
    img_tensor = torch.from_numpy(img_np).permute(2, 0, 1).float() / 255.0
    img_tensor = (img_tensor * 2.0) - 1.0
    return img_tensor.unsqueeze(0)


def main():
    # --- Configuration ---
    hr_folder = "test_images_hr"  # Ground Truth
    enhanced_folder = os.path.join("test_images_output", "enhanced_result")

    NUM_IMAGES_TO_TEST = 100
    ENHANCED_SUFFIX = "_Enhanced.png"

    # --- Setup ---
    print("Setting up evaluation...")
    psnr_scores = []
    ssim_scores = []
    lpips_scores = []

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "mps"
        if torch.backends.mps.is_available()
        else "cpu"
    )
    print(f"Using device: {device} for LPIPS calculation.")
    lpips_model = lpips.LPIPS(net="vgg").to(device)
    lpips_model.eval()

    try:
        enhanced_files = [
            f for f in os.listdir(enhanced_folder) if f.endswith(ENHANCED_SUFFIX)
        ]
        if len(enhanced_files) == 0:
            raise FileNotFoundError(
                f"No '{ENHANCED_SUFFIX}' files found in '{enhanced_folder}'."
            )

        if len(enhanced_files) < NUM_IMAGES_TO_TEST:
            print(
                f"Warning: Found only {len(enhanced_files)} images. Testing on all available."
            )
            NUM_IMAGES_TO_TEST = len(enhanced_files)

        random.shuffle(enhanced_files)
        test_files = enhanced_files[:NUM_IMAGES_TO_TEST]

    except FileNotFoundError:
        print(f"Error: Could not find the enhanced images folder at: {enhanced_folder}")
        print("Please run 'enhancer_final.py' to generate some images first.")
        return
    except Exception as e:
        print(f"An error occurred: {e}")
        return

    print(f"Starting evaluation on {NUM_IMAGES_TO_TEST} random images...")

    # --- Main Evaluation Loop ---
    for i, filename in enumerate(test_files):
        try:
            # --- Find Matching File Pair ---
            base_name = filename.replace(ENHANCED_SUFFIX, "")
            hr_filename = f"{base_name}_HR.png"

            enhanced_path = os.path.join(enhanced_folder, filename)
            hr_path = os.path.join(hr_folder, hr_filename)

            if not os.path.exists(hr_path):
                print(
                    f"Warning: Skipping {filename}, could not find matching HR file: {hr_filename}"
                )
                continue

            # --- Load Images ---
            img_hr_np = load_image(hr_path)
            img_enhanced_np = load_image(enhanced_path)

            # --- THIS IS THE FIX ---
            # If dimensions don't match, resize the ENHANCED image
            # down to match the HR (Ground Truth) image.
            if img_hr_np.shape != img_enhanced_np.shape:
                print(
                    f"Info: Resizing enhanced image from {img_enhanced_np.shape} to {img_hr_np.shape} for comparison."
                )
                # Convert NumPy array to PIL Image to use resize
                img_enhanced_pil = Image.fromarray(img_enhanced_np)
                # Get target dimensions from HR image
                target_size = (
                    img_hr_np.shape[1],
                    img_hr_np.shape[0],
                )  # (width, height)

                # Resize using high-quality anti-aliasing
                img_enhanced_pil_resized = img_enhanced_pil.resize(
                    target_size, Image.LANCZOS
                )

                # Convert back to NumPy array for metrics
                img_enhanced_np = np.array(img_enhanced_pil_resized)
            # --- END OF FIX ---

            # --- Calculate PSNR & SSIM (using scikit-image on NumPy arrays) ---
            current_psnr = psnr(img_hr_np, img_enhanced_np, data_range=255)
            current_ssim = ssim(
                img_hr_np, img_enhanced_np, data_range=255, channel_axis=-1, win_size=7
            )

            psnr_scores.append(current_psnr)
            ssim_scores.append(current_ssim)

            # --- Calculate LPIPS (using lpips on PyTorch tensors) ---
            img_hr_t = np_to_tensor(img_hr_np).to(device)
            img_enhanced_t = np_to_tensor(img_enhanced_np).to(
                device
            )  # Use the (now resized) numpy array

            with torch.no_grad():
                current_lpips = lpips_model(img_hr_t, img_enhanced_t).item()

            lpips_scores.append(current_lpips)

            print(
                f"({i + 1}/{NUM_IMAGES_TO_TEST}) {filename} - PSNR: {current_psnr:.2f}, SSIM: {current_ssim:.4f}, LPIPS: {current_lpips:.4f}"
            )

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # --- Print Final Results ---
    print("\n--- Evaluation Complete ---")
    if psnr_scores:
        print(f"Average PSNR: {np.mean(psnr_scores):.2f} dB  (Higher is better)")
        print(
            f"Average SSIM: {np.mean(ssim_scores):.4f}      (Higher is better, 1.0 is perfect)"
        )
        print(
            f"Average LPIPS: {np.mean(lpips_scores):.4f}     (Lower is better, 0 is perfect)"
        )
    else:
        print("No images were successfully processed.")


if __name__ == "__main__":
    main()
