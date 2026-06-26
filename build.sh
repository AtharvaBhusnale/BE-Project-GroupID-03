#!/usr/bin/env bash
# exit on error
set -o errexit

echo "🚀 Upgrading pip, setuptools, and wheel..."
pip install --upgrade pip setuptools wheel

echo "🚀 Pre-installing PyTorch and torchvision (CPU-only)..."
pip install torch==2.9.1 torchvision==0.24.1 --extra-index-url https://download.pytorch.org/whl/cpu

echo "🚀 Installing remaining requirements from requirements.txt..."
pip install -r requirements.txt

echo "✅ Build completed successfully!"
