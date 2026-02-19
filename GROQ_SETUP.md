# Groq API Setup Guide

PharmaGuard now uses **Groq API** instead of Ollama for LLM explanations. This means:
- ✅ **No model download needed** (faster startup)
- ✅ **Free tier available** (14,400 requests/day)
- ✅ **Much faster inference** (GPU-powered)
- ✅ **Lower memory requirements** (no need for 8GB RAM)

---

## Step 1: Get Groq API Key (Free)

1. **Sign up**: Go to [console.groq.com](https://console.groq.com)
   - Click "Sign Up" or "Get Started"
   - Use Google/GitHub to sign in (fastest)

2. **Create API Key**:
   - Go to [API Keys](https://console.groq.com/keys)
   - Click "Create API Key"
   - Give it a name (e.g., "PharmaGuard")
   - **Copy the key immediately** (you won't see it again!)

3. **Free Tier Limits**:
   - **14,400 requests/day** (600 requests/hour)
   - Models: `llama-3.1-8b-instant`, `llama-3.1-70b-versatile`, `mixtral-8x7b-32768`
   - **No credit card required** for free tier

---

## Step 2: Set Environment Variable

### Option A: Local Development (Docker Compose)

Create a `.env` file in `Pharma_Guard` directory:

```bash
GROQ_API_KEY=your-api-key-here
GROQ_MODEL=llama-3.1-8b-instant
```

Then run:
```bash
docker compose --env-file .env up --build
```

### Option B: Local Development (Direct)

Set environment variable:

**Windows (PowerShell)**:
```powershell
$env:GROQ_API_KEY="your-api-key-here"
$env:GROQ_MODEL="llama-3.1-8b-instant"
```

**Windows (CMD)**:
```cmd
set GROQ_API_KEY=your-api-key-here
set GROQ_MODEL=llama-3.1-8b-instant
```

**Linux/Mac**:
```bash
export GROQ_API_KEY="your-api-key-here"
export GROQ_MODEL="llama-3.1-8b-instant"
```

### Option C: Cloud Deployment

Set environment variable in your hosting platform:

- **Railway**: Project → Variables → Add `GROQ_API_KEY`
- **Render**: Service → Environment → Add `GROQ_API_KEY`
- **Fly.io**: `fly secrets set GROQ_API_KEY=your-key`
- **DigitalOcean**: App → Settings → Environment Variables

---

## Step 3: Test Locally

```bash
cd Pharma_Guard
docker compose --env-file .env up --build
```

Visit: http://localhost

Upload a VCF file and analyze a drug. You should see LLM explanations generated via Groq!

---

## Available Groq Models

| Model | Speed | Quality | Free Tier |
|-------|-------|---------|-----------|
| `llama-3.1-8b-instant` | ⚡⚡⚡ Very Fast | ⭐⭐⭐ Good | ✅ Yes |
| `llama-3.1-70b-versatile` | ⚡⚡ Fast | ⭐⭐⭐⭐ Excellent | ✅ Yes |
| `mixtral-8x7b-32768` | ⚡⚡ Fast | ⭐⭐⭐⭐ Excellent | ✅ Yes |

**Recommended**: `llama-3.1-8b-instant` (fastest, good quality, free)

---

## Troubleshooting

### "llm_not_configured_placeholder" in results

**Problem**: Groq API key not set or invalid.

**Solution**:
1. Check environment variable: `echo $GROQ_API_KEY` (Linux/Mac) or `echo %GROQ_API_KEY%` (Windows)
2. Verify key is correct in Groq console
3. Restart Docker containers: `docker compose restart backend`

### "llm_error_placeholder" in results

**Problem**: API request failed (rate limit, network, etc.)

**Solution**:
1. Check Groq API status: [status.groq.com](https://status.groq.com)
2. Check rate limits in Groq console
3. Wait a few minutes and try again
4. Check backend logs: `docker compose logs backend`

### Rate Limit Exceeded

**Problem**: Free tier limit reached (14,400 requests/day).

**Solution**:
- Wait until next day (resets at midnight UTC)
- Or upgrade to paid tier for higher limits

---

## Cost Comparison

| Option | Cost | Setup Time | Speed |
|--------|------|------------|-------|
| **Groq API** | $0 (free tier) | 2 minutes | ⚡⚡⚡ Very Fast |
| Ollama (local) | $0 | 15+ min (model download) | ⚡⚡ Fast |
| Ollama (cloud) | $20-40/month | 30+ minutes | ⚡⚡ Fast |

**Groq API is the best free option!** 🎉

---

## Next Steps

1. ✅ Get Groq API key
2. ✅ Set `GROQ_API_KEY` environment variable
3. ✅ Deploy with Docker Compose
4. ✅ Test your app!

For deployment instructions, see `DEPLOYMENT_FREE.md`.
