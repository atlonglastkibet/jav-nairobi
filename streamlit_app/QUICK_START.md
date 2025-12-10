# Route Explorer - Quick Start Guide

## What's New?

The Route Explorer now uses **Folium** for interactive visualization - the same great experience you have in your Jupyter notebooks!

## Installation (First Time)

```bash
# 1. Navigate to streamlit app
cd /home/dataopske/Desktop/jav/streamlit_app

# 2. Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run app.py
```

## If Already Installed

Just add the new dependencies:

```bash
cd /home/dataopske/Desktop/jav/streamlit_app
source venv/bin/activate  # if using venv
pip install streamlit-folium osmnx
```

## How to Use

1. **Select a Route**: Choose from dropdown at top
2. **View the Map**: Interactive map loads with:
   - 🔵 Blue = Existing route
   - 🟢 Green = Recommended extension (best GNN score)
   - 🟡 Yellow = Alternative 1
   - 🔴 Red = Alternative 2

3. **Click to Compare**: Click any colored route line to see its metrics in the floating stats panel

4. **Toggle Layers**: Use the layer control (top-right) to show/hide variants

## Features You'll Love

### 1. Click-to-View Metrics ✨
No more scrolling! Click a route variant and the stats panel updates instantly:
- Final Score
- Equity Multiplier
- Coverage Score
- Temporal Equity Score
- Population Impact

### 2. Road-Snapped Routes 🛣️
Routes follow actual roads using OSMnx - much more realistic than straight lines!

### 3. Dark Mode 🌙
Professional dark theme throughout the map.

### 4. Layer Control 🗺️
Toggle variants on/off to compare different options side-by-side.

## What It Looks Like

```
┌─────────────────────────────────────────────────────────────┐
│  ROUTE 70600010211 • 23  │                                  │
│  CBD - Thika Road         │                                  │
│  ─────────────────────── │        MAP AREA                  │
│  Current Extension        │                                  │
│  Variant A (Recommended)  │   (Click routes to view stats)  │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐ │                                  │
│  │ Existing    Adding  │ │                                  │
│  │   12        +3      │ │        [Layer Control]          │
│  │  stops     stops    │ │        ☑ Existing Route         │
│  └─────────────────────┘ │        ☑ Recommended Ext        │
│  ┌─────────────────────┐ │        ☐ Alternative 1          │
│  │ Score: 0.847        │ │        ☐ Alternative 2          │
│  │ Equity: 1.42x       │ │                                  │
│  │ Coverage: 0.923     │ │                                  │
│  │ Temporal: 0.856     │ │                                  │
│  └─────────────────────┘ │                                  │
│  ┌─────────────────────┐ │                                  │
│  │ Population Coverage │ │                                  │
│  │ Existing: 12,450    │ │                                  │
│  │ Adding: +8,920      │ │                                  │
│  │ Total: 21,370       │ │                                  │
│  └─────────────────────┘ │                                  │
│  ┌─────────────────────┐ │                                  │
│  │  +71% Coverage      │ │                                  │
│  └─────────────────────┘ │                                  │
└─────────────────────────────────────────────────────────────┘
```

## Troubleshooting

### Map Takes Long to Load First Time
- OSMnx is downloading the Nairobi road network
- This is cached for next time (~2 minutes first load, instant afterward)

### Can't Install Dependencies
If you see "externally-managed-environment" error:
```bash
# Use a virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Map Doesn't Display
1. Check browser console (F12) for errors
2. Verify these files exist:
   - `data/raw/digitalmatatu/GTFS_FEED_2019.zip`
   - `data/training_output/route_recommendations_comprehensive.csv`
   - `data/training_output/top_candidates.csv`

## Why Folium?

You asked whether to stick with PyDeck or switch to Folium. We chose **Folium** because:

1. ✅ **Better Interactivity** - Click handlers and floating popups work natively
2. ✅ **No Scrolling** - Stats update on the map, not below it
3. ✅ **Road Accuracy** - OSMnx integration for realistic paths
4. ✅ **Proven** - Same implementation you're using in notebook [11_route_extensions.ipynb](../notebooks/11_route_extensions.ipynb)
5. ✅ **Performance** - Lightweight for route-level viz

## Next Steps

1. Run the app: `streamlit run app.py`
2. Navigate to "Route Explorer" page
3. Select a route and explore!
4. Click different colored routes to compare metrics

Enjoy exploring your GNN recommendations! 🚍✨
