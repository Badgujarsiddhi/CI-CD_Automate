# Deploy PharmaGuard: Vercel (Frontend) + Docker (Backend)

This guide deploys:
- **Frontend** → **Vercel** (no Docker, free tier)
- **Backend** → **Railway** or **Render** (Docker, free trial / low cost)
- **Groq API** → Used by backend (free tier)

You do **not** need Docker or virtualization on your own PC.

---

## Overview

```
User → Vercel (React app) → Backend on Railway/Render (Docker) → Groq API
```

1. Push your code to GitHub.
2. Deploy backend (Docker image) to Railway or Render; set `GROQ_API_KEY`.
3. Deploy frontend to Vercel; set `VITE_API_BASE_URL` to your backend URL.
4. Done.

---

## Prerequisites

- GitHub account
- [Groq API key](https://console.groq.com/keys)
- Vercel account (free): [vercel.com](https://vercel.com)
- Railway account (free trial): [railway.app](https://railway.app)  
  **or** Render account (free tier): [render.com](https://render.com)

---

## Step 1: Push Code to GitHub

### 1.1 Create a repository

1. Go to [github.com/new](https://github.com/new).
2. Name it (e.g. `pharmaguard`).
3. Do **not** add README/license (you already have code).
4. Create repository.

### 1.2 Push your project

From your project folder (adjust if your repo root is different):

```powershell
cd C:\Pharma_Guard\Pharma_Guard

git init
git add .
git commit -m "PharmaGuard: Vercel + Docker backend"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git push -u origin main
```

If the repo already exists:

```powershell
cd C:\Pharma_Guard\Pharma_Guard
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO_NAME.git
git add .
git commit -m "PharmaGuard: Vercel + Docker backend"
git push -u origin main
```

**Important:** Do **not** commit `.env` or `API_key.txt`. Add to `.gitignore`:

```
.env
.env.local
API_key.txt
**/API_key.txt
```

---

## Step 2: Deploy Backend (Docker) on Railway

### 2.1 Create project

1. Go to [railway.app](https://railway.app) and sign in with GitHub.
2. **New Project** → **Deploy from GitHub repo**.
3. Select your repo.
4. Railway will detect the repo; you will add the backend service manually.

### 2.2 Add backend service

1. In the project, click **+ New** → **GitHub Repo** (or **Empty Service**).
2. If you chose “Empty Service”:
   - **Settings** → **Source** → Connect the same GitHub repo.
   - **Root Directory**: set to `backend` (so Railway uses the `backend` folder).
   - **Build**: Dockerfile (Railway will use `backend/Dockerfile`).
3. If Railway added the whole repo:
   - **Settings** → **Root Directory** → `backend`.
   - **Settings** → **Build** → Dockerfile.
4. **Settings** → **Networking** → **Generate Domain** (e.g. `yourapp-backend.up.railway.app`).
5. **Variables**:
   - `GROQ_API_KEY` = your Groq API key.
   - `GROQ_MODEL` = `llama-3.1-8b-instant` (optional).
6. Save. Railway will build the Docker image and deploy.

### 2.3 Get backend URL

After deploy, open the service → **Settings** → **Networking** → copy the public URL, e.g.:

`https://pharmaguard-backend-production-xxxx.up.railway.app`

No trailing slash. You’ll use this in Step 3.

---

## Step 2 (Alternative): Deploy Backend on Render

### 2.1 Create Web Service

1. Go to [render.com](https://render.com) and sign in with GitHub.
2. **New** → **Web Service**.
3. Connect your repo and select it.

### 2.2 Configure

1. **Name**: `pharmaguard-backend`.
2. **Region**: choose closest to you.
3. **Root Directory**: `backend` (or leave blank if backend is at repo root).
4. **Environment**: **Docker**.
5. **Instance Type**: Free (or paid for more reliability).
6. **Environment Variables**:
   - `GROQ_API_KEY` = your Groq API key.
   - `GROQ_MODEL` = `llama-3.1-8b-instant` (optional).
7. **Create Web Service**.

### 2.3 Get backend URL

After deploy, the URL will look like:

`https://pharmaguard-backend.onrender.com`

Copy it (no trailing slash) for Step 3.

---

## Step 3: Deploy Frontend on Vercel

### 3.1 Import project

1. Go to [vercel.com](https://vercel.com) and sign in with GitHub.
2. **Add New** → **Project**.
3. Import your GitHub repo.

### 3.2 Configure build

1. **Root Directory**: set to `frontend` (so Vercel builds the React app).
2. **Framework Preset**: Vite (auto-detected).
3. **Build Command**: `npm run build` (default).
4. **Output Directory**: `dist` (default).
5. **Environment Variables**:
   - **Name**: `VITE_API_BASE_URL`
   - **Value**: your backend URL from Step 2, e.g.  
     `https://pharmaguard-backend-production-xxxx.up.railway.app`  
     or  
     `https://pharmaguard-backend.onrender.com`
   - Apply to Production, Preview, and Development.
6. **Deploy**.

### 3.3 Result

Vercel will give you a URL like:

`https://your-project.vercel.app`

Open it; the app will call your backend on Railway/Render.

---

## Step 4: Verify

1. Open the Vercel URL.
2. Upload a small VCF and select a drug; run analysis.
3. If you see results and LLM explanation, deployment is working.
4. If you see network/CORS errors, check:
   - Backend URL in `VITE_API_BASE_URL` (no trailing slash).
   - Backend is running (Railway/Render dashboard).
   - Backend has `GROQ_API_KEY` set (no “llm_not_configured_placeholder”).

---

## Repo structure (for reference)

Your repo should look like this so Root Directory settings work:

```
your-repo/
├── frontend/           ← Vercel root directory: "frontend"
│   ├── src/
│   ├── package.json
│   ├── vercel.json
│   └── ...
├── backend/            ← Railway/Render root directory: "backend"
│   ├── main.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── ...
├── docker-compose.yml  (optional; for local Docker)
└── README.md
```

---

## Environment variables summary

| Where       | Variable           | Value                                      |
|------------|--------------------|--------------------------------------------|
| Railway/Render | `GROQ_API_KEY`     | Your Groq API key                          |
| Railway/Render | `GROQ_MODEL`       | `llama-3.1-8b-instant` (optional)         |
| Vercel     | `VITE_API_BASE_URL` | Backend URL (e.g. `https://xxx.up.railway.app`) |

---

## Cost (free tier)

- **Vercel**: Free (frontend).
- **Railway**: Free trial credits, then usage-based (backend stays small with Groq).
- **Render**: Free tier for backend (spins down when idle).
- **Groq**: Free tier for API.

---

## Troubleshooting

**Frontend shows “Unable to connect to the server”**  
- Confirm `VITE_API_BASE_URL` in Vercel matches the backend URL exactly (no trailing slash).
- Redeploy frontend after changing env vars (Vite bakes `VITE_*` at build time).

**Backend 502 / not starting**  
- Check Railway/Render logs.
- Ensure `GROQ_API_KEY` is set.
- Ensure root directory is `backend` and Dockerfile is used.

**CORS errors**  
- Backend already uses `allow_origins=["*"]`. If you still see CORS errors, the request is likely going to the wrong URL; double-check `VITE_API_BASE_URL`.

**“llm_not_configured_placeholder” in results**  
- Backend env: `GROQ_API_KEY` must be set on Railway/Render and the service restarted after adding it.

---

## Optional: Run Docker locally (when you have Docker)

Once Docker works on your machine (e.g. after enabling virtualization):

```powershell
cd C:\Pharma_Guard\Pharma_Guard
# Use .env with GROQ_API_KEY
docker compose --env-file .env up --build
```

- Frontend: http://localhost  
- Backend: http://localhost:8000  

For production you keep using **Vercel + Railway/Render** as above.
