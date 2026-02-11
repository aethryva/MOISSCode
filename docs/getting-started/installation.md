# Installation Guide

## Prerequisites

- **Python 3.10+**  - [Download here](https://www.python.org/downloads/)
- **pip**  - Comes with Python automatically

---

## Quick Setup (Recommended)

### 1. Get the Code

**Option A: Clone from GitHub**
```bash
git clone https://github.com/aethryva/moisscode.git
cd moisscode
```

**Option B: Already have the files?**
Open a terminal and navigate to your project folder:
```bash
cd "c:\Aethryva Code"
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the Engine

```bash
python api.py
```

You should see:
```
Aethryva Deeptech | MOISSCode Engine v1.0
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 4. Test It

Open your browser to [http://localhost:8000/docs](http://localhost:8000/docs) to see the API documentation.

---

## Run a MOISS Script

You can run any `.moiss` file directly:

```bash
python run_moiss.py examples/full_test.moiss
```

---

## Run with the Visual Dashboard

To start the web dashboard alongside the engine:

**Windows:**
```bash
start_moisscode.bat
```

This starts both:
- **Engine** at `http://localhost:8000`
- **Dashboard** at `http://localhost:3000`
