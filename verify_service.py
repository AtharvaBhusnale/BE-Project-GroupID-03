
import os
from segmentation_service import SegmentationService
import cv2

# Use one of the extracted images
TEST_IMG = os.path.join('brats_dataset', 'converted_images', 'volume_100_slice_100.png')
OUTPUT_IMG = os.path.join('test_segmentation_output.png')
MODEL_PATH = os.path.join('weights', 'unet_brain.pth')

def test_service():
    if not os.path.exists(TEST_IMG):
        print(f"Test image not found: {TEST_IMG}")
        return

    print("Initializing Segmentation Service...")
    service = SegmentationService(model_path=MODEL_PATH)
    
    if service.model is None:
        print("FAILED: Model did not load.")
        return

    print(f"Segmenting {TEST_IMG}...")
    success = service.segment(TEST_IMG, OUTPUT_IMG)
    
    if success:
        print(f"✅ Segmentation successful! Output saved to {OUTPUT_IMG}")
        # Check if output exists
        if os.path.exists(OUTPUT_IMG):
            print("Output file exists.")
    else:
        print("FAILED: Segmentation returned False.")

if __name__ == "__main__":
    test_service()
