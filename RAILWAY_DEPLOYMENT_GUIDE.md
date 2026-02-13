# Railway.app Deployment Guide
## WBS Transcript Tracker - Online Deployment

---

## Prerequisites

Before starting, make sure you have:
- ✅ GitHub account
- ✅ Railway account (https://railway.app)
- ✅ Project pushed to GitHub repository
- ✅ All local testing complete and working

---

## Step 1: Push Your Code to GitHub

If you haven't already pushed your code:

```bash
cd C:\Users\YourUsername\WBS-TRANSCRIPT-TRACKER
git add .
git commit -m "WBS Transcript Tracker - Ready for deployment"
git push origin main
```

**Verify** your GitHub repo has:
- `backend/` folder
- `frontend/` folder
- `requirements-simple.txt` in backend
- `package.json` in frontend

---

## Step 2: Create Railway Account

1. Go to: https://railway.app
2. Click **"Start for free"** or **"Sign up"**
3. Choose **"Continue with GitHub"**
4. Authorize Railway to access your GitHub
5. Create new project

---

## Step 3: Add MongoDB to Your Project

### In Railway Dashboard:

1. Click the **"+"** button or **"Add Service"**
2. Search for **"MongoDB"**
3. Click **"MongoDB"**
4. Railway will:
   - Create MongoDB instance
   - Generate connection string automatically
   - Show credentials in the dashboard

### Copy MongoDB Connection String:

1. Click the MongoDB service in your project
2. Go to **"Variables"** tab
3. Look for **DATABASE_URL** or similar
4. Copy the full connection string
   - Format: `mongodb+srv://username:password@cluster.mongodb.net/dbname?retryWrites=true&w=majority`
   - Or: `mongodb://user:pass@host:port/dbname`

**Save this string** - you'll need it for backend configuration.

---

## Step 4: Deploy Backend to Railway

### Step 4A: Add GitHub Repository

1. In Railway dashboard, click **"+ Add Service"**
2. Select **"GitHub Repo"**
3. Search for your repo: `WBS-TRANSCRIPT-TRACKER`
4. Click to select it

### Step 4B: Configure Backend Service

1. Railway will detect it's a GitHub repo
2. **Root Directory**: Set to `backend`
3. Railway should auto-detect it's a Python app
4. Click **"Deploy"**

**Wait 2-5 minutes for initial build...**

### Step 4C: Add Environment Variables

Once deployed, configure the backend:

1. Click your backend service in Railway dashboard
2. Go to **"Variables"** tab
3. Add these environment variables:

```
MONGO_URL = mongodb+srv://username:password@cluster.mongodb.net/wbs_tracker?retryWrites=true&w=majority
DB_NAME = wbs_tracker
JWT_SECRET = super-secret-key-change-this-in-production-12345
CORS_ORIGINS = https://your-frontend-url.railway.app,https://your-domain.com
RESEND_API_KEY = (leave blank if not using email)
SENDER_EMAIL = onboarding@resend.dev
```

**For MONGO_URL**: 
- Use the MongoDB connection string from Step 3
- Replace `<username>` and `<password>` with actual credentials
- Change database name to `wbs_tracker`

### Step 4D: Get Backend URL

1. Click your backend service
2. Go to **"Settings"** tab
3. Look for **"Public URL"** or **"Domain"**
4. Copy the full URL
   - Example: `https://wbs-transcript-tracker-production.up.railway.app`

**Save this URL** - you need it for frontend configuration.

---

## Step 5: Configure Backend for Production

### Update Startup Command:

1. In Railway backend service, go to **"Settings"**
2. Find **"Start Command"**
3. Set it to:
   ```
   python -m uvicorn server:app --host 0.0.0.0 --port $PORT
   ```
   (Railway sets PORT environment variable automatically)

4. **Save changes** - service will redeploy

### Verify Backend is Running:

1. Visit your backend URL: `https://your-backend-url.railway.app`
2. Should show: `{"detail":"Not Found"}` or FastAPI docs at `/docs`
3. If you see an error, check the **"Logs"** tab for issues

---

## Step 6: Deploy Frontend to Railway

### Step 6A: Add Another GitHub Repository Service

1. In Railway project dashboard, click **"+ Add Service"**
2. Select **"GitHub Repo"**
3. Select the **same repo** again
4. Railway will ask about root directory

### Step 6B: Configure Frontend Service

1. **Root Directory**: Set to `frontend`
2. Railway might auto-detect it's a Node.js app
3. **Build Command**: `yarn build`
4. **Start Command**: `yarn start`
5. Click **"Deploy"**

**Wait 5-10 minutes for build and deployment...**

### Step 6C: Add Frontend Environment Variables

1. Click your frontend service
2. Go to **"Variables"** tab
3. Add this environment variable:

```
REACT_APP_BACKEND_URL = https://your-backend-url.railway.app
```

**Use the backend URL from Step 4D**

### Step 6D: Get Frontend URL

1. Click your frontend service
2. Go to **"Settings"** tab
3. Look for **"Public URL"** or **"Domain"**
4. Copy the full URL
   - Example: `https://wbs-transcript-tracker-frontend.up.railway.app`

---

## Step 7: Test Your Deployment

### Test Backend API:

1. Visit: `https://your-backend-url.railway.app/docs`
2. Should show **FastAPI Swagger UI**
3. Try the **GET /analytics** endpoint
4. Should return data (not an error)

### Test Frontend:

1. Visit: `https://your-frontend-url.railway.app`
2. Should load the **Landing Page**
3. Click **"Login"**
4. Try logging in with:
   - Email: `admin@wolmers.org`
   - Password: `Admin123!`

### If Login Works:

✅ **Deployment successful!** You should see:
- Admin Dashboard
- Analytics charts
- User management
- Request tracking

### If Login Fails:

Check these things:

**1. Backend Connection**:
- Open browser DevTools (F12)
- Go to **Network** tab
- Try logging in
- Look for failed API requests
- Check the error message

**2. Check Backend Logs**:
- In Railway, click backend service
- Go to **"Logs"** tab
- Look for error messages
- Common issues:
  - MongoDB connection failed
  - CORS error (check CORS_ORIGINS variable)
  - JWT_SECRET not set

**3. Check Environment Variables**:
- Make sure all variables are set correctly
- Especially: `MONGO_URL`, `REACT_APP_BACKEND_URL`

---

## Step 8: Custom Domain (Optional)

If you have a custom domain (like `app.wolmers.org`):

### For Frontend:

1. Click frontend service in Railway
2. Go to **"Settings"** → **"Domains"**
3. Click **"+ Add Domain"**
4. Enter your domain
5. Follow DNS instructions from Railway
6. Add DNS records to your domain provider

### For Backend:

1. Same process for backend service
2. Use different domain (like `api.wolmers.org`)

### Update Frontend Variable:

1. After custom domain is set up
2. Update frontend `REACT_APP_BACKEND_URL` to your custom backend domain
3. Railway will redeploy automatically

---

## Step 9: Useful Railway Commands & Tips

### Monitor Your App:

1. **Logs Tab**: See real-time error logs
2. **Metrics Tab**: View CPU, memory, database usage
3. **Deployments Tab**: See deployment history

### Redeploy:

1. Click service
2. Go to **"Settings"**
3. Click **"Redeploy"** button
4. Latest code from GitHub is deployed

### Update Environment Variables:

1. Click service
2. Go to **"Variables"**
3. Change any variable
4. Click **"Save"**
5. Service auto-redeploys

### Scale (Upgrade Plan):

1. Click service
2. Go to **"Settings"**
3. Find **"Plan"** or **"Tier"**
4. Upgrade for more resources
5. Free tier has limited CPU/memory

---

## Step 10: Production Best Practices

### Security:

1. ✅ **Change JWT_SECRET** to a secure, random string:
   ```
   JWT_SECRET = <use a strong random string like: `openssl rand -hex 32`>
   ```

2. ✅ **Update CORS_ORIGINS** with your actual domains:
   ```
   CORS_ORIGINS = https://your-frontend-domain.com,https://www.your-frontend-domain.com
   ```

3. ✅ **Update database name** from default

4. ✅ **Enable MongoDB backups** in MongoDB Atlas (if using Atlas)

### Performance:

1. ✅ **Enable caching** in frontend (Railway does this automatically)

2. ✅ **Monitor logs** for errors

3. ✅ **Set up email notifications** from Railway

### Backups:

1. ✅ **MongoDB Backups**: Set up automatic backups in MongoDB Atlas
2. ✅ **GitHub Backups**: Your code is already backed up on GitHub

---

## Troubleshooting

### Problem: Backend won't deploy
**Solution**: 
- Check Logs tab for errors
- Make sure `python -m uvicorn server:app ...` works locally
- Verify all Python dependencies in `requirements-simple.txt`

### Problem: Frontend shows 404 errors
**Solution**:
- Clear browser cache (Ctrl+Shift+Del)
- Check that `REACT_APP_BACKEND_URL` is set correctly
- Visit `https://your-frontend-url.railway.app/docs` to test backend connection

### Problem: Login fails with "Invalid credentials"
**Solution**:
- Check MongoDB connection (MONGO_URL)
- Verify MongoDB contains admin user
- Check backend logs for database errors
- Make sure admin account was created on first run

### Problem: CORS errors
**Solution**:
- Update `CORS_ORIGINS` to include your frontend URL
- Don't use `localhost` - use actual domain name
- Redeploy backend after changing variable

### Problem: Build takes too long
**Solution**:
- This is normal for first deployment (5-15 minutes)
- Subsequent builds are faster
- Check Logs tab to see progress

---

## Your URLs After Deployment

```
Frontend:     https://your-frontend-url.railway.app
Backend:      https://your-backend-url.railway.app
API Docs:     https://your-backend-url.railway.app/docs
MongoDB:      Managed by Railway (private)
```

---

## Next Steps

1. Test the app thoroughly at your Railway URLs
2. Invite users to test (staff, students)
3. Monitor logs and metrics daily for first week
4. Set up email notifications (optional)
5. Plan for scaling if needed

---

## Support & Documentation

- **Railway Docs**: https://docs.railway.app
- **FastAPI Docs**: https://fastapi.tiangolo.com
- **React Docs**: https://react.dev
- **MongoDB Atlas**: https://www.mongodb.com/cloud/atlas

---

## Quick Reference Checklist

- [ ] GitHub account with repo
- [ ] Railway account created
- [ ] MongoDB service added to Railway
- [ ] Backend deployed to Railway
- [ ] Backend environment variables set
- [ ] Backend URL copied
- [ ] Frontend deployed to Railway
- [ ] Frontend `REACT_APP_BACKEND_URL` set to backend URL
- [ ] Frontend URL copied
- [ ] Tested backend at `/docs` endpoint
- [ ] Tested frontend login
- [ ] Custom domain configured (if needed)
- [ ] JWT_SECRET changed to secure value
- [ ] CORS_ORIGINS updated with actual domain
- [ ] Backups enabled
- [ ] Monitoring set up

---

**Your app is now live online!** 🚀

Share your Railway URLs with your team and users to start using the WBS Transcript Tracker from anywhere!
