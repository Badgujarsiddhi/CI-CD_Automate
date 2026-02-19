# PharmaGuard Deployment Guide

This guide covers deploying PharmaGuard with Docker and Ollama to various cloud platforms.

## Prerequisites

- Docker and Docker Compose installed locally (for testing)
- Git repository (GitHub, GitLab, etc.)
- Account on your chosen cloud platform

---

## Option 1: Railway (Recommended - Easiest)

Railway supports Docker Compose and is the simplest option.

### Steps:

1. **Push code to GitHub**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git remote add origin <your-github-repo-url>
   git push -u origin main
   ```

2. **Deploy on Railway**
   - Go to [railway.app](https://railway.app)
   - Sign up/login with GitHub
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway will detect `docker-compose.yml`
   - **Important**: Railway may need adjustments:
     - Go to project settings → "Variables"
     - Set memory limit to **8GB** minimum
     - Railway will deploy all services automatically

3. **Configure Ollama Model**
   - After deployment, open Railway dashboard
   - Click on the `ollama` service
   - Open "Logs" tab
   - Wait for model download to complete (~5-15 min)
   - Or SSH into container: `railway run ollama pull llama3.2:3b`

4. **Access Your App**
   - Railway provides a public URL (e.g., `yourapp.up.railway.app`)
   - Frontend will be available at that URL

**Cost**: ~$20-40/month (depends on RAM usage)

---

## Option 2: Render (Good Alternative)

Render supports Docker but requires separate services.

### Steps:

1. **Push to GitHub** (same as Railway)

2. **Create Services on Render**
   
   **a) Ollama Service:**
   - Go to [render.com](https://render.com)
   - New → "Web Service"
   - Connect GitHub repo
   - Settings:
     - **Name**: `pharmaguard-ollama`
     - **Environment**: Docker
     - **Dockerfile Path**: (create a simple one, see below)
     - **Instance Type**: Standard (8GB RAM)
     - **Health Check Path**: `/api/tags`
   
   **b) Backend Service:**
   - New → "Web Service"
   - Settings:
     - **Name**: `pharmaguard-backend`
     - **Environment**: Docker
     - **Dockerfile Path**: `backend/Dockerfile`
     - **Environment Variables**:
       - `OLLAMA_BASE_URL`: `http://pharmaguard-ollama:11434`
       - `OLLAMA_MODEL`: `llama3.2:3b`
   
   **c) Frontend Service:**
   - New → "Static Site" or "Web Service"
   - If Web Service: Use `frontend/Dockerfile`
   - If Static Site: Build command: `npm run build`, Publish: `dist`

3. **Note**: Render services communicate via internal network. Update `OLLAMA_BASE_URL` to use Render's internal hostname.

**Cost**: ~$25-50/month (Ollama needs 8GB instance)

---

## Option 3: Fly.io (Good for Docker)

Fly.io excels at Docker deployments.

### Steps:

1. **Install Fly CLI**
   ```bash
   # Windows (PowerShell)
   iwr https://fly.io/install.ps1 -useb | iex
   ```

2. **Create Fly App**
   ```bash
   cd Pharma_Guard
   fly launch
   ```
   - Follow prompts
   - Select region
   - **Important**: Fly.io doesn't support docker-compose directly
   - You'll need to deploy services separately or use Fly's multi-machine setup

3. **Deploy Ollama**
   ```bash
   fly apps create pharmaguard-ollama
   fly deploy -c fly.ollama.toml  # Create this config
   ```

4. **Deploy Backend**
   ```bash
   fly apps create pharmaguard-backend
   fly deploy -c fly.backend.toml
   ```

5. **Deploy Frontend**
   ```bash
   fly apps create pharmaguard-frontend
   fly deploy -c fly.frontend.toml
   ```

**Cost**: ~$15-30/month (pay for what you use)

---

## Option 4: DigitalOcean App Platform

### Steps:

1. **Push to GitHub**

