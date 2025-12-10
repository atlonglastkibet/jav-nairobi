# Quick Start Guide

## Running the App

### Option 1: Using the launch script (Recommended)

```bash
cd /home/dataopske/Desktop/jav/streamlit_app
./run_app.sh
```

### Option 2: Manual launch

```bash
cd /home/dataopske/Desktop/jav/streamlit_app
source ../.venv/bin/activate
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## Navigation

The app has 3 main pages accessible from the sidebar:

### 🏠 Home
- Overview of Nairobi's transit network
- Interactive Pydeck map with route arcs
- Key metrics dashboard
- Routes color-coded by equity tier

### ℹ️ About
- Project background and methodology
- GNN vs Traditional ML comparison
- Model performance metrics
- Technology stack details

### 🗺️ Route Explorer
- Interactive route variant comparison
- Select from 27 routes with recommendations
- View original route vs GNN-recommended variants
- Detailed metrics for each variant

## Key Features

### Home Page
- **136 routes** visualized as arcs from CBD
- **Color coding**: Red (underserved) → Yellow → Green (well-served)
- **Metrics panel**: Routes, stops, population impact, ward coverage

### Route Explorer
- **27 routes** with GNN recommendations (39 total variants)
- **Variant types**: A (recommended), B, C (alternatives)
- **Metrics**: GNN score, population served, equity multiplier
- **Interactive map**: Toggle variants on/off

## Troubleshooting

### App won't start
```bash
# Reinstall dependencies
cd /home/dataopske/Desktop/jav/streamlit_app
source ../.venv/bin/activate
pip install -r requirements.txt
```

### Data not loading
Check that these files exist:
- `../data/raw/digitalmatatu/GTFS_FEED_2019.zip`
- `../data/training_output/route_recommendations_comprehensive.csv`
- `../data/training_output/top_candidates.csv`
- `../data/training_output/ward_summary.csv`

### Port already in use
```bash
streamlit run app.py --server.port 8502
```

## Next Steps

### For Development
1. Edit page files in `pages/` directory
2. Modify styling in `utils/styling.py`
3. Update data processing in `utils/data_loader.py`

### For Deployment
See `README.md` for deployment instructions to Streamlit Cloud or other platforms.

## Data Summary

Based on current data:
- **136 routes** in GTFS feed
- **4,284 stops** total
- **27 routes** with GNN recommendations
- **39 variants** (A, B, C for different routes)
- **88 wards** covered

## Performance Notes

- First load may take ~10-15 seconds (loading GTFS data)
- Subsequent page navigation is cached and faster
- Map rendering is hardware-dependent (GPU acceleration helps)

## Contact

For issues or questions:
- Check the main `README.md`
- Review code comments in source files
- Data processing pipeline is in parent `/notebooks` directory
