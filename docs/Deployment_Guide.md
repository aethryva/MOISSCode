# MOISSCode Deployment Guide

## 1. Local Development (Quickest Way)

### Start the Engine Only
```bash
python api.py
```
- API available at `http://localhost:8000`
- API docs at `http://localhost:8000/docs`

### Start Engine + Dashboard
```bash
start_moisscode.bat
```
- Engine at `http://localhost:8000`
- Dashboard at `http://localhost:3000`

### Run a Script Directly
```bash
python run_moiss.py examples/full_test.moiss
```

---

## 2. Docker Deployment

### Prerequisites
- Docker Desktop installed

### Launch
```bash
docker-compose -f deployment/docker-compose.yml up --build
```

### `docker-compose.yml`
```yaml
services:
  api:
    build: ..
    ports:
      - "8000:8000"
    environment:
      - MOISS_ENV=production

  frontend:
    build: ../moiss-web
    ports:
      - "3000:3000"
    depends_on:
      - api
```

---

## 3. Cloud Deployment

### Option A: Railway (Free Tier)
1. Push to GitHub
2. Go to [railway.app](https://railway.app)
3. Click "New Project" → "Deploy from GitHub repo"
4. Select your repo
5. Done  - Railway auto-detects Python and deploys

### Option B: Render (Free Tier)
1. Push to GitHub
2. Go to [render.com](https://render.com)
3. Create a "Web Service"
4. Connect your GitHub repo
5. Set start command: `python api.py`
6. Deploy

---

## 4. Security Notes

- **The Engine is stateless**  - no patient data is stored permanently.
- **Always use `med.research.deidentify(p)`** before logging or exporting data.
- **Enable HTTPS** in production (all cloud providers do this automatically).