2. **Create App on DigitalOcean**
   - Go to [cloud.digitalocean.com](https://cloud.digitalocean.com)
   - Apps → Create App → GitHub
   - Select repository

3. **Configure Services**
   - DigitalOcean will detect Docker Compose
   - **Important**: Set Ollama service to **8GB RAM** minimum
   - Set environment variables for backend

4. **Deploy**
   - Click "Create Resources"
   - Wait for deployment (~10-20 min)

**Cost**: ~$24-48/month (8GB droplet)

---

## Option 5: Self-Hosted VPS (Most Control)

Deploy on your own server (DigitalOcean Droplet, AWS EC2, Hetzner, etc.).

### Steps:

1. **Create VPS**
   - Minimum: **8GB RAM, 2 CPU cores, 50GB disk**
   - OS: Ubuntu 22.04 LTS

2. **SSH into Server**
   ```bash
   ssh root@your-server-ip
   ```

3. **Install Docker**
   ```bash
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   apt install docker-compose-plugin -y
   ```

4. **Clone Repository**
   ```bash
   git clone <your-repo-url>
   cd Pharma_Guard
   ```

5. **Deploy**
   ```bash
   docker compose up -d --build
   ```

6. **Set Up Reverse Proxy (Nginx)**
   ```bash
   apt install nginx certbot python3-certbot-nginx -y
   # Configure nginx to proxy to localhost:80
   certbot --nginx -d yourdomain.com
   ```

7. **Access App**
   - Frontend: `http://yourdomain.com`
   - Backend: `http://yourdomain.com/api`

**Cost**: ~$12-24/month (VPS)

---

## Option 6: AWS/GCP/Azure (Enterprise)

For production at scale:

- **AWS**: Use ECS (Elastic Container Service) with Fargate
- **GCP**: Use Cloud Run or GKE (Google Kubernetes Engine)
- **Azure**: Use Container Instances or AKS

These require more setup but offer better scaling and reliability.

---

## Quick Test Before Deploying

Test locally first:

```bash
cd Pharma_Guard
docker compose up --build
```

- Frontend: http://localhost
- Backend: http://localhost:8000
- Ollama: http://localhost:11434

Check logs:
```bash
docker compose logs ollama  # Wait for model download
docker compose logs backend
docker compose logs frontend
```

---

## Environment Variables Reference

### Backend (FastAPI)
```env
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2:3b
```

### Frontend (React)
```env
VITE_API_BASE_URL=  # Empty for same-origin (Docker)
# OR for separate domains:
VITE_API_BASE_URL=https://your-backend-url.com
```

---

## Troubleshooting

**Ollama out of memory**
- Increase container memory limit to 8GB+
- Or use a smaller model: `llama3.2:1b`

**Backend can't reach Ollama**
- Ensure services are on same Docker network
- Check `OLLAMA_BASE_URL` environment variable
- Verify Ollama is running: `docker compose ps`

**Model not loading**
- Check Ollama logs: `docker compose logs ollama`
- Manually pull: `docker exec pharmaguard-ollama ollama pull llama3.2:3b`
- Wait for download (first time takes 5-15 min)

**Frontend can't reach backend**
- Check nginx proxy configuration
- Verify backend is running: `docker compose ps backend`
- Check browser console for CORS errors

---

## Recommended for Beginners

**Start with Railway** - It's the easiest:
1. Push to GitHub
2. Connect Railway to repo
3. Railway handles everything automatically
4. Just wait for Ollama model to download

---

## Cost Comparison

| Platform | Monthly Cost | Difficulty | Best For |
|----------|--------------|------------|----------|
| Railway | $20-40 | ⭐ Easy | Quick deployment |
| Render | $25-50 | ⭐⭐ Medium | Separate services |
| Fly.io | $15-30 | ⭐⭐ Medium | Docker experts |
| DigitalOcean | $24-48 | ⭐⭐ Medium | App Platform users |
| VPS | $12-24 | ⭐⭐⭐ Hard | Full control |
| AWS/GCP | $30-100+ | ⭐⭐⭐⭐ Very Hard | Enterprise |

---

## Next Steps

1. Choose a platform
2. Push code to GitHub
3. Follow platform-specific steps above
4. Test deployment
5. Monitor logs for errors
6. Enjoy your deployed app! 🚀
