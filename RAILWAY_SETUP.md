# Railway Setup - Next Steps

## Step 1: Initialize Database

1. **Open Railway Shell**:
   - Go to your Railway project dashboard
   - Click on your service
   - Click "Deployments" tab
   - Click on the latest deployment
   - Click "View Logs" or use the terminal icon to open shell
   - OR use Railway CLI: `railway shell`

2. **Run database initialization**:
   ```bash
   python app/scripts/init_db.py
   ```

## Step 2: Load Initial Data

Load locations, categories, subcategories, and sublocations:

```bash
python app/scripts/load_data.py
```

## Step 3: Create Users

Create default users (admin and members):

```bash
python app/scripts/create_users.py
```

This creates:
- `admin` / `admin123` (Admin role)
- `user1` / `password1` (Member role)
- `user2` / `password2` (Member role)
- `manager` / `manager123` (Member role)
- `staff` / `staff123` (Member role)

## Step 4: Access Your Application

1. **Get your app URL**:
   - In Railway dashboard, go to your service
   - Click "Settings" tab
   - Find "Domains" section
   - Copy your Railway URL (e.g., `https://your-app.up.railway.app`)

2. **Open in browser** and login with:
   - Username: `admin`
   - Password: `admin123`

## Step 5: Verify Everything Works

1. ✅ Login with admin account
2. ✅ Register a new asset
3. ✅ Check that barcode is generated
4. ✅ View asset list
5. ✅ Test filtering
6. ✅ Test printing barcode

## Important Notes

- **Change default passwords** after first login
- **Set SECRET_KEY** environment variable in Railway (if not already set)
- **Add Volume** for barcode storage (if not already added):
  - Railway dashboard → New → Volume
  - Mount path: `/data`
  - Name: `barcode-storage`

## Troubleshooting

**Can't access shell?**
- Use Railway CLI: `railway shell`

**Scripts not found?**
- Make sure you're in the correct directory
- Try: `cd /app && python app/scripts/init_db.py`

**Database errors?**
- Check that PostgreSQL is added and `DATABASE_URL` is set
- Verify connection in Railway logs

**Barcode images not showing?**
- Verify volume is mounted at `/data`
- Check Railway logs for storage errors

