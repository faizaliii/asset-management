# Deployment Guide - Railway

This guide will help you deploy the Asset Management application to Railway.

## Prerequisites

1. A Railway account (sign up at https://railway.app)

## Step 1: Deploy to Railway

### Option A: Deploy via GitHub (Recommended)

1. **Push your code to GitHub** (if not already done):
   ```bash
   cd asset-management
   git add .
   git commit -m "Prepare for deployment"
   git push origin main
   ```

2. **Connect Railway to GitHub**:
   - Go to https://railway.app
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Authorize Railway to access your GitHub account
   - Select your `asset-management` repository
   - Railway will automatically detect it's a Python app

3. **Add Environment Variables**:
   - In your Railway project, go to "Variables" tab
   - Add the following environment variable:
     ```
     SECRET_KEY=your-random-secret-key-here-generate-a-long-random-string
     ```
   - For `SECRET_KEY`, generate a random string (you can use: `python -c "import secrets; print(secrets.token_hex(32))"`)

4. **Add PostgreSQL Database** (optional but recommended):
   - In Railway, click "New" → "Database" → "Add PostgreSQL"
   - Railway will automatically set the `DATABASE_URL` environment variable
   - The app will automatically use PostgreSQL instead of SQLite

5. **Add Volume Storage for Barcode Images**:
   - In Railway, click "New" → "Volume"
   - Name it "barcode-storage" (or any name you prefer)
   - Set the mount path to `/data` (this is the default)
   - Railway will automatically set the `RAILWAY_VOLUME_MOUNT_PATH` environment variable
   - **Important**: The volume will persist barcode images across deployments

6. **Deploy**:
   - Railway will automatically deploy when you push to the main branch
   - Or click "Deploy" in the Railway dashboard

### Option B: Deploy via Railway CLI

1. **Install Railway CLI**:
   ```bash
   npm i -g @railway/cli
   ```

2. **Login to Railway**:
   ```bash
   railway login
   ```

3. **Initialize Railway project**:
   ```bash
   cd asset-management
   railway init
   ```

4. **Set environment variables**:
   ```bash
   railway variables set SECRET_KEY=your-random-secret-key-here
   ```

5. **Add PostgreSQL** (optional):
   ```bash
   railway add postgresql
   ```

6. **Add Volume**:
   ```bash
   railway volume create barcode-storage
   railway volume mount barcode-storage /data
   ```

7. **Deploy**:
   ```bash
   railway up
   ```

## Step 2: Initialize Database

After deployment, you need to initialize the database:

1. **Open Railway Shell**:
   - In Railway dashboard, go to your service
   - Click "Deployments" → "View Logs"
   - Or use Railway CLI: `railway shell`

2. **Run initialization scripts**:
   ```bash
   python app/scripts/init_db.py
   python app/scripts/load_data.py
   python app/scripts/create_users.py
   ```

## Step 3: Access Your Application

1. Railway will provide you with a URL (e.g., `https://your-app-name.up.railway.app`)
2. Click on the URL or go to "Settings" → "Generate Domain" to get a custom domain
3. Your app should now be live!

## Environment Variables Reference

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `SECRET_KEY` | Flask secret key for sessions | Yes | (none) |
| `DATABASE_URL` | Database connection string | No | `sqlite:///asset_manager.db` |
| `RAILWAY_VOLUME_MOUNT_PATH` | Path where Railway volume is mounted | No | `/data` |

**Note**: Railway automatically sets `RAILWAY_VOLUME_MOUNT_PATH` when you mount a volume. The default is `/data`.

## Storage Configuration

### Railway Volume Storage

- **Location**: Barcode images are stored in Railway volumes at `/data/barcodes/`
- **Persistence**: Files persist across deployments
- **Backup**: Railway volumes are automatically backed up
- **Cost**: Included in Railway pricing (check current pricing)

### Local Development

- **Location**: Barcode images are stored in `app/static/barcodes/`
- **Git**: This directory is excluded from git (see `.gitignore`)

## Troubleshooting

### Database Issues
- If using PostgreSQL, make sure the `DATABASE_URL` is set correctly
- Railway automatically sets this when you add a PostgreSQL service

### Barcode Images Not Showing
- Check that the Railway volume is mounted correctly
- Verify the volume mount path is `/data` (or matches `RAILWAY_VOLUME_MOUNT_PATH`)
- Check Railway logs for storage errors
- Ensure the volume has write permissions

### Application Won't Start
- Check Railway logs for errors
- Verify all environment variables are set
- Make sure `requirements.txt` includes all dependencies
- Check that the volume is properly mounted

### Port Issues
- Railway automatically sets the `PORT` environment variable
- The Procfile uses `$PORT` - don't change this

### Volume Not Mounted
- Verify the volume is created in Railway dashboard
- Check that the mount path is set correctly
- Ensure the service has access to the volume

## Cost Estimate

**Railway Pricing:**
- **Hobby Plan**: $5/month (includes 512MB RAM, 1GB storage, 100GB bandwidth)
- **Developer Plan**: $20/month (includes 2GB RAM, 8GB storage, 400GB bandwidth)
- **Volume Storage**: Included in plan (check current pricing)
- **PostgreSQL**: Included in plan

**Total Cost**: Starting at $5/month for small applications

## Alternative Deployment Options

### Render.com
- Free tier available
- Similar setup process
- PostgreSQL included
- Persistent disk storage available

### Fly.io
- Free tier available
- Good for global distribution
- Volume storage available

### Heroku
- Paid plans only (no free tier)
- Easy deployment
- PostgreSQL addon available
- Ephemeral filesystem (use S3 for persistent storage)

## Post-Deployment Checklist

- [ ] Database initialized
- [ ] Initial data loaded (locations, categories, etc.)
- [ ] Users created
- [ ] Environment variables set
- [ ] Railway volume mounted
- [ ] Test asset registration
- [ ] Test barcode generation
- [ ] Verify images are stored in Railway volume
- [ ] Test image serving

## Storage Details

### How It Works

1. **Development**: Barcodes are stored in `app/static/barcodes/` directory
2. **Production**: Barcodes are stored in Railway volume at `/data/barcodes/`
3. **Serving**: Images are served via Flask route `/static/barcodes/<filename>`
4. **Persistence**: Railway volumes persist across deployments and restarts

### Volume Management

- **Create Volume**: Railway dashboard → New → Volume
- **Mount Volume**: Set mount path to `/data` (default)
- **View Files**: Use Railway shell to access volume
- **Backup**: Railway automatically backs up volumes

## Support

For issues:
1. Check Railway logs
2. Verify volume is mounted correctly
3. Check environment variables
4. Review application logs
5. Verify file permissions on volume
