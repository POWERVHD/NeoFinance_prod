# NeoFinance Deployment Checklist

**Date:** November 1, 2025
**App:** NeoFinance - AI-Powered Finance Dashboard
**Status:** Ready for Deployment ✅

---

## 📋 PRE-DEPLOYMENT VERIFICATION

### ✅ Code Fixes Completed

- [x] Frontend API URL uses environment variable (`VITE_API_URL`)
- [x] Frontend `.env.example` created with required variables
- [x] Backend `main.py` wrapper created for Render compatibility
- [x] `render.yaml` configuration file created for easy deployment
- [x] Backup SQL schema created (`supabase_schema_backup.sql`)
- [x] Deployment plan updated with NeoFinance specifics
- [x] All changes ready to commit

### ✅ Account Requirements

- [ ] GitHub account - Repository: `NeoFinance_Prod`
- [ ] Supabase account created → https://supabase.com
- [ ] Render account created → https://render.com
- [ ] Vercel account created → https://vercel.com
- [ ] Google AI Studio account → https://aistudio.google.com

---

## 🚀 DEPLOYMENT STEPS

### PHASE 1: Database Setup (Supabase)
**Estimated Time:** 10 minutes

- [ ] **1.1 Create Supabase Project**
  - Go to https://supabase.com/dashboard
  - Click "New Project"
  - Project name: `neofinance-prod`
  - Database password: _(generate strong password & save securely)_
  - Region: Singapore or closest to you
  - Wait for provisioning (~2 min)

- [ ] **1.2 Get Connection String**
  - Navigate: Settings → Database
  - Copy "Connection String (URI)"
  - Format: `postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres`
  - Save in password manager

- [ ] **1.3 Run Alembic Migrations**
  ```bash
  # Temporarily update backend/.env with Supabase DATABASE_URL
  cd backend
  alembic upgrade head
  ```

- [ ] **1.4 Verify Database**
  - Go to Supabase → Table Editor
  - Confirm tables: `users`, `transactions`, `alembic_version`
  - Check indexes are created

**Save for Later:**
```
DATABASE_URL=postgresql://postgres:[PASSWORD]@[HOST]:5432/postgres
SUPABASE_URL=https://[project-id].supabase.co
```

---

### PHASE 2: Backend Deployment (Render)
**Estimated Time:** 15 minutes

- [ ] **2.1 Generate Production Secrets**
  ```bash
  # Generate SECRET_KEY
  python -c "import secrets; print(secrets.token_urlsafe(32))"
  # Save the output securely
  ```

- [ ] **2.2 Get Gemini API Key**
  - Go to https://aistudio.google.com
  - Create API key for Gemini
  - Save securely

- [ ] **2.3 Create Render Web Service**
  - Go to https://dashboard.render.com
  - Click "New +" → "Web Service"
  - Connect GitHub repository: `NeoFinance_Prod`
  - Render will detect `render.yaml` automatically

- [ ] **2.4 Configure Build Settings** (if not using render.yaml)
  ```
  Name: neofinance-backend
  Region: Singapore
  Branch: main
  Root Directory: backend
  Runtime: Python 3
  Build Command: pip install -r requirements.txt
  Start Command: uvicorn main:app --host 0.0.0.0 --port $PORT
  Instance: Free
  ```

- [ ] **2.5 Add Environment Variables**
  Click "Environment" tab and add:
  ```bash
  DATABASE_URL=[from Supabase Step 1.2]
  SECRET_KEY=[generated in Step 2.1]
  ALGORITHM=HS256
  ACCESS_TOKEN_EXPIRE_MINUTES=30
  API_V1_PREFIX=/api/v1
  PROJECT_NAME=NeoFinance API
  DEBUG=False
  CORS_ORIGINS=http://localhost:5173
  GEMINI_API_KEY=[from Step 2.2]
  ENVIRONMENT=production
  ```
  **Note:** Will update `CORS_ORIGINS` after Vercel deployment

- [ ] **2.6 Deploy Backend**
  - Click "Create Web Service"
  - Wait for build (~3-5 minutes)
  - Monitor logs for errors

- [ ] **2.7 Verify Backend**
  - Note Render URL: `https://neofinance-backend.onrender.com`
  - Visit: `https://neofinance-backend.onrender.com/docs`
  - Verify FastAPI docs load
  - Test root endpoint: `https://neofinance-backend.onrender.com/`
  - Should return: `{"status": "ok", "message": "NeoFinance API", ...}`

**Save for Later:**
```
BACKEND_URL=https://neofinance-backend.onrender.com
```

---

### PHASE 3: Frontend Deployment (Vercel)
**Estimated Time:** 10 minutes

- [ ] **3.1 Create Vercel Project**
  - Go to https://vercel.com/dashboard
  - Click "Add New..." → "Project"
  - Import Git repository: `NeoFinance_Prod`
  - Select repository

- [ ] **3.2 Configure Build Settings**
  ```
  Framework Preset: Vite
  Root Directory: frontend
  Build Command: npm run build
  Output Directory: dist
  Install Command: npm install
  Node Version: 20.x
  ```

- [ ] **3.3 Add Environment Variables**
  Settings → Environment Variables:
  ```bash
  VITE_API_URL=https://neofinance-backend.onrender.com/api/v1
  VITE_APP_NAME=NeoFinance
  VITE_APP_VERSION=1.0.0
  ```
  Apply to: Production, Preview, Development

- [ ] **3.4 Deploy Frontend**
  - Click "Deploy"
  - Wait for build (~2-3 minutes)
  - Monitor build logs

- [ ] **3.5 Get Vercel Domain**
  - Note deployed URL: `https://[project-name].vercel.app`
  - Save this URL

**Save for Later:**
```
FRONTEND_URL=https://[your-project].vercel.app
```

