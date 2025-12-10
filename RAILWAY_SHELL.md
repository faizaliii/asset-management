# How to Access Railway Shell

## Option 1: Railway CLI (Easiest)

1. **Install Railway CLI** (if not already installed):
   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Link to your project**:
   ```bash
   cd asset-management
   railway link
   ```
   (Select your project when prompted)

4. **Open shell**:
   ```bash
   railway shell
   ```

5. **Run the initialization commands**:
   ```bash
   python app/scripts/init_db.py
   python app/scripts/load_data.py
   python app/scripts/create_users.py
   ```

## Option 2: Railway Web Interface

1. In Railway dashboard, go to your **"web"** service
2. Click on **"Deployments"** tab (you're already there)
3. Click on the **three dots (⋮)** menu next to the active deployment
4. Select **"Open Shell"** or **"Terminal"**
5. This will open a web-based terminal
6. Run your commands there

## Option 3: Direct Command via Railway CLI

You can also run commands directly without opening a shell:

```bash
railway run python app/scripts/init_db.py
railway run python app/scripts/load_data.py
railway run python app/scripts/create_users.py
```

## Quick Setup (All Commands at Once)

If using Railway CLI, you can run all setup commands:

```bash
railway run python app/scripts/init_db.py && \
railway run python app/scripts/load_data.py && \
railway run python app/scripts/create_users.py
```

