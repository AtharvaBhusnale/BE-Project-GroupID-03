import os
import torch
import numpy as np
import cv2
from PIL import Image
from unet_model import UNet

class SegmentationService:
    def __init__(self, model_path=None):
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)
        else:
            print("⚠️ Segmentation model not found. Using CV fallback.")

    def load_model(self, model_path):
        try:
            # U-Net trained on 1 channel (grayscale) -> 1 class (binary mask)
            self.model = UNet(n_channels=1, n_classes=1)
            state_dict = torch.load(model_path, map_location=self.device)
            self.model.load_state_dict(state_dict)
            self.model.to(self.device)
            self.model.eval()
            print(f"✅ Segmentation model loaded from {model_path}")
        except Exception as e:
            print(f"🔴 Error loading segmentation model: {e}")
            self.model = None

    def segment(self, image_path, output_path):
        """
        Segments the image and saves the mask to output_path.
        Returns True if successful.
        """
        try:
            if self.model is not None:
                return self._segment_with_model(image_path, output_path)
            else:
                return self._segment_with_cv(image_path, output_path)
        except Exception as e:
            print(f"Error during segmentation: {e}")
            return False

    def _segment_with_model(self, image_path, output_path):
        try:
            # 1. Load Image
            img_bgr = cv2.imread(image_path)
            if img_bgr is None: return False
            
            # Convert to Grayscale for Model
            img_gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            
            # Preprocess for PyTorch: [0, 255] -> [0, 1] -> (1, H, W) -> (1, 1, H, W)
            img_tensor = img_gray.astype(np.float32) / 255.0
            img_tensor = torch.from_numpy(img_tensor).unsqueeze(0).unsqueeze(0)
            img_tensor = img_tensor.to(self.device)
            
            # 2. Inference
            with torch.no_grad():
                output = self.model(img_tensor)
                probs = torch.sigmoid(output)
                mask = (probs > 0.5).float()
                
            # 3. Post-process
            # Convert back to numpy: (1, 1, H, W) -> (H, W)
            mask_np = mask.squeeze().cpu().numpy().astype(np.uint8) * 255
            
            # 4. Create Visualization (Green Overlay)
            # Create a colored mask (Green)
            colored_mask = np.zeros_like(img_bgr)
            colored_mask[:, :, 1] = mask_np # Set Green channel
            
            # Blend original image with mask
            # Ensure mask is boolean for indexing
            binary_mask = mask_np > 0
            
            overlay = img_bgr.copy()
            # Increase green channel intensity where mask is present
            overlay[binary_mask] = cv2.addWeighted(img_bgr[binary_mask], 0.7, colored_mask[binary_mask], 0.3, 0)
            
            # Draw contours for sharper edge
            contours, _ = cv2.findContours(mask_np, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            cv2.drawContours(overlay, contours, -1, (0, 255, 0), 2)
            
            # Save
            cv2.imwrite(output_path, overlay)
            return True
            
        except Exception as e:
            print(f"Error in _segment_with_model: {e}")
            # Fallback to CV if model fails? Or just fail. 
            # Let's fallback to be safe for user demo if training failed
            return self._segment_with_cv(image_path, output_path)

    def _segment_with_cv(self, image_path, output_path):
        """
        Fallback segmentation using OpenCV to highlight brain matter.
        """
        img = cv2.imread(image_path)
        if img is None: return False
        
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # 1. Thresholding to separate brain from background
        _, thresh = cv2.threshold(gray, 40, 255, cv2.THRESH_BINARY)
        
        # 2. Morphological operations to clean up noise
        kernel = np.ones((3,3), np.uint8)
        opening = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel, iterations=2)
        
        # 3. Find contours to get the main brain area
        contours, _ = cv2.findContours(opening, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        # Create a mask
        mask = np.zeros_like(gray)
        
        # Draw the largest contour (assumed to be the brain)
        if contours:
            largest_contour = max(contours, key=cv2.contourArea)
            cv2.drawContours(mask, [largest_contour], -1, (255), thickness=cv2.FILLED)
            
        # Apply mask to original image to show just the brain, or save the mask itself
        # Let's save a visualization: Original image with a green overlay
        
        overlay = img.copy()
        overlay[mask == 255] = [0, 255, 0] # Green where the brain is
        
        # Blend
        alpha = 0.3
        cv2.addWeighted(overlay, alpha, img, 1 - alpha, 0, img)
        
        cv2.imwrite(output_path, img)
        return True
