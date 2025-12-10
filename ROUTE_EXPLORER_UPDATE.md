# Route Explorer Update: PyDeck → Folium

## Summary

The Route Explorer has been completely rebuilt using **Folium** instead of PyDeck for significantly improved interactivity and user experience.

## What Changed

### Before (PyDeck)
- Static visualization with checkboxes
- Metrics displayed in sidebar below map
- Required scrolling to compare variants
- Straight-line routes between stops
- Limited interactivity

### After (Folium)
- **Click-to-view metrics**: Click any route variant to instantly see detailed stats
- **Floating stats panel**: Metrics update on the map without scrolling
- **Road-snapped routes**: Uses OSMnx to follow actual road networks
- **Layer control**: Toggle variants on/off with built-in Leaflet controls
- **Dark mode theme**: Professional styling matching your design system
- **Better performance**: Lightweight for route-level visualization

## Key Features

### 1. Interactive Stats Panel
- Click any route line to view its metrics
- Panel updates in real-time with JavaScript
- No page reload or scrolling needed
- Shows: Score, Equity, Coverage, Temporal metrics, Population impact

### 2. Road-Accurate Rendering
- Routes follow actual roads using OSMnx graph
- More realistic visualization of extensions
- Helps understand route feasibility

### 3. Layer Control
- Toggle existing route, recommended extension, and alternatives
- Built-in Leaflet control in top-right corner
- Show/hide layers independently

### 4. Professional UI
- Dark mode throughout
- Color-coded variants (Blue=Existing, Green=Recommended, Yellow/Red=Alternatives)
- Floating legend
- Route header panel
- Tooltip on hover

## Files Modified

### 1. `/streamlit_app/pages/1_Route_Explorer.py`
**Complete rewrite** - Now uses Folium instead of PyDeck
- Imports `plot_route_variants_folium` from `utils.viz_utils`
- Loads OSMnx graph for road snapping
- Renders map with `st_folium()`
- Simplified layout (no sidebar)

### 2. `/streamlit_app/utils/data_loader.py`
**Added function**: `prepare_folium_route_data(route_id)`
- Prepares all data needed for Folium visualization
- Converts GTFS data to format expected by `viz_utils.py`
- Handles column naming and data type conversions

### 3. `/streamlit_app/requirements.txt`
**Added dependencies**:
- `streamlit-folium>=0.15.0` - Streamlit integration for Folium
- `osmnx>=1.3.0` - Road network data (was missing)

### 4. `/streamlit_app/README.md`
**Updated documentation**:
- Added virtual environment installation instructions
- Documented new Folium features
- Added note about Arch/Manjaro system Python (PEP 668)
- Updated technology stack

## How It Works

### Data Flow
```
Route Selection
    ↓
prepare_folium_route_data()
    ↓
Loads: GTFS feed, variants, candidates, road network (G)
    ↓
plot_route_variants_folium()
    ↓
Generates interactive Folium map with:
  - Original route (blue)
  - Recommended extension (green)
  - Alternative variants (yellow/red)
  - Floating stats panels
  - Click handlers
    ↓
st_folium() renders in Streamlit
```

### Visualization Logic (from `utils/viz_utils.py`)
1. **Road Snapping**: `route_stops_to_coords()` uses OSMnx to find shortest path between stops on road network
2. **Extension Paths**: `extension_coords()` extends routes by road-snapping new stops
3. **Interactive Elements**: JavaScript handlers update stats panel on click
4. **Layer Management**: Folium FeatureGroups create toggleable layers

## Installation

### For New Users
```bash
cd streamlit_app
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
streamlit run app.py
```

### For Existing Users
```bash
cd streamlit_app
pip install streamlit-folium osmnx
# or if using venv:
source venv/bin/activate
pip install streamlit-folium osmnx
```

## Benefits Over PyDeck

| Aspect | PyDeck | Folium |
|--------|--------|--------|
| **Click Interaction** | Limited | Native click handlers |
| **Metrics Display** | Sidebar (requires scroll) | Floating panel on map |
| **Route Rendering** | Straight lines | Road-snapped paths |
| **Layer Toggle** | Checkboxes | Built-in control |
| **Performance** | GPU-accelerated (overkill) | Lightweight |
| **Code Reuse** | New implementation | Uses existing `viz_utils.py` |
| **Dark Mode** | Custom styling needed | Built-in |

## Testing Checklist

- [ ] Route selection dropdown works
- [ ] Map loads with road network
- [ ] Existing route displays (blue)
- [ ] Recommended extension displays (green)
- [ ] Alternative variants toggle on/off
- [ ] Clicking route lines updates stats panel
- [ ] Stats panel shows correct metrics
- [ ] Layer control works
- [ ] Dark mode displays correctly
- [ ] OSMnx graph caches (second load faster)

## Known Limitations

1. **First Load**: OSMnx downloads Nairobi road network on first run (cached afterward)
2. **Memory**: Road network graph requires ~100MB RAM when cached
3. **Browser Compatibility**: Requires modern browser with JavaScript enabled

## Future Enhancements

Potential improvements:
- [ ] Add comparison mode (side-by-side variants)
- [ ] Export map as standalone HTML
- [ ] Show congestion overlay from traffic data
- [ ] Add animation for route extensions
- [ ] Mobile-responsive layout

## Troubleshooting

### "Road network unavailable"
- OSMnx couldn't download graph
- Check internet connection
- Verify Nairobi bounding box coordinates

### "Module 'streamlit_folium' not found"
- Run: `pip install streamlit-folium`
- If on Arch/Manjaro: Use virtual environment

### Map not displaying
- Check browser console for errors
- Verify data files exist
- Ensure route has variants in CSV

## Conclusion

The Folium implementation delivers a **superior user experience** with:
- ✅ Better interactivity (click-to-view)
- ✅ No scrolling needed (floating stats)
- ✅ More realistic visualization (road-snapped)
- ✅ Professional aesthetics (dark mode)
- ✅ Code reuse (existing `viz_utils.py`)

This matches your notebook implementation and provides the same great UX you were already using for analysis.
