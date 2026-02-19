# Free Deployment Options for PharmaGuard

Ollama requires **4-8GB RAM**, which most free tiers don't provide. Here are realistic free options:

---

## Option 1: Free VPS Trials (Best Option)

### Oracle Cloud Free Tier ⭐⭐⭐⭐⭐
**Best free option - includes 4GB RAM VPS**

1. **Sign up**: [cloud.oracle.com](https://cloud.oracle.com)
   - Requires credit card (won't be charged)
   - Free tier includes:
     - **2 VMs with 1/8 OCPU and 1GB RAM each** (ARM)
     - OR **1 VM with 1 OCPU and 1GB RAM** (x86)
     - **200GB storage**
     - **10TB egress bandwidth/month**

2. **Create Instance**:
   - Choose **ARM-based Ampere A1** (better for free tier)
   - Select **2 OCPUs, 12GB RAM** (free tier allows this!)
   - OS: Ubuntu 22.04
   - Add SSH key

3. **Deploy**:
   ```bash
   ssh opc@your-instance-ip
   curl -fsSL https://get.docker.com -o get-docker.sh
   sh get-docker.sh
   apt install docker-compose-plugin -y
   
   git clone <your-repo-url>
   cd Pharma_Guard
   docker compose up -d --build
   ```

**Cost**: $0/month (permanently free)
**Limitations**: ARM architecture (may need to rebuild images)

---

### Google Cloud Free Tier ⭐⭐⭐⭐
**$300 free credits for 90 days**

1. **Sign up**: [cloud.google.com](https://cloud.google.com)
   - Get $300 free credits (90 days)
   - Create VM instance:
     - **e2-medium**: 2 vCPU, 4GB RAM
     - Ubuntu 22.04
     - **Cost**: ~$30/month → Free for ~10 months with credits

2. **Deploy**:
   ```bash
   # Same as Oracle Cloud steps above
   ```

**Cost**: $0 for 90 days, then ~$30/month
**Best for**: Testing/learning

---

### AWS Free Tier ⭐⭐⭐
**12 months free, then pay**

1. **Sign up**: [aws.amazon.com](https://aws.amazon.com)
   - Free tier: **t2.micro** (1GB RAM) - **Too small for Ollama**
   - Need **t3.medium** (4GB RAM) - ~$30/month after free tier

**Cost**: $0 for 12 months (limited), then ~$30/month
**Note**: Free tier too small, need paid instance

---

## Option 2: Split Deployment (Free Frontend + Paid Backend)

### Frontend: Vercel (Free) ✅
**Deploy React app for free**

1. **Push frontend to GitHub**
2. **Deploy on Vercel**:
   - Go to [vercel.com](https://vercel.com)
   - Import GitHub repo (frontend folder)
   - Set environment variable: `VITE_API_BASE_URL=https://your-backend-url.com`
   - Deploy (free forever)

**Cost**: $0/month

### Backend + Ollama: Railway Free Trial ⭐⭐⭐
**$5 free credit, then pay**

1. **Deploy backend + Ollama on Railway**:
   - Sign up: [railway.app](https://railway.app)
   - Get $5 free credit
   - Deploy docker-compose.yml
   - **Cost**: ~$20/month after credit runs out

**Cost**: $0 for ~1 week, then ~$20/month

---

## Option 3: Local Development Server (Free Forever)

### Run on Your Own Computer ⭐⭐⭐⭐
**If you have a decent PC**

1. **Requirements**:
   - Windows/Mac/Linux
   - 8GB+ RAM
   - Docker Desktop installed

2. **Deploy Locally**:
   ```bash
   cd Pharma_Guard
   docker compose up -d
   ```

3. **Expose to Internet** (optional):
   - Use **ngrok** (free): `ngrok http 80`
   - Use **Cloudflare Tunnel** (free): `cloudflared tunnel --url http://localhost:80`
   - Use **localtunnel** (free): `npx localtunnel --port 80`

**Cost**: $0/month
**Limitations**: Your PC must be on, uses your bandwidth

---

## Option 4: Use Smaller Model (Free Tier Compatible)

### Replace Ollama with Free API ⭐⭐⭐⭐⭐
**Use free LLM APIs instead of Ollama**

### Option A: Groq API (Free Tier)
**Very fast, free tier available**

1. **Sign up**: [groq.com](https://groq.com)
   - Free tier: **14,400 requests/day**
   - Fast inference (no GPU needed)

2. **Update Backend**:
   ```python
   # Replace Ollama call with Groq API
   import groq
   client = groq.Groq(api_key=os.getenv("GROQ_API_KEY"))
   response = client.chat.completions.create(
       model="llama-3.1-8b-instant",  # Free model
       messages=[{"role": "user", "content": prompt}]
   )
   ```

3. **Deploy**:
   - Frontend: Vercel (free)
   - Backend: Railway free trial → Render free tier → Fly.io free tier

**Cost**: $0/month (within free tier limits)

---

### Option B: Together.ai (Free Credits)
**$25 free credits**

1. **Sign up**: [together.ai](https://together.ai)
   - Get $25 free credits
   - Use `meta-llama/Llama-3-8b-chat-hf` model

2. **Update Backend**: Similar to Groq

**Cost**: $0 for ~$25 worth of requests, then pay-as-you-go

---

### Option C: Hugging Face Inference API (Free)
**Limited but free**

1. **Sign up**: [huggingface.co](https://huggingface.co)
   - Free inference API
   - Limited requests/hour

2. **Update Backend**: Use HF API

**Cost**: $0/month (with rate limits)

---

## Option 5: Hybrid - Free Frontend + Minimal Backend

### Frontend: Netlify/Vercel (Free) ✅
### Backend: Render Free Tier ⭐⭐
**Limited but free**

1. **Render Free Tier**:
   - 750 hours/month free
   - **512MB RAM** - **Too small for Ollama**
   - But you can use free LLM API instead!

2. **Deploy**:
   - Frontend: Netlify/Vercel (free)
   - Backend: Render (free) + Groq API (free)
   - No Ollama needed!

**Cost**: $0/month

---

## Recommended Free Setup

### Best Combo: Oracle Cloud + Free LLM API ⭐⭐⭐⭐⭐

1. **Oracle Cloud Free Tier**:
   - 4GB RAM VPS (free forever)
   - Deploy backend + frontend

2. **Replace Ollama with Groq API**:
   - Free tier: 14,400 requests/day
   - Fast, no model download needed
   - Update backend to use Groq instead of Ollama

3. **Result**: 
   - **$0/month**
   - **Fully functional**
   - **No model download** (faster startup)

---

## Quick Comparison

| Option | Cost | RAM | Difficulty | Best For |
|--------|------|-----|------------|----------|
| **Oracle Cloud** | $0 | 4-12GB | ⭐⭐⭐ | Best free option |
| **Google Cloud Credits** | $0 (90 days) | 4GB | ⭐⭐⭐ | Testing |
| **Local PC + ngrok** | $0 | Your PC | ⭐⭐ | Development |
| **Vercel + Railway Trial** | $0 (1 week) | 8GB | ⭐⭐ | Quick demo |
| **Groq API + Render** | $0 | N/A | ⭐⭐ | No Ollama needed |
| **AWS Free Tier** | $0 (12mo) | 1GB | ⭐⭐⭐ | Too small |

---

## Step-by-Step: Oracle Cloud (Recommended)

### 1. Create Account
- Go to [cloud.oracle.com](https://cloud.oracle.com)
- Sign up (credit card required, won't charge)
- Verify email

### 2. Create Free Instance
- Dashboard → "Create a VM instance"
- **Shape**: VM.Standard.A1.Flex
- **OCPUs**: 2
- **Memory**: 12GB (free tier allows this!)
- **OS**: Ubuntu 22.04
- **Add SSH key** (generate with `ssh-keygen`)
- Click "Create"

### 3. SSH and Deploy
```bash
# SSH into instance
ssh opc@<your-instance-ip>

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker opc
sudo apt install docker-compose-plugin -y

# Logout and login again
exit
ssh opc@<your-instance-ip>

# Clone repo
git clone <your-github-repo-url>
cd Pharma_Guard

# Deploy
docker compose up -d --build

# Check logs
docker compose logs -f ollama  # Wait for model download
```

### 4. Access Your App
- Get public IP from Oracle Cloud dashboard
- Visit: `http://<your-ip>`
- Set up domain (optional): Use Cloudflare DNS (free)

**Cost**: $0/month forever!

---

## Alternative: Use Free LLM API (No Ollama)

If you want to avoid running Ollama entirely:

1. **Update backend** to use Groq API (free tier)
2. **Deploy frontend** on Vercel (free)
3. **Deploy backend** on Render free tier (512MB is enough for API calls)

**Total Cost**: $0/month

Would you like me to:
1. Create a version that uses Groq API instead of Ollama?
2. Provide Oracle Cloud setup instructions?
3. Set up the free LLM API integration?
