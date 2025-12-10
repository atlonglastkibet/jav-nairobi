# New Stop Markers - Route Explorer

## Design Implementation

### Recommended Variant (Green) Stops
**Visual Design:**
- **Outer Circle**: Radius 12px, green fill with 4px white border
- **Inner Dot**: Radius 5px, white fill for contrast
- **Color**: `#46CC71` (bright green)
- **Opacity**: 100% (fully opaque)

**Result:** Large green circles with white centers that stand out prominently

### Alternative Variant Stops
**Variant B (Yellow):**
- **Outer Circle**: Radius 11px, yellow fill with 3px white border
- **Inner Dot**: Radius 4px, white fill
- **Color**: `#F1C40F` (bright yellow)

**Variant C (Red):**
- **Outer Circle**: Radius 11px, red fill with 3px white border
- **Inner Dot**: Radius 4px, white fill
- **Color**: `#E74C3C` (bright red)

## Visibility Features

1. **Two-Layer Design**
   - Outer colored circle with white border makes stops pop against the dark map
   - Inner white dot creates a target/bullseye effect
   - High contrast ensures visibility at all zoom levels

2. **Size Differentiation**
   - Recommended stops: Larger (radius 12px)
   - Alternative stops: Slightly smaller (radius 11px)
   - Existing stops: Smallest (radius 6px)

3. **Tooltips**
   - Hover shows: "NEW STOP" + stop_id
   - Quick identification without clicking

4. **Detailed Popups**
   - Click shows:
     - Stop type (🟢 Recommended or 🔶 Alternative)
     - Stop ID
     - GNN Quality Score
     - Population within 500m

## Layer Organization

```
Route Explorer Map
├── Existing Route (Blue line + stops)
├── Recommended Extension (Green, show=True)
│   ├── Route line (solid green, 6px)
│   └── New Stops (green circles with white center)
├── Alternative 1 (Yellow, show=False)
│   ├── Route line (dashed yellow, 5px)
│   └── New Stops (yellow circles with white center)
└── Alternative 2 (Red, show=False)
    ├── Route line (dashed red, 5px)
    └── New Stops (red circles with white center)
```

## Visual Hierarchy

**From Most to Least Prominent:**
1. 🟢 **Recommended new stops** - Largest, bright green with white center
2. 🔶 **Alternative new stops** - Medium, yellow/red with white center
3. **Route lines** - Solid or dashed, colored by variant
4. 🔵 **Existing stops** - Smallest, blue with white fill

## Example Visual

```
Map View:
┌─────────────────────────────────────┐
│  Existing Route ●─────●─────●       │
│                             │       │
│                             ●       │
│                        ┌───▶◉ NEW  │ <- Large green circle
│  Recommended           │    ◉ NEW  │    with white center
│  Extension ────────────┘    ◉ NEW  │    (Variant A)
│                                     │
│                        ┌───▶○ NEW  │ <- Medium yellow circle
│  Alternative 1         │    ○ NEW  │    (Variant B, hidden by default)
│  (Hidden) ─ ─ ─ ─ ─ ─ ─┘            │
└─────────────────────────────────────┘

Legend:
● = Existing stop (small blue)
◉ = Recommended new stop (large green with white center)
○ = Alternative new stop (medium yellow/red with white center)
```

## Code Location

**File:** `/home/dataopske/Desktop/jav/utils/viz_utils.py`

**Recommended stops:** Lines 318-343
```python
# Outer circle (12px radius, green with white border)
folium.CircleMarker(radius=12, color='#ffffff', fillColor=COLORS['recommended'], weight=4)

# Inner dot (5px radius, white)
folium.CircleMarker(radius=5, fillColor='#ffffff')
```

**Alternative stops:** Lines 381-405
```python
# Outer circle (11px radius, colored with white border)
folium.CircleMarker(radius=11, color='#ffffff', fillColor=color_alt, weight=3)

# Inner dot (4px radius, white)
folium.CircleMarker(radius=4, fillColor='#ffffff')
```

## Testing Checklist

- [ ] Load Route Explorer with route 70601000211
- [ ] See large green circles with white centers (recommended new stops)
- [ ] Toggle "Alternative 1" layer - see yellow circles appear
- [ ] Toggle "Alternative 2" layer - see red circles appear
- [ ] Hover over new stops - tooltip shows "NEW STOP" + ID
- [ ] Click new stops - popup shows detailed info
- [ ] Zoom in/out - stops remain clearly visible at all levels

## Comparison with Notebook

The notebook implementation uses similar CircleMarkers but may have different styling. The Streamlit implementation now uses:
- **Larger circles** for better visibility
- **White borders** for contrast against dark map
- **Two-layer design** (outer + inner) for distinctive appearance
- **Higher z-index** to ensure stops appear above other map elements

This creates a more prominent, professional appearance suitable for web deployment.
