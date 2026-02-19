# Quick Start Guide

## Local Development Setup

### 1. Install Ollama

Download and install Ollama from https://ollama.ai

### 2. Pull a Model (for 8GB RAM)

```bash
# Recommended: llama3.2:3b (~2GB)
ollama pull llama3.2:3b

# Or try mistral:7b (~4GB) for better quality
ollama pull mistral:7b
```

### 3. Start Ollama

```bash
ollama serve
```

Ollama will run on `http://localhost:11434` by default.

### 4. Set Up Backend

```bash
cd backend
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the `backend` directory:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2:3b
```

### 6. Run the Backend

```bash
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

### 7. Test the Setup

```bash
# Test Ollama is running
curl http://localhost:11434/api/tags

# Test the API endpoint
curl -X POST http://localhost:8000/api/analyze \
  -F "vcf_file=@your_test.vcf" \
  -F "drugs=WARFARIN"
```

## Model Recommendations

For pharmacogenomics on an 8GB laptop:

| Model | Size | Speed | Quality | Command |
|-------|------|-------|---------|---------|
| llama3.2:3b | ~2GB | Fast | Good | `ollama pull llama3.2:3b` |
| phi3:mini | ~2GB | Fast | Good (medical) | `ollama pull phi3:mini` |
| mistral:7b | ~4GB | Medium | Better | `ollama pull mistral:7b` |

**Recommendation**: Start with `llama3.2:3b` - it's fast, uses less RAM, and works well for structured explanations.

## Production Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

**Key Points**:
- Ollama must be hosted separately (Railway, Render, Fly.io, etc.)
- Set `OLLAMA_BASE_URL` environment variable in Vercel to point to your Ollama service
- Set `OLLAMA_MODEL` to your chosen model name
