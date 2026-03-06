<div align="center">

# 🎨 LAF mHub — AI Wall Mural Design Engine

**Upload a wall photo → AI detects the surface → Generate stunning mural previews → Get print-ready panels**

Built for [Lakshmi Art Fixers](https://lakshmi-arts.vercel.app) · Telangana & Andhra Pradesh

[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18+-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![SDXL](https://img.shields.io/badge/Stable_Diffusion-XL-FF6F00?logo=stability-ai&logoColor=white)](https://stability.ai)

</div>

---

## 🔥 What It Does

LAF mHub is an AI-powered mural visualization tool that lets homeowners and designers **see how wall art will look on their actual walls** before committing to expensive installations.

```
📸 Wall Photo → 🧠 SAM Wall Detection → 🎨 SDXL Generation → 🖼️ Perspective Warp → 🖨️ Print Panels
```

### The Pipeline

| Step | Technology | What Happens |
|------|-----------|--------------|
| **Upload** | FastAPI + Pillow | User uploads a wall photo |
| **Auto-Detect** | Meta SAM (`sam-vit-base`) | AI segments wall surfaces into selectable polygons |
| **Depth Map** | Intel MiDaS (`dpt-large`) | Extracts room geometry for perspective-correct generation |
| **Generate** | SDXL + ControlNet Depth | Creates mural art that respects wall plane and room geometry |
| **Composite** | OpenCV Homography | Warps artwork to match wall perspective + lighting |
| **Print Panels** | Pillow | Slices output into 60cm strips at 150 DPI for print shops |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- ~20GB disk space (for AI models on first run)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Pre-download AI models (one-time, ~20GB)
python preload_models.py

# Start the server with REAL AI pipeline
USE_MOCK_PIPELINE=False uvicorn main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev -- --port 5174
```

Open **http://localhost:5174** and upload a wall photo!

---

## 📱 Mobile-First

- **Camera Capture** — "Take a Photo" button opens the rear camera on mobile
- **Touch Drawing** — Tap and drag to select the wall area (PointerEvents API)
- **PWA-Ready** — Add to Home Screen for a native app feel
- **Safe Area Support** — Respects iPhone notch and home indicator

---

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│                 React Frontend               │
│  Upload → Tag → Print Area → Style → Result  │
├──────────────────────────────────────────────┤
│              FastAPI Backend                  │
│  ┌─────────┐  ┌───────────┐  ┌───────────┐  │
│  │ Wall    │  │ Style     │  │ Design    │  │
│  │ Agent   │  │ Agent     │  │ Agent     │  │
│  └────┬────┘  └─────┬─────┘  └─────┬─────┘  │
│       │             │              │         │
│  ┌────┴─────────────┴──────────────┴──────┐  │
│  │        Advanced Mural Pipeline         │  │
│  │  SAM → MiDaS → SDXL+ControlNet →     │  │
│  │  Perspective Warp → Lighting Match    │  │
│  └───────────────────────────────────────┘  │
├──────────────────────────────────────────────┤
│          Async Task Queue                    │
│  POST /generate → task_id → GET /status     │
└──────────────────────────────────────────────┘
```

---

## 🎯 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/wall/upload` | Upload wall image |
| `GET`  | `/api/wall/{id}` | Get wall data |
| `POST` | `/api/wall/{id}/tags` | Update room/surface tags |
| `POST` | `/api/wall/{id}/print-area` | Set print area coordinates |
| `POST` | `/api/wall/{id}/detect-walls` | Run SAM auto-detection |
| `POST` | `/api/wall/generate` | Queue mural generation (returns `task_id`) |
| `GET`  | `/api/wall/status/{task_id}` | Poll generation status |
| `GET`  | `/api/styles` | Get available style presets |

---

## 💰 Business Model

| Revenue Stream | How It Works |
|---|---|
| **Visualization Fees** | ₹499–₹4999 for AI mural previews (Basic/Pro/Studio) |
| **Service Conversion** | Previews → WhatsApp handoff → site visit → installation booking |
| **Marketplace** | Creators list designs; platform takes 20% commission |

---

## 🛣️ Roadmap

See [GitHub Issues](https://github.com/gypse007/LAF_mHub/issues) for the active roadmap.

**Key Milestones:**
- [x] Core pipeline (Upload → Tag → Area → Style → Generate → Result)
- [x] Real SDXL + ControlNet + SAM integration
- [x] Async generation with polling
- [x] Mobile-first responsive UI with camera capture
- [ ] Cloud GPU deployment (Replicate/Modal) for <10s generation
- [ ] OpenClaw AI Concierge (chat-based mural design)
- [ ] WhatsApp integration for lead handoff
- [ ] Payment gateway (Razorpay) for visualization fees
- [ ] Creator marketplace

---

## 🧪 Tech Stack

**Backend:** Python · FastAPI · PyTorch · Diffusers · Transformers · OpenCV · Pillow
**Frontend:** React 18 · TypeScript · Vite · Vanilla CSS
**AI Models:** Stable Diffusion XL · ControlNet Depth · Meta SAM · Intel MiDaS

---

## 📄 License

Proprietary — Lakshmi Art Fixers. All rights reserved.
