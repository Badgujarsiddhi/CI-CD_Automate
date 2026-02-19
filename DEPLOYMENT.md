# Deployment Guide for PharmaGuide

This guide explains how to deploy the PharmaGuide application with Ollama LLM support on Vercel.

## Architecture Overview

The application consists of:
- **Frontend**: React/Vite application
- **Backend**: FastAPI Python application
- **LLM**: Ollama (hosted separately, accessed via API)

## Important Note: Ollama Deployment

**Vercel cannot run Ollama models directly** because:
- Vercel is a serverless platform with execution time limits
- Ollama models require persistent storage and memory
- Model files are too large for serverless functions

### Solution: Separate Ollama Service

You have two options:

#### Option 1: Host Ollama on a Separate Service (Recommended)

Deploy Ollama on a service that supports long-running processes:
- **Railway** (recommended for simplicity)
- **Render**
- **Fly.io**
- **DigitalOcean App Platform**
- **Your own VPS/server**

Then configure your Vercel deployment to call the Ollama API.

#### Option 2: Use Ollama Cloud API

Use a managed Ollama service if available, or run Ollama locally for development.

## Setup Instructions

### 1. Install and Configure Ollama Locally (for Development)

1. **Install Ollama**: Download from https://ollama.ai

2. **Pull a suitable model for 8GB RAM**:
   ```bash
   # Recommended models for pharmacogenomics on 8GB RAM:
   ollama pull llama3.2:3b        # ~2GB, fast, good for structured tasks
   # OR
   ollama pull mistral:7b         # ~4GB, better reasoning, requires more RAM
   # OR
   ollama pull phi3:mini          # ~2GB, Microsoft model, good for medical
   ```

3. **Start Ollama** (runs on http://localhost:11434 by default):
   ```bash
   ollama serve
   ```

4. **Test the API**:
   ```bash
   curl http://localhost:11434/api/chat -d '{
     "model": "llama3.2:3b",
     "messages": [{"role": "user", "content": "Hello"}]
   }'
   ```

### 2. Configure Environment Variables

Create a `.env` file in the backend directory (for local development):

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

For production (Vercel), set these as environment variables in the Vercel dashboard:
- `OLLAMA_BASE_URL`: Your Ollama service URL (e.g., `https://your-ollama-service.railway.app`)
- `OLLAMA_MODEL`: Model name (e.g., `llama3.2:3b`)

### 3. Deploy Ollama Service (Example: Railway)

1. **Create a Railway account** at https://railway.app

2. **Create a new project** and add a service

3. **Use Railway's Docker template** or create a `Dockerfile`:
   ```dockerfile
   FROM ollama/ollama:latest
   EXPOSE 11434
   ```

4. **Deploy** and note the public URL

5. **Pull the model** on the deployed service:
   ```bash
   # SSH into Railway or use their CLI
   ollama pull llama3.2:3b
   ```

### 4. Deploy to Vercel

1. **Install Vercel CLI** (if not already installed):
   ```bash
   npm i -g vercel
   ```

2. **Login to Vercel**:
   ```bash
   vercel login
   ```

3. **Set environment variables**:
   ```bash
   vercel env add OLLAMA_BASE_URL
   vercel env add OLLAMA_MODEL
   ```

4. **Deploy**:
   ```bash
   vercel --prod
   ```

   Or connect your GitHub repository to Vercel for automatic deployments.

### 5. Frontend Deployment

The frontend should be built and served by Vercel. Update `vercel.json` routes if needed to serve static files from the `frontend/dist` directory after building.

## Model Recommendations for Pharmacogenomics

For an 8GB laptop, these models work well:

1. **llama3.2:3b** (Recommended)
   - Size: ~2GB
   - Good for structured explanations
   - Fast inference
   - Command: `ollama pull llama3.2:3b`

2. **mistral:7b**
   - Size: ~4GB
   - Better reasoning capabilities
   - Requires more RAM
   - Command: `ollama pull mistral:7b`

3. **phi3:mini**
   - Size: ~2GB
   - Good for medical/clinical tasks
   - Command: `ollama pull phi3:mini`

## Testing

1. **Test locally**:
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. **Test Ollama connection**:
   ```bash
   curl http://localhost:11434/api/chat -d '{
     "model": "llama3.2:3b",
     "messages": [{"role": "user", "content": "Explain pharmacogenomics"}]
   }'
   ```

3. **Test the API endpoint**:
   ```bash
   curl -X POST http://localhost:8000/api/analyze \
     -F "vcf_file=@test.vcf" \
     -F "drugs=WARFARIN"
   ```

## Troubleshooting

### Ollama Connection Issues

- **Check Ollama is running**: `curl http://localhost:11434/api/tags`
- **Verify model is pulled**: `ollama list`
- **Check environment variables**: Ensure `OLLAMA_BASE_URL` is set correctly
- **Network issues**: If deploying on separate services, ensure CORS is configured

### Vercel Deployment Issues

- **Python version**: Ensure Python 3.11+ is available
- **Dependencies**: Check that all packages in `requirements.txt` are compatible
- **Timeout**: Vercel has a 10s timeout for Hobby plan, 60s for Pro. Ollama calls may take longer - consider using background jobs or increasing timeout

### Performance Optimization

- Use smaller models (3B parameters) for faster responses
- Consider caching LLM responses for similar queries
- Use streaming responses if supported by your frontend

## Alternative: Using Ollama Cloud (if available)

If Ollama Cloud or similar services become available, you can use them instead of self-hosting:

```env
OLLAMA_BASE_URL=https://api.ollama.cloud
OLLAMA_API_KEY=your_api_key
```

Update `main.py` to include API key authentication if needed.