---

### PHASE 4: Final Configuration
**Estimated Time:** 5 minutes

- [ ] **4.1 Update Backend CORS**
  - Go back to Render dashboard
  - Navigate to neofinance-backend → Environment
  - Update `CORS_ORIGINS`:
    ```
    CORS_ORIGINS=https://[your-project].vercel.app,https://[your-project]-*.vercel.app,http://localhost:5173
    ```
  - Save changes
  - Wait for automatic redeploy (~2 min)

- [ ] **4.2 Verify CORS Configuration**
  - Visit frontend URL
  - Open browser DevTools → Console
  - Should see NO CORS errors
  - Check Network tab for API calls

---

## ✅ POST-DEPLOYMENT TESTING

### End-to-End Flow Test

- [ ] **Test 1: User Registration**
  - Visit frontend URL
  - Navigate to Register/Sign Up
  - Create test account
  - Verify success message

- [ ] **Test 2: User Login**
  - Log in with test credentials
  - Verify redirect to dashboard
  - Check token stored in localStorage

- [ ] **Test 3: Dashboard Load**
  - Verify dashboard components render
  - Check summary cards display
  - Verify no console errors

- [ ] **Test 4: Create Transaction**
  - Add new income transaction
  - Add new expense transaction
  - Verify they appear in list

- [ ] **Test 5: View Transactions**
  - Check transaction list loads
  - Verify data displays correctly
  - Test filtering/sorting (if applicable)

- [ ] **Test 6: AI Financial Coach (if enabled)**
  - Test Gemini AI integration
  - Verify financial insights load
  - Check for API errors

- [ ] **Test 7: Backend Performance**
  - Check first request cold start time
  - Note: ~30 seconds is normal for free tier
  - Subsequent requests should be fast (<500ms)

---

## 📊 DEPLOYMENT VERIFICATION

### Health Checks

- [ ] Backend health endpoint responding
- [ ] Frontend loads without errors
- [ ] Database connection successful
- [ ] API authentication working
- [ ] CORS properly configured
- [ ] No JavaScript console errors
- [ ] No network request failures

### Security Checks

- [ ] `.env` files NOT committed to Git
- [ ] Production `SECRET_KEY` is unique (not example key)
- [ ] Database password is strong
- [ ] API keys stored securely (not in code)
- [ ] CORS origins are specific (not wildcard `*`)

---

## 📝 DEPLOYMENT INFORMATION

### URLs (Fill in after deployment)

```bash
# Frontend
FRONTEND_URL=https://_____________.vercel.app

# Backend
BACKEND_URL=https://neofinance-backend.onrender.com
BACKEND_DOCS=https://neofinance-backend.onrender.com/docs

# Database
SUPABASE_PROJECT=https://_____________.supabase.co
SUPABASE_DASHBOARD=https://supabase.com/dashboard/project/_____________

# Dashboards
VERCEL_DASHBOARD=https://vercel.com/dashboard
RENDER_DASHBOARD=https://dashboard.render.com
```

### Credentials (Store securely in password manager)

```
DATABASE_URL=postgresql://postgres:_____________@_____________.supabase.co:5432/postgres
SECRET_KEY=_____________
GEMINI_API_KEY=_____________
SUPABASE_PASSWORD=_____________
```

---

## 🎤 INTERVIEW PREPARATION

### Pre-Interview Checklist (Day Before)

- [ ] Wake backend (visit URL 5 min before interview)
- [ ] Test complete user flow once
- [ ] Clear browser cache and test as new user
- [ ] Prepare to explain architecture
- [ ] Have local version ready as backup
- [ ] Practice demo flow (2-3 minutes)

### Key Talking Points

**Architecture:**
- "Deployed with microservices architecture using Vercel (frontend), Render (backend), and Supabase (database)"
- "Each component scales independently"
- "Demonstrates production-ready DevOps practices"

**Technology Choices:**
- "React + Vite for fast frontend development"
- "FastAPI for modern Python backend with auto-generated docs"
- "PostgreSQL via Supabase for managed database with connection pooling"
- "Alembic for database migration management"
- "Google Gemini AI for intelligent financial insights"

**Trade-offs:**
- "Free tier backend has ~30s cold start - shows cost optimization for demos"
- "Would use paid tier for production to eliminate cold starts"
- "Architecture supports easy upgrade path to scale"

---

## 🐛 TROUBLESHOOTING

### Issue: Frontend can't reach backend (CORS error)

**Solution:**
1. Check browser console for exact error
2. Verify `CORS_ORIGINS` in Render includes Vercel domain
3. Ensure protocol is `https://` not `http://`
4. Wait 2-3 min after updating env vars (auto-redeploy)

### Issue: Backend responds with 502 Bad Gateway

**Solution:**
1. Check Render logs for errors
2. Verify `DATABASE_URL` is correct
3. Test database connection from Supabase dashboard
4. Restart Render service manually

### Issue: Frontend shows blank page

**Solution:**
1. Check Vercel build logs for errors
2. Verify `VITE_API_URL` is set correctly
3. Check browser console for errors
4. Verify `frontend/dist` was created in build

### Issue: Alembic migrations fail

**Solution:**
1. Verify `DATABASE_URL` format is correct
2. Check Supabase project is running
3. Test connection: `psql $DATABASE_URL`
4. Fallback: Use `supabase_schema_backup.sql` in SQL Editor

---

## ✅ DEPLOYMENT COMPLETE!

**Total Time:** ~40 minutes
**Status:** Production Ready
**Next Steps:**
1. Document any customizations
2. Schedule regular health checks
3. Monitor free tier limits
4. Prepare demo walkthrough

---

**Deployed by:** _______________
**Date Completed:** _______________
**Production URL:** _______________
