# MANGANEX AI - User Guide

## Quick Start

**Access the application:**
- Open your browser to: http://localhost:5173

## Main Features

### 1. **Dashboard (Overview)**
The home screen showing:
- **Exploration workspace intro** with "Open GIS Explorer" button
- **4 Stat Cards:**
  - Priority targets (total count)
  - High prospectivity areas (requires field validation)
  - Data layers (8 satellite, geology & terrain inputs)
  - Model status (Ready - demo inference pipeline)
- **Prospectivity distribution** - bar chart showing target breakdown by zone (High/Medium/Low)
- **Top targets** - ranked list of highest-priority exploration targets

**How to use:**
1. Review the workspace summary
2. Check stat cards for quick insights
3. Click "Open GIS Explorer" to explore on a map

---

### 2. **GIS Explorer (Interactive Map)**
An interactive mapping interface for spatial exploration:

**Map Features:**
- **Basemap:** OpenStreetMap raster tiles
- **Target layer:** Red (High), Orange (Medium), Gray (Low) priority points
- **Prospectivity zones:** Colored polygons showing estimated exploration priority areas

**Controls:**
- **Search:** Type target code (MN-001) or name to zoom to location
- **Zoom buttons:** + / - buttons in bottom-right to zoom in/out
- **Reset map:** "Locate" button returns to full Central & Eastern India view
- **Layer toggle:** Left panel checkbox to show/hide:
  - Prospectivity zones
  - Priority targets
- **Color legend:** Shows zone categories and their meanings

**How to use:**
1. Use search box to find specific targets (e.g., "Keonjhar")
2. Click on red target points to see popup with:
   - Target code & name
   - Prospectivity score (/100)
   - Geology description
   - Exact latitude and longitude (five decimal places)
   - Evidence variations contributing to the ranking, such as spectral response, structure, terrain, lithology, and occurrence proximity
3. Toggle layers on/off to focus analysis
4. Zoom to examine specific regions in detail

---

### 3. **Priority Targets (Data Table)**
Comprehensive table of all 10 exploration targets with:

**Columns:**
- **Target:** Code & Name (e.g., MN-001 Keonjhar North)
- **Exact location:** Latitude and longitude in decimal degrees (for example, `21.68000° N, 85.58000° E`)
- **Score:** Prospectivity score (0-100)
- **Confidence:** Model confidence % (0-100)
- **Zone:** Priority level (HIGH/MEDIUM/LOW)
- **Geology:** Rock type & formation
- **Evidence variations:** The target-specific evidence factors used to support its ranking
- **Status:** Review state (Pending/Validated/Needs review)

**Filter Options:**
- Buttons: ALL / HIGH / MEDIUM / LOW to filter by zone
- Automatically sorts by highest score first

**Detailed Cards:**
Below table shows top 3 targets with:
- Target code
- Target name
- Exact coordinates (latitude, longitude, five decimal places)
- Evidence variations/factors supporting the target score
- Visual prospectivity bar

**How to use:**
1. Click HIGH/MEDIUM/LOW to filter targets
2. Click column headers to sort by score, confidence, or geology
3. Review scores and confidence values
4. Use coordinates for field planning
5. Check status to identify targets needing validation

---

### 4. **Data & Processing**
Information about workspace datasets:

**Datasets shown:**
- Sentinel-2 multispectral (12 scenes, Ready)
- Geological formations layer (Ready)
- DEM terrain model 30m resolution (Ready)
- Training features for ML (2,840 samples, Ready)

**Action buttons:**
- Upload layer - Add GeoJSON, KML, CSV, or GeoTIFF
- Satellite search - Find Sentinel-2 / Landsat scenes
- Terrain analysis - Calculate elevation, slope, aspect

**Recent processing:**
- Shows completed jobs (Feature extraction)
- Processing status (Completed)

**How to use:**
1. Review available data inputs
2. Upload new data if needed
3. Check processing status for jobs
4. Download results when ready

