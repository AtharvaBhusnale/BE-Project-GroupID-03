import torch
print(f"Is CUDA available? {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"Device Name: {torch.cuda.get_device_name(0)}")
# ```
# Run this script. If it says `False`, you need to reinstall PyTorch.

# **Step 2: Reinstall PyTorch with CUDA support**
# 1.  Go to the official [PyTorch Get Started page](https://pytorch.org/get-started/locally/).

# 2.  Select your configuration:
#     * **PyTorch Build:** Stable
#     * **Your OS:** Windows
#     * **Package:** Pip
#     * **Language:** Python
#     * **Compute Platform:** CUDA 11.8 or CUDA 12.1 (Choose one that matches your installed drivers, 11.8 is generally very stable).
# 3.  Copy the command it generates. It will look something like this:
#     ```bash
#     pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118