# MANGANEX AI — Manganese Exploration Platform

A clean, professional demo-ready full-stack application for AI-assisted manganese mineral prospectivity exploration.

## Stack
- Frontend: React + TypeScript + Vite + Tailwind CSS v4 + MapLibre GL
- Backend: FastAPI + SQLite + SQLAlchemy
- GIS: MapLibre with OpenStreetMap raster tiles, GeoJSON target/prospectivity layers
- Demo data: included; no API keys required

## Important
This application is a **prospectivity decision-support prototype**. Scores indicate model-estimated exploration priority and are not proof of mineral reserves.

## Run in VS Code

### 1. Backend
Open a terminal in `backend`:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Backend:
`http://127.0.0.1:8000`

API docs:
`http://127.0.0.1:8000/docs`

\
### 2. Frontend
Open a second terminal in `frontend`:

```powershell
npm install
npm run dev
```

Frontend:
`http://localhost:5173`

The GIS Explorer uses OpenStreetMap tiles, so an internet connection is required for the basemap. The application itself needs no external API key.

## Demo account
Use any email/password on the sign-in screen. This prototype keeps authentication local for easy evaluation.

## Main workflow
Dashboard → Manganese Prospectivity Map → inspect ranked targets → validate training data → field verification → reports.

## Manganese model status

The repository currently contains a replaceable manganese prediction interface and an optional Random Forest training workflow. No validated manganese-labelled dataset or trained estimator is included.

All current target rankings, map zones and prediction responses are explicitly marked `model_status: demo`. They are screening outputs for workflow evaluation, not confirmation of a manganese deposit.

Training CSV records must include:

```text
latitude,longitude,label
```

where `label=1` is a validated manganese occurrence and `label=0` is background. Optional features include manganese and iron concentrations, silica, alumina, terrain, magnetic, SAR and structural measurements. The API validates records but does not claim to train or evaluate a model without suitable data.

## Manganese API

Primary routes:

```text
GET  /api/manganese/targets
GET  /api/manganese/targets/{id}
GET  /api/manganese/prospectivity
POST /api/manganese/predict
POST /api/manganese/predict-batch
POST /api/manganese/upload-data
GET  /api/manganese/model/status
```

The original `/api/targets` and `/api/maps/prospectivity` routes remain available for compatibility.

## Project structure
```text
manganex-ai/
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.ts
├── backend/
│   ├── app/
│   ├── tests/
│   └── requirements.txt
└── README.md
```
