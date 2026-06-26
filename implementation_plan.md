# Implementation Plan - MRI Image Segmentation

## Goal
Implement image segmentation to highlight brain matter/ventricles using a U-Net model.

## Proposed Changes

### 1. New File: `unet_model.py`
- Define a standard U-Net architecture using PyTorch.
- `UNet(n_channels, n_classes)`

### 2. New File: `segmentation_service.py`
- Class `SegmentationService`
- Method `load_model()`: Loads U-Net weights if available.
- Method `segment(image_path)`:
    - Preprocesses image.
    - Runs inference (if model loaded).
    - Fallback: Uses OpenCV thresholding/contours if model weights are missing (to ensure functionality).
    - Returns path to the saved mask image.

### 3. Update `app.py`
- Import `SegmentationService`.
- Initialize the service.
- Add endpoint `/api/segment_image` (POST).
    - Input: Image file (or reference to uploaded file).
    - Output: JSON with URL to the segmentation mask.

### 4. Update `templates/index.html`
- Add a "Segment Brain" button next to "Enhance".
- Display the segmentation result (overlay or side-by-side).

## Verification Plan
### Automated Tests
- None (Visual verification required).

### Manual Verification
- Upload an MRI image.
- Click "Segment Brain".
- Verify that a mask image is displayed, highlighting the brain area.
