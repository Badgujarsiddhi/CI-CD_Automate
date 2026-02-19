# PharmaGuard - Docker Deployment with Ollama

Run the full PharmaGuard stack (Frontend, Backend, Ollama LLM) using Docker Compose.

## Prerequisites

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- **8 GB RAM** minimum (Ollama needs ~4–8 GB for llama3.2:3b)
- **10 GB disk space** for the Ollama model

## Quick Start

```bash
cd Pharma_Guard
docker compose up --build
```

- **Frontend**: http://localhost (port 80)
- **Backend API**: http://localhost:8000
- **Ollama**: http://localhost:11434 (optional direct access)

## First Run

On first start, Ollama will download the `llama3.2:3b` model (~2 GB). This can take 5–15 minutes depending on your connection. The backend will return placeholder LLM explanations until the model is ready.

Check model status:
```bash
docker exec pharmaguard-ollama ollama list
```

## Services

| Service | Port | Description |
|---------|------|-------------|
| frontend | 80 | React app (nginx) |
| backend | 8000 | FastAPI |
| ollama | 11434 | LLM server (llama3.2:3b) |

## Environment Variables

### Backend
- `OLLAMA_BASE_URL` — Ollama API URL (default: `http://ollama:11434`)
- `OLLAMA_MODEL` — Model name (default: `llama3.2:3b`)

### Frontend
- `VITE_API_BASE_URL` — API base URL; empty for same-origin (Docker default)

## Production Deployment

For production (e.g., cloud VPS):

1. Use a reverse proxy (e.g., Traefik, Caddy) for HTTPS
2. Consider increasing Ollama memory limits
3. Persist `ollama_data` volume for model caching
4. Set `restart: unless-stopped` (already in compose)

## Troubleshooting

**Ollama out of memory**  
Increase Docker memory limit or use a smaller model.

**Backend can't reach Ollama**  
Ensure all services are on the same Docker network (default with compose).

**Model not loading**  
Manually pull: `docker exec -it pharmaguard-ollama ollama pull llama3.2:3b`
