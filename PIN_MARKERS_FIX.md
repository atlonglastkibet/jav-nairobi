# Pin Markers Fix - Final Solution

## The Real Problem

After fixing the data loading and string parsing issues, markers still weren't visible because we were using `folium.CircleMarker()` (simple circles) instead of `folium.Marker()` with icons (actual pin/marker graphics).

## User Expectation vs Reality

**User Expected:** 📍 Actual pin markers like the green pin with + symbol in the image
**What We Had:** ⭕ Small circles that were hard to see

## Solution: Use Folium.Marker with Icons

Changed from `CircleMarker` to `Marker` with Font Awesome icons:

### Recommended Variant (Green Pins)
```python
folium.Marker(
    location=[stop['lat'], stop['lon']],
    popup=f"<b>🟢 NEW STOP (Recommended)</b><br><b>ID:</b> {stop['stop_id']}<br>...",
    tooltip=f"<b>NEW STOP</b><br>{stop['stop_id']}",
    icon=folium.Icon(
        color='green',      # Green pin
        icon='plus',        # Plus symbol (+)
        prefix='fa'         # Font Awesome
    )
).add_to(rec_layer)
```

### Alternative Variants (Orange/Red Pins)
```python
# Map hex colors to Folium color names
icon_color_map = {COLORS['alt_1']: 'orange', COLORS['alt_2']: 'red'}
icon_color = icon_color_map.get(color_alt, 'orange')

folium.Marker(
    location=[stop['lat'], stop['lon']],
    popup=f"<b>🔶 NEW STOP (Variant ...)</b><br>...",
    tooltip=f"<b>NEW STOP</b><br>{stop['stop_id']}",
    icon=folium.Icon(
        color=icon_color,   # orange or red
        icon='plus',        # Plus symbol
        prefix='fa'
    )
).add_to(alt_layer)
```

## Visual Result

### Recommended Variant:
- 📍 **Green pin with + symbol**
- Visible on "Recommended Extension" layer (shown by default)
- Tooltip on hover: "NEW STOP" + stop ID
- Popup on click: Full details with GNN score and population

### Alternative Variants:
- 📍 **Orange pin** for Alternative 1 (Variant B)
- 📍 **Red pin** for Alternative 2 (Variant C)
- Hidden by default, toggle layer to view
- Same tooltip and popup behavior

## Complete Fix Chain

All three issues needed to be resolved:

1. ✅ **Data Source** - Changed to `all_candidates_equity.csv` (1,645 stops)
2. ✅ **String Parsing** - Added `ast.literal_eval()` to parse stop lists
3. ✅ **Marker Type** - Changed from `CircleMarker` to `Marker` with icons

## File Changes

**File:** `utils/viz_utils.py`

**Lines 333-347:** Recommended variant pins
- Changed from 2x CircleMarker to 1x Marker with icon
- Green pin with plus icon
- Added debug output

**Lines 385-400:** Alternative variant pins
- Changed from 2x CircleMarker to 1x Marker with icon
- Orange/red pins with plus icons
- Color mapping for alternatives

## Debug Output

Console should now show:
```
DEBUG: Route 70601000211, Variant 70601000211_C
DEBUG: new_top_ids = ['CANDIDATE_Gatina Ward_3', 'CANDIDATE_Waithaka Ward_0', 'CANDIDATE_Waithaka Ward_1']
DEBUG: new_top_df has 3 stops
DEBUG: First stop: CANDIDATE_Gatina Ward_3 at (-1.292895, 36.758416)
DEBUG: Adding 3 marker pins for recommended variant
DEBUG: Adding marker at (-1.292895, 36.758416) for CANDIDATE_Gatina Ward_3
DEBUG: Adding marker at (-1.287139, 36.733004) for CANDIDATE_Waithaka Ward_0
DEBUG: Adding marker at (-1.285502, 36.732045) for CANDIDATE_Waithaka Ward_1
DEBUG: Variant 70601000211_C has 3 new stops
```

## Map Legend

After fix, the map should show:

```
Route Explorer
├── Existing Route
│   └── Blue circles (existing stops)
├── Recommended Extension ✓ (shown)
│   ├── Green solid line
│   └── 📍 Green pins with + (NEW STOPS)
├── Alternative 1 (hidden)
│   ├── Yellow dashed line
│   └── 📍 Orange pins with +
└── Alternative 2 (hidden)
    ├── Red dashed line
    └── 📍 Red pins with +
```

## Why This Works

`folium.Marker()` creates actual pin/marker icons that:
- Look like traditional map pins 📍
- Stand out prominently on the map
- Have recognizable shapes and colors
- Support Font Awesome icons (like the + symbol)
- Match user expectations from other mapping tools

`folium.CircleMarker()` creates SVG circles that:
- Are just colored dots ⭕
- Easy to miss, especially on dark backgrounds
- Don't look like "stops" or "locations"
- Not intuitive for users

## Testing

Verify the pins appear:
1. Open Route Explorer
2. Select route 70601000211
3. Should immediately see 3 **green pins with + symbols**
4. Toggle "Alternative 1" - see **orange pins**
5. Toggle "Alternative 2" - see **red pins**
6. Hover over pins - tooltip appears
7. Click pins - popup with full details

## Success Criteria

- ✅ Pins look like actual map markers (not circles)
- ✅ Green pins visible by default
- ✅ Orange/red pins visible when toggling layers
- ✅ Tooltips work on hover
- ✅ Popups show full stop details
- ✅ Metrics panel matches pin count (e.g., "ADDING 3 stops" = 3 pins)
