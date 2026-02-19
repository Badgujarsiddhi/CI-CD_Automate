# PharmaGuard - Docker Deployment with Groq API

Run the full PharmaGuard stack (Frontend, Backend, Groq LLM API) using Docker Compose.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- **Groq API Key** (free tier available) - Get from [console.groq.com](https://console.groq.com/keys)
- **2 GB RAM** minimum (much less than Ollama!)

## Quick Start

1. **Get Groq API Key**:
   - Sign up at [console.groq.com](https://console.groq.com)
   - Create API key at [API Keys](https://console.groq.com/keys)
   - Copy your key

2. **Create `.env` file**:
   ```bash
   cp .env.example .env
   # Edit .env and add your GROQ_API_KEY
   ```

3. **Start services**:
   ```bash
   cd Pharma_Guard
   docker compose --env-file .env up --build
   ```

- **Frontend**: http://localhost (port 80)
- **Backend API**: http://localhost:8000

## First Run

No model download needed! Groq API is cloud-based, so startup is instant (~30 seconds).

## Services

| Service | Port | Description |
|---------|------|-------------|
| frontend | 80 | React app (nginx) |
| backend | 8000 | FastAPI with Groq API |

## Environment Variables

### Backend
- `GROQ_API_KEY` — **Required** - Your Groq API key from [console.groq.com](https://console.groq.com/keys)
- `GROQ_MODEL` — Model name (default: `llama-3.1-8b-instant`)

Available models:
- `llama-3.1-8b-instant` - Fastest, recommended (default)
- `llama-3.1-70b-versatile` - Better quality
- `mixtral-8x7b-32768` - Excellent quality

### Frontend
- `VITE_API_BASE_URL` — API base URL; empty for same-origin (Docker default)

## Groq Free Tier

- ✅ **14,400 requests/day** (600/hour)
- ✅ **No credit card required**
- ✅ **Fast GPU inference**
- ✅ **Multiple models available**

See [GROQ_SETUP.md](./GROQ_SETUP.md) for detailed setup instructions.

## Production Deployment

For production (e.g., cloud VPS):

1. Use a reverse proxy (e.g., Traefik, Caddy) for HTTPS
2. Set `GROQ_API_KEY` as environment variable in your hosting platform
3. Set `restart: unless-stopped` (already in compose)
4. Monitor Groq API usage in [console.groq.com](https://console.groq.com)

## Troubleshooting

**"llm_not_configured_placeholder" in results**  
- Check `GROQ_API_KEY` is set: `echo $GROQ_API_KEY` (Linux/Mac) or `echo %GROQ_API_KEY%` (Windows)
- Verify key is correct in Groq console
- Restart backend: `docker compose restart backend`

**"llm_error_placeholder" in results**  
- Check Groq API status: [status.groq.com](https://status.groq.com)
- Check rate limits in Groq console
- Check backend logs: `docker compose logs backend`

**Rate limit exceeded**  
- Free tier: 14,400 requests/day
- Wait until next day (resets at midnight UTC)
- Or upgrade to paid tier

## Advantages Over Ollama

| Feature | Groq API | Ollama |
|---------|----------|--------|
| Setup time | 2 minutes | 15+ minutes |
| RAM needed | 2 GB | 8 GB |
| Model download | None | 2-10 GB |
| Speed | ⚡⚡⚡ Very Fast | ⚡⚡ Fast |
| Cost | $0 (free tier) | $0 (but needs VPS) |

## Next Steps

1. ✅ Get Groq API key from [console.groq.com](https://console.groq.com/keys)
2. ✅ Set `GROQ_API_KEY` in `.env` file
3. ✅ Run `docker compose up --build`
4. ✅ Test at http://localhost

For deployment to cloud platforms, see [DEPLOYMENT_FREE.md](./DEPLOYMENT_FREE.md).
