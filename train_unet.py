
import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from PIL import Image
import numpy as np
from unet_model import UNet
import glob

# Configuration
DATA_DIR = os.path.join('brats_dataset', 'converted_images')
MODEL_SAVE_PATH = os.path.join('weights', 'unet_brain.pth')
BATCH_SIZE = 8
EPOCHS = 30
LEARNING_RATE = 1e-4
DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

class BrainDataset(Dataset):
    def __init__(self, data_dir):
        self.data_dir = data_dir
        # Find all images that are NOT masks
        all_files = glob.glob(os.path.join(data_dir, "*.png"))
        self.images = [f for f in all_files if "_mask.png" not in f]
        print(f"Dataset found {len(self.images)} images.")

    def __len__(self):
        return len(self.images)

    def __getitem__(self, idx):
        img_path = self.images[idx]
        # Construct mask path: name.png -> name_mask.png
        # Note: glob returns absolute/relative paths depending on input. 
        # Our naming convention: volume_x_slice_y.png -> volume_x_slice_y_mask.png
        mask_path = img_path.replace(".png", "_mask.png")
        
        # Load Image
        image = Image.open(img_path).convert("L") # Grayscale
        img_np = np.array(image, dtype=np.float32)
        
        # Normalize to [0, 1]
        img_np = img_np / 255.0
        
        # Add Channel dimension: (H, W) -> (1, H, W)
        img_tensor = torch.from_numpy(img_np).unsqueeze(0)

        # Load Mask
        mask_tensor = torch.zeros((1, img_np.shape[0], img_np.shape[1]), dtype=torch.float32)
        if os.path.exists(mask_path):
            mask = Image.open(mask_path).convert("L")
            mask_np = np.array(mask, dtype=np.float32)
            # Threshold just in case
            mask_np = (mask_np > 127).astype(np.float32)
            mask_tensor = torch.from_numpy(mask_np).unsqueeze(0)
            
        return img_tensor, mask_tensor

def calculate_dice_score(pred, target, smooth=1e-6):
    """
    Calculates the Dice Coefficient for model evaluation.
    Expected to return between 0.0 and 1.0.
    """
    pred = torch.sigmoid(pred)
    pred_binary = (pred > 0.5).float()
    intersection = (pred_binary * target).sum(dim=(1, 2, 3))
    union = pred_binary.sum(dim=(1, 2, 3)) + target.sum(dim=(1, 2, 3))
    dice = (2. * intersection + smooth) / (union + smooth)
    return dice.mean()

import argparse

def train_model():
    parser = argparse.ArgumentParser()
    parser.add_argument('--quick', action='store_true', help='Train on a small subset for debugging')
    args = parser.parse_args()

    # 1. Create Weights Directory
    os.makedirs(os.path.dirname(MODEL_SAVE_PATH), exist_ok=True)

    # 2. Prepare Data
    dataset = BrainDataset(DATA_DIR)
    if len(dataset) == 0:
        print("🔴 No images found! Check your data extraction.")
        return
    
    if args.quick:
        print("⚡ Quick mode enabled: Using only 200 images.")
        dataset.images = dataset.images[:200]
        
    loader = DataLoader(dataset, batch_size=BATCH_SIZE, shuffle=True)

    # 3. Initialize Model
    # n_channels=1 (Grayscale input), n_classes=1 (Binary output)
    model = UNet(n_channels=1, n_classes=1).to(DEVICE)
    
    # Masks are mostly 0s (background), so the model quickly learns to predict 0 everywhere.
    # We heavily weight the positive class (the tumor). An estimated weight of 50.0 is a good start.
    pos_weight = torch.tensor([50.0]).to(DEVICE)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)
    optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

    print(f"Starting training on {DEVICE} for {EPOCHS} epochs...")

    # 4. Training Loop
    for epoch in range(EPOCHS):
        model.train()
        train_loss = 0
        
        for batch_idx, (images, masks) in enumerate(loader):
            images = images.to(DEVICE)
            masks = masks.to(DEVICE)
            
            optimizer.zero_grad()
            outputs = model(images)
            loss = criterion(outputs, masks)
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            
            if batch_idx % 10 == 0:
                print(f"Epoch {epoch+1}/{EPOCHS} [{batch_idx*len(images)}/{len(dataset)}] Loss: {loss.item():.4f}")
        
        avg_loss = train_loss / len(loader)
        print(f"Epoch {epoch+1} Complete. Average Loss: {avg_loss:.4f}")
        
        # Save checkpoint
        torch.save(model.state_dict(), MODEL_SAVE_PATH)
        print(f"Saved model to {MODEL_SAVE_PATH}")

    print("✅ Training Complete!")

if __name__ == "__main__":
    train_model()
