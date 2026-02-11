---
sidebar_position: 11
title: Deployment
---

# Deployment

## Local Development

```bash
pip install -e .
moiss run examples/phase3_demo.moiss -v
```

## API Server

```bash
pip install -e ".[api]"
uvicorn api:app --host 0.0.0.0 --port 8000
```

POST to `/run`:
```json
{
  "code": "protocol Test { input: Patient p; assess p for sepsis; }"
}
```

## Docker

```bash
cd deployment
docker-compose up --build
```

## Cloud Deployment

### Railway (Free Tier)

1. Push to GitHub
2. Go to [railway.app](https://railway.app) → "New Project" → "Deploy from GitHub"
3. Select your repo
4. Set start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`

### Render

1. Push to GitHub
2. Go to [render.com](https://render.com) → "New Web Service"
3. Connect repo
4. Build command: `pip install -e ".[api]"`
5. Start command: `uvicorn api:app --host 0.0.0.0 --port $PORT`
