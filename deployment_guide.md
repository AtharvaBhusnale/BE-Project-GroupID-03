# Deployment Guide: MRI Enhancement & Segmentation

This guide walks you through deploying your Flask application to run **24/7 in the cloud** without using Docker, by connecting a GitHub repository directly to **Render** or **Railway**.

---

## Prerequisites & Architecture Details

1. **Production Server**: We use `waitress` (already installed via `requirements.txt`) as the production WSGI server. It is lightweight, production-ready, and works on both Linux and Windows.
2. **Secrets Security**: You must **never** commit your `.env` or `serviceAccountKey.json` to GitHub. The code has been updated to load the Firebase credentials and API keys directly from environment variables.
3. **Large Model Weights**:
   - `RealESRGAN_x4plus.pth` (67MB) is automatically downloaded from its official release URL at startup if it is missing.
   - `unet_brain.pth` (124MB) exceeds GitHub's file size limit (100MB). You should host it as a **GitHub Release Asset** (explained in Step 1) and configure the app to download it at startup.

---

## Step 1: Host Your U-Net Weights File

Since the `unet_brain.pth` file is too large for standard GitHub pushes (GitHub blocks files larger than 100MB), you should upload it to get a **direct download link**. We will use **GitHub Releases** (100% free and supports files up to 2GB):

### Step 1a: Create a GitHub Release
1. Make sure you complete **Step 2** (Pushing your code to GitHub) first.
2. Go to your repository page on GitHub.
3. On the right-hand sidebar, find and click on **Releases** (or click "Create a new release").
4. Choose a tag name (e.g., `v1.0.0`) and enter a title (e.g., `Model Weights`).
5. Scroll down to the files section (labeled **Attach binaries by dropping them here...**).
6. Drag and drop your local `weights/unet_brain.pth` file here.
7. Click **Publish release**.

### Step 1b: Get the Direct Download URL
1. Once published, you will see your release page.
2. Look under the **Assets** section for the `unet_brain.pth` file.
3. Right-click on `unet_brain.pth` and select **Copy Link Address** (or **Copy Link**).
4. Save this URL. It will look like:
   `https://github.com/YOUR_USERNAME/YOUR_REPO_NAME/releases/download/v1.0.0/unet_brain.pth`
5. You will paste this URL as the `UNET_MODEL_URL` environment variable in Step 3.

---

## Step 2: Push Your Code to GitHub

1. Create a new repository on [GitHub](https://github.com/) (Private is recommended to protect your custom code).
2. Open your terminal in the `e:\MRI Enhancement` directory and run the following commands to initialize and push:
   ```bash
   git init
   git add .
   git commit -m "Configure deployment and auto-weights download"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
   git push -u origin main
   ```
   *(Note: The `.gitignore` file will automatically prevent your weights, virtual environments, local uploads, and credentials from uploading.)*

---

## Step 3: Deploying the Application

Choose either **Render** or **Railway** to host your application 24/7.

### Option A: Deploy on Render.com (Recommended & Free Tier)

1. Sign up/Log in to [Render](https://render.com/).
2. Click **New +** and select **Web Service**.
3. Connect your GitHub account and select your repository.
4. Configure the settings:
   - **Name**: `mri-enhancement-service` (or any name)
   - **Region**: Select the region closest to your users.
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `waitress-serve --port=$PORT app:app`
   - **Instance Type**: Select **Free** (or a higher tier if you encounter memory limitations with PyTorch).
5. Click **Advanced** and add the following **Environment Variables**:
   - `GROQ_API_KEY`: Your Groq API Key (from your `.env` file).
   - `UNET_MODEL_URL`: The direct download URL to your `unet_brain.pth` weights file (from Step 1).
   - `FIREBASE_SERVICE_ACCOUNT_JSON`: Copy and paste the **entire text content** of your local `serviceAccountKey.json` file.
6. Click **Deploy Web Service**. Render will fetch your code, install dependencies, download the model weights automatically, and start your app.

---

### Option B: Deploy on Railway.app

1. Sign up/Log in to [Railway](https://railway.app/).
2. Click **New Project** -> **Deploy from GitHub repo** and select your repository.
3. Once the service is created, go to the **Variables** tab and click **New Variable** to add:
   - `GROQ_API_KEY`
   - `UNET_MODEL_URL`
   - `FIREBASE_SERVICE_ACCOUNT_JSON` (the string contents of `serviceAccountKey.json`)
4. Go to **Settings** -> **Deploy** -> **Start Command** and set it to:
   ```bash
   waitress-serve --port=$PORT app:app
   ```
5. Railway will automatically rebuild and redeploy your service. Go to **Settings** -> **Environment** -> **Generate Domain** to get your live URL.

---

## Step 4: Persistent Volumes (Optional but Recommended)

On cloud providers like Render and Railway, the local disk is **ephemeral**. This means every time the server restarts or goes to sleep:
1. Deployed patient files inside the `uploads/` directory will be deleted.
2. The encryption `secret.key` file will be regenerated, which means any previously encrypted images (if they survived a restart) cannot be decrypted.

### How to fix this:
- **Render**: Under your web service dashboard, go to **Disks** -> **Add Disk**. Set the mount path to `/app/uploads` and size to `1 GB`. Store the `secret.key` in `/app/uploads/secret.key` by updating the path in `app.py` if desired.
- **Railway**: Go to your Service -> **Volumes** -> **Add Volume**. Mount it to `/app/uploads`.
