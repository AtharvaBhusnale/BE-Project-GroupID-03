import os
import torch
import tempfile
from PIL import Image
import numpy as np
from unet_model import UNet
from train_unet import BrainDataset
import unittest

class TestMLPipeline(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.data_dir = self.temp_dir.name
        
        # ML-01 setup: Create dummy image and mask
        self.img_name = "test_image.png"
        self.mask_name = "test_image_mask.png"
        
        # Create 64x64 dummy image and mask
        self.H, self.W = 128, 128
        
        # Random image for ML-02 normalization test
        img_np = np.random.randint(0, 256, (self.H, self.W), dtype=np.uint8)
        mask_np = np.random.randint(0, 2, (self.H, self.W), dtype=np.uint8) * 255
        
        Image.fromarray(img_np).save(os.path.join(self.data_dir, self.img_name))
        Image.fromarray(mask_np).save(os.path.join(self.data_dir, self.mask_name))
        
        self.dataset = BrainDataset(self.data_dir)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_ml_01_dataset_pairing(self):
        """
        ML-01: Verify dataset pairs images with correct masks
        Expected Output: getitem returns a tuple where the mask filename exactly matches the image filename base.
        """
        # Verify dataset found 1 image and it's not the mask
        self.assertEqual(len(self.dataset), 1)
        
        img_path = self.dataset.images[0]
        self.assertTrue(img_path.endswith(self.img_name))
        
        # Test getitem returns 2 tensors
        img_tensor, mask_tensor = self.dataset[0]
        
        self.assertIsInstance(img_tensor, torch.Tensor)
        self.assertIsInstance(mask_tensor, torch.Tensor)
        
        # Verify the mask file corresponding to the image base has been paired correctly
        # mask is saved with "_mask.png" 
        expected_mask_path = img_path.replace(".png", "_mask.png")
        self.assertTrue(os.path.exists(expected_mask_path))

    def test_ml_02_tensor_shapes_and_normalization(self):
        """
        ML-02: Verify tensor shapes and normalization
        Expected Output: Image tensor is shape (1, H, W) and values are normalized between [0.0, 1.0].
        """
        img_tensor, mask_tensor = self.dataset[0]
        
        # Shape: (1, H, W)
        self.assertEqual(img_tensor.shape, (1, self.H, self.W))
        self.assertEqual(mask_tensor.shape, (1, self.H, self.W))
        
        # Normalization [0.0, 1.0]
        self.assertTrue(torch.min(img_tensor) >= 0.0)
        self.assertTrue(torch.max(img_tensor) <= 1.0)
        
    def test_ml_03_model_forward_pass(self):
        """
        ML-03: Verify model forward pass handles correct input shapes
        Expected Output: Model returns an output tensor of identical shape (Batch, 1, H, W) without crashing.
        """
        model = UNet(n_channels=1, n_classes=1)
        batch_size = 2
        
        # Input tensor (Batch, 1, H, W)
        input_tensor = torch.randn(batch_size, 1, self.H, self.W)
        
        try:
            output_tensor = model(input_tensor)
        except Exception as e:
            self.fail(f"Model forward pass crashed with exception: {e}")
            
        self.assertEqual(output_tensor.shape, input_tensor.shape)

    def test_ml_04_metric_calculation_dice_score(self):
        """
        ML-04: Verify metric calculation (Dice Score)
        Expected Output: Dice score is correctly calculated between 0.0 (no overlap) and 1.0 (perfect overlap).
        """
        from train_unet import calculate_dice_score
        
        target_mask = torch.zeros(2, 1, 64, 64)
        target_mask[:, :, 10:50, 10:50] = 1.0
        
        # Perfect prediction logit
        perfect_pred_logits = torch.ones(2, 1, 64, 64) * -10.0
        perfect_pred_logits[:, :, 10:50, 10:50] = 10.0
        
        dice_perfect = calculate_dice_score(perfect_pred_logits, target_mask)
        self.assertAlmostEqual(dice_perfect.item(), 1.0, places=4)
        
        # Bad prediction logit
        bad_pred_logits = torch.ones(2, 1, 64, 64) * -10.0
        bad_pred_logits[:, :, 55:60, 55:60] = 10.0
        
        dice_bad = calculate_dice_score(bad_pred_logits, target_mask)
        self.assertAlmostEqual(dice_bad.item(), 0.0, places=4)

    def test_ml_05_model_checkpoint_saving(self):
        """
        ML-05: Verify model checkpoint saving
        Expected Output: A unet_brain.pth file is successfully saved to the weights/ directory.
        """
        model = UNet(n_channels=1, n_classes=1)
        save_path = os.path.join(self.temp_dir.name, "weights", "unet_brain.pth")
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        torch.save(model.state_dict(), save_path)
        
        self.assertTrue(os.path.exists(save_path))
        self.assertTrue(os.path.isfile(save_path))

if __name__ == '__main__':
    unittest.main()
