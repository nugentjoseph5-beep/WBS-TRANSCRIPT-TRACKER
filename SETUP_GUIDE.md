# WBS Transcript Tracker - Complete Setup Guide

## Project Overview
**Repository**: https://github.com/nugentjoseph5-beep/WBS-TRANSCRIPT-TRACKER
**Framework**: React Frontend + FastAPI Backend
**Database**: MongoDB
**OS Used**: Windows 11

---

## Prerequisites Installed
- ✅ Python 3.14
- ✅ Node.js and npm
- ✅ Yarn (v1.22.22)
- ✅ MongoDB (Community Edition)
- ✅ Git

---

## Installation Steps Completed

### 1. Cloned Repository
```bash
git clone https://github.com/nugentjoseph5-beep/WBS-TRANSCRIPT-TRACKER.git
cd WBS-TRANSCRIPT-TRACKER
```

### 2. MongoDB Setup
- Downloaded and installed MongoDB Community Edition
- Added MongoDB to Windows PATH
- Started MongoDB service: `net start MongoDB`
- Verified with: `mongosh` command

### 3. Backend Setup

#### Installed Python Dependencies
```bash
cd backend
python -m pip install -r requirements-simple.txt
```

**Note**: Used simplified requirements file (`requirements-simple.txt`) due to dependency conflicts with:
- google-api-core[grpc] version conflicts
- grpcio-status version conflicts
- protobuf version conflicts

**Modified packages**:
- Removed: `emergentintegrations==0.1.0` (unavailable on PyPI)
- Downgraded: `grpcio-status` to compatible version
- Adjusted: `protobuf` to compatible version

#### Created Environment Variables
Set in PowerShell before running backend:
```powershell
$env:MONGO_URL="mongodb://localhost:27017"
$env:DB_NAME="wbs_tracker"
$env:JWT_SECRET="your-super-secret-jwt-key-change-this-in-production"
$env:CORS_ORIGINS="http://localhost:3000,http://localhost:3001"
```

#### Started Backend Server
```powershell
cd C:\Users\j.nugent\WBS-TRANSCRIPT-TRACKER\backend
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

**Status**: ✅ Running on `http://localhost:8000`

### 4. Frontend Setup

#### Installed Node Dependencies
```bash
cd frontend
yarn install
```

#### Created Frontend Environment
File: `frontend/.env.local`
```
REACT_APP_BACKEND_URL=http://localhost:8000
```

#### Started Frontend Dev Server
```bash
yarn start
```

**Status**: ✅ Running on `http://localhost:3000`

---

## Default Admin Credentials
- **Email**: `admin@wolmers.org`
- **Password**: `Admin123!`

**Auto-created**: The admin account is automatically created when the backend starts for the first time.

---

## Accessing the Application

### Frontend URL
```
http://localhost:3000
```

### Backend API
```
http://localhost:8000
```

### API Documentation
```
http://localhost:8000/docs
```

---

## Key Files Modified/Created

### requirements-simple.txt
Created a simplified requirements file that removes problematic Google API packages to avoid dependency conflicts.

### frontend/.env.local
Sets the backend URL for the frontend to connect to.

### startup scripts
- `start-all.sh` - Starts both backend and frontend
- `start-backend.sh` - Starts only backend
- `start-frontend.sh` - Starts only frontend
- `backend/.env` - Backend environment configuration

---

## Troubleshooting

### Issue: "craco: not found"
**Solution**: Run `yarn install` in the frontend folder to install all dependencies.

### Issue: Dependency conflicts
**Solution**: Use `requirements-simple.txt` instead of `requirements.txt` in the backend folder.

### Issue: MONGO_URL not found
**Solution**: Set environment variables in PowerShell before running the backend:
```powershell
$env:MONGO_URL="mongodb://localhost:27017"
$env:DB_NAME="wbs_tracker"
$env:JWT_SECRET="your-secret-key"
$env:CORS_ORIGINS="http://localhost:3000"
```

### Issue: Port already in use
**Solution**: 
- For port 8000: `netstat -ano | findstr :8000`
- For port 3000: `netstat -ano | findstr :3000`
- Kill process or use different port: `python -m uvicorn server:app --port 9000`

### Issue: MongoDB not starting
**Windows**: 
```powershell
net start MongoDB
mongosh
```

### Issue: Frontend can't connect to backend
**Solution**: Verify `frontend/.env.local` contains:
```
REACT_APP_BACKEND_URL=http://localhost:8000
```

---

## Architecture

```
WBS-TRANSCRIPT-TRACKER/
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   └── lib/
│   ├── package.json
│   ├── .env.local
│   └── craco.config.js
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   ├── requirements-simple.txt (used)
│   ├── .env
│   └── uploads/
├── start-all.sh
├── start-backend.sh
└── start-frontend.sh
```

---

## Technology Stack

### Frontend
- React 19.0.0
- React Router DOM 7.5.1
- Tailwind CSS 3.4.17
- shadcn/ui components
- Axios for API calls
- Sonner for notifications
- Recharts for data visualization

### Backend
- FastAPI 0.110.1
- Motor (async MongoDB driver)
- PyJWT for authentication
- bcrypt for password hashing
- Uvicorn ASGI server
- python-docx for document generation
- ReportLab for PDF generation

### Database
- MongoDB 7.0 (Community Edition)

---

## Running the Application

### Start Backend (Terminal 1)
```powershell
cd C:\Users\YourUsername\WBS-TRANSCRIPT-TRACKER\backend
$env:MONGO_URL="mongodb://localhost:27017"
$env:DB_NAME="wbs_tracker"
$env:JWT_SECRET="your-secret-key"
$env:CORS_ORIGINS="http://localhost:3000"
python -m uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

### Start Frontend (Terminal 2)
```powershell
cd C:\Users\YourUsername\WBS-TRANSCRIPT-TRACKER\frontend
yarn start
```

### Access Application
- **Frontend**: http://localhost:3000
- **Backend**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### Login
- Email: `admin@wolmers.org`
- Password: `Admin123!`

---

## Important Notes

1. **Keep both servers running** - Don't close the PowerShell windows while using the app
2. **MongoDB must be running** - Start it before running the backend
3. **Environment variables** - Must be set each time you restart PowerShell
4. **Use requirements-simple.txt** - The original requirements.txt has dependency conflicts

---

## Additional Resources

- **FastAPI Docs**: http://localhost:8000/docs
- **MongoDB Connection**: `mongodb://localhost:27017/wbs_tracker`
- **Frontend Port**: 3000
- **Backend Port**: 8000

---

## Support Notes

- The app uses port 3000 for frontend and port 8000 for backend
- MongoDB should be running on default port 27017
- Admin account is created automatically on first backend startup
- All API endpoints are documented at http://localhost:8000/docs

---

**Setup completed successfully!** 🎉
