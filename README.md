# fleetline-interactive-demo
- **Backend:** FastAPI + OR-Tools routing optimizer
- **Frontend:** Leaflet.js interactive map
- **Features:**
  - Click-to-add deliveries
  - Dynamic route recalculation
  - Color-coded routes per truck
  - ETA for each delivery
  - Human-readable JSON output

## Run Locally

1. Backend:
   ```bash
   cd backend
   pip install -r requirements.txt
   uvicorn server:app --reload
   Frontend:

cd frontend
start index.html


Click anywhere on the map to add a new delivery and watch routes recalc dynamically.
