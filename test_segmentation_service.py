import os
import unittest
import sys
from io import StringIO
import tempfile
import cv2
import numpy as np
import torch

from segmentation_service import SegmentationService
from unet_model import UNet

class TestSegmentationService(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dummy_image_path = os.path.join(self.temp_dir.name, "dummy.png")
        self.dummy_output_path = os.path.join(self.temp_dir.name, "output.png")
        
        # Create a dummy image for testing CV fallback
        img = np.zeros((100, 100, 3), dtype=np.uint8)
        cv2.imwrite(self.dummy_image_path, img)
        
    def tearDown(self):
        self.temp_dir.cleanup()

    def test_ut_01_fallback_missing_model(self):
        """
        UT-01: Verify graceful fallback if model file is missing
        Preconditions: Initialize service with invalid model_path
        Expected Output: Service prints warning, self.model is None, and it falls back to OpenCV method.
        """
        invalid_path = "non_existent_model.pth"
        
        # Capture stdout to verify print statement
        captured_output = StringIO()
        sys.stdout = captured_output
        
        service = SegmentationService(model_path=invalid_path)
        
        sys.stdout = sys.__stdout__ # Reset redirect
        
        # Verify Warning (checking for the fallback part of the string)
        self.assertIn("Segmentation model not found. Using CV fallback.", captured_output.getvalue())
        
        # Verify self.model is None
        self.assertIsNone(service.model)
        
        # Verify fallback to OpenCV method
        # If segment() runs successfully without self.model, it must have used OpenCV
        result = service.segment(self.dummy_image_path, self.dummy_output_path)
        self.assertTrue(result)
        self.assertTrue(os.path.exists(self.dummy_output_path))

    def test_ut_02_successful_model_loading(self):
        """
        UT-02: Verify successful model loading
        Preconditions: Initialize service with valid unet_brain.pth
        Expected Output: self.model is loaded and set to .eval() mode.
        """
        valid_model_path = os.path.join("weights", "unet_brain.pth")
        
        # Ensure a real/mock model file exists for this test to be robust
        if not os.path.exists(valid_model_path):
            os.makedirs("weights", exist_ok=True)
            model = UNet(n_channels=1, n_classes=1)
            torch.save(model.state_dict(), valid_model_path)
            
        service = SegmentationService(model_path=valid_model_path)
        
        # Verify model successfully loaded (not None)
        self.assertIsNotNone(service.model)
        
        # Verify the model is an instance of the loaded U-Net
        self.assertIsInstance(service.model, UNet)
        
        # Verify the model is in .eval() mode (training attribute will be False)
        self.assertFalse(service.model.training)

if __name__ == '__main__':
    unittest.main()
