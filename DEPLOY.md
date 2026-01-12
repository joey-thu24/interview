# 🚀 Deployment Guide (Streamlit Cloud + TiDB)

Your application is "Stateless" (local files are not saved permanently), but it uses **TiDB Cloud** for data storage. This makes it perfect for **Streamlit Community Cloud**.

## Step 1: Prepare Codebase
We have already updated your `requirements.txt`.
Ensure all your files are saved.

## Step 2: Push to GitHub
1. Create a new repository on GitHub.
2. Push your code:
   ```bash
   git init
   git add .
   git commit -m "Ready for deployment"
   git branch -M main
   # Replace with your repo URL
   git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git
   git push -u origin main
   ```

## Step 3: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io/).
2. Click **"New app"**.
3. Select your GitHub repository.
4. Set **Main file path** to: `app/main.py`
5. Click **"Deploy!"**.

## Step 4: Configure Secrets (Critical!)
Your `.env` file is not uploaded to GitHub (it's ignored for security). You must set these variables in the Streamlit Cloud dashboard.

1. On your app's dashboard, click **"Manage app"** (bottom right) or the **Settings** menu.
2. Go to **"Secrets"**.
3. Copy the content of your local `.env` file and paste it there in TOML format.

**Example format for Streamlit Secrets:**
```toml
# NOTE: Streamlit Secrets uses TOML format.
# If your .env is KEY=VALUE, here it is usually same, but keys are case sensitive.

DATABASE_URL = "mysql+pymysql://<user>:<password>@<host>:<port>/<dbname>?ssl_verify_cert=true&ssl_verify_identity=true"
OPENAI_API_KEY = "sk-......"
OPENAI_BASE_URL = "https://api.siliconflow.cn/v1"
```

## Step 5: Verify
- Visit your App URL.
- Try to **Register** a new user.
- Since TiDB is a cloud database, your data will persist even if the app restarts!
