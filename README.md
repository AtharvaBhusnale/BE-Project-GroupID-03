# MRI_Enhancer
# BE-Project-GroupID-03

### 1. Prerequisites
Before setting up the project, make sure you have the following installed:
*   **Git** & **Git LFS** (Git Large File Storage) — *Crucial because model weights (`.pth` files) are stored via Git LFS.*
*   **Python 3.10** (Recommended)
*   A **Firebase Project** (with Authentication and Firestore Database enabled)
*   A **Groq API Key** (Get one for free at [console.groq.com](https://console.groq.com/keys))

---

### 2. Clone the Repository & Pull Large Files
First, clone the repository and fetch the large PyTorch model weights via Git LFS:

```bash
# 1. Initialize Git LFS on your machine (if not already done)
git lfs install

# 2. Clone the repository
git clone https://github.com/AtharvaBhusnale/BE-Project-GroupID-03.git
cd BE-Project-GroupID-03

# 3. Pull the model weights (.pth files)
git lfs pull
```

---

### 3. Create a Virtual Environment & Install Dependencies
Set up a virtual environment and install the required Python packages from [requirements.txt](file:///e:/MRI%20Enhancement/requirements.txt):

**On Windows:**
```powershell
python -m venv vr_env_310
.\vr_env_310\Scripts\activate
pip install -r requirements.txt
```

**On macOS / Linux:**
```bash
python3 -m venv vr_env_310
source vr_env_310/bin/activate
pip install -r requirements.txt
```

#### *(Optional) Set Up CUDA/GPU Acceleration:*
The project uses PyTorch models for MRI enhancement and segmentation. If you have an NVIDIA GPU, you can verify if CUDA is enabled by running [check_cuda.py](file:///e:/MRI%20Enhancement/check_cuda.py):
```bash
python check_cuda.py
```
If it returns `False`, you can reinstall PyTorch with CUDA support:
```bash
# For CUDA 11.8:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# For CUDA 12.1:
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
```

---

### 4. Configuration
You will need to set up two configuration files in the project root:

1.  **Firebase Credentials**:
    *   Go to your [Firebase Console](https://console.firebase.google.com/).
    *   Navigate to **Project Settings** > **Service Accounts**.
    *   Click **Generate new private key** and save the downloaded JSON file in the project's root folder as **`serviceAccountKey.json`**.
2.  **Environment Variables**:
    *   Create a file named **`.env`** in the project's root folder.
    *   Add your Groq API Key:
        ```env
        GROQ_API_KEY=your_groq_api_key_here
        ```

---

### 5. Initialize the Database (Test Doctor Account)
Run the [setup_doctor.py](file:///e:/MRI%20Enhancement/setup_doctor.py) script to seed a test doctor account in your Firebase Auth and Firestore:
```bash
python setup_doctor.py
```
*(By default, this creates a doctor with email `atharvaabhusnale@gmail.com` and password `Atharva@10`.)*

---

### 6. Run the Application
Start the Flask development server by running [app.py](file:///e:/MRI%20Enhancement/app.py):
```bash
python app.py
```
Once started, open your web browser and go to `http://127.0.0.1:5000` to access the application.
