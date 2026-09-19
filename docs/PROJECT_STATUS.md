# Project status

## Working
- React/Vite frontend
- FastAPI backend
- Demo target API
- GeoJSON prospectivity API
- MapLibre GIS Explorer
- Target layer with clickable popups
- Prospectivity layer toggle
- Target search and map navigation
- Dashboard charts
- Responsive navigation
- Clear demo/validation disclaimer
- Manganese-first target, prediction and model-status routes
- Validated training CSV ingestion boundary
- Batch manganese prediction contract
- Configurable five-class prospectivity thresholds
- Optional Random Forest training workflow with measured holdout metrics

## Demo / prototype
- Authentication
- Satellite data
- Geological layers
- Terrain processing
- Reports
- Current target/map rankings and predictions

These are represented as evaluation-ready workflow screens and demo data. Connect real providers, storage and trained models before operational use.

## Model and dataset limitation

No validated manganese-labelled training dataset or trained estimator is included in this repository. The model status is `demo`, metrics are absent, and synthetic/demo rankings must not be described as confirmed deposits. The training package is ready to consume validated records when they become available.

## Primary API

The manganese namespace is the active frontend data path:

- `/api/manganese/targets`
- `/api/manganese/targets/{id}`
- `/api/manganese/prospectivity`
- `/api/manganese/predict`
- `/api/manganese/predict-batch`
- `/api/manganese/upload-data`
- `/api/manganese/model/status`

## GIS Explorer
The map is intentionally implemented with a native MapLibre map rather than a screenshot. It loads OpenStreetMap raster tiles and overlays application-owned GeoJSON layers from the FastAPI backend.