---

### 5. **Reports**
Generate exploration outputs:

**Available Reports:**
1. **Prospectivity summary**
   - Overview of ranked demo targets
   - Model-estimated exploration zones
   - Click download button to export

2. **Field validation sheet**
   - Coordinates, scores, confidence values
   - Suggested review factors
   - Ready for field team use

**Validation Disclaimer:**
⚠️ "Reports clearly separate model output from geological confirmation. No target should be treated as a proven reserve without field evidence, laboratory assays and appropriate drilling."

**How to use:**
1. Review report descriptions
2. Click download icon to export as PDF/CSV
3. Share with field teams for validation
4. Use validation sheet for ground-truthing

---

### 6. **Settings**
Workspace configuration:

**Settings include:**
- **Prospectivity thresholds:** High 70–100 · Medium 40–69 · Low 0–39
- **Notifications:** Processing completion and field-review reminders
- **Security:** Demo authentication mode (local evaluation)

**How to use:**
1. Adjust thresholds to match your criteria
2. Enable/disable notification types
3. Review authentication settings

---

## Typical Workflow

### Step 1: Quick Assessment (Dashboard)
- View overview of all targets
- Check high prospectivity count
- Review distribution chart

### Step 2: Spatial Exploration (GIS Explorer)
- Navigate map to regions of interest
- Search specific target locations
- Examine prospectivity zones
- Verify target placement against geology

### Step 3: Detailed Review (Priority Targets)
- Sort by score or confidence
- Filter by prospectivity zone
- Review target codes and geology
- Check validation status

### Step 4: Planning (Data & Reports)
- Generate field validation sheet
- Export coordinates for GPS
- Download prospectivity summary
- Share with field teams

### Step 5: Validation & Follow-up
- Conduct field verification
- Collect samples and assays
- Update target status (Pending → Validated)
- Document findings

---

## Demo Data

**10 Exploration Targets included:**
- 4 HIGH prospectivity (scores 74-92)
- 3 MEDIUM prospectivity (scores 55-68)
- 3 LOW prospectivity (scores 27-38)

**Coverage Area:**
- Central & Eastern India
- Focus: Known manganese provinces (Keonjhar, Sundargarh, Balaghat, etc.)

**Model Outputs:**
- Scores based on satellite, geological, and terrain evidence
- Confidence values indicate model certainty
- Zone classification for prioritization

---

## Important Notes

⚠️ **This is a DEMO/PROTOTYPE:**
- Uses demo data for evaluation
- Scores are model estimates, NOT proven reserves
- Field validation is REQUIRED
- No external API keys needed
- Local authentication (any email/password works)

🔧 **For Production Use:**
- Connect real satellite data sources
- Integrate actual geological databases
- Deploy trained ML models
- Setup database backend
- Implement user authentication
- Add report export services

---

## Support

**Backend API Documentation:**
Visit: http://127.0.0.1:8000/docs (Interactive Swagger UI)

**API Endpoints:**
- `/api/health` - Server status
- `/api/manganese/targets` - List manganese exploration targets
- `/api/manganese/targets/{id}` - Get a manganese target detail
- `/api/manganese/prospectivity` - Manganese GeoJSON prospectivity zones
- `/api/manganese/predict` - Validate one manganese screening request
- `/api/manganese/predict-batch` - Validate a bounded batch of screening requests
- `/api/manganese/upload-data` - Validate manganese-labelled CSV text
- `/api/manganese/model/status` - Model version, dataset and metric status

The `/api/targets` and `/api/maps/prospectivity` routes remain available for compatibility. No validated manganese-labelled dataset or trained estimator is bundled with this demo, so current outputs are screening simulations and must be field-validated.

**Common Issues:**
- Map not loading? Check internet connection (needs OpenStreetMap tiles)
- Targets showing 0? Refresh page or check backend API status
- Layout issues on mobile? Use desktop browser for full features
