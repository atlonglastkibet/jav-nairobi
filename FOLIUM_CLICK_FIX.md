# Folium Click Handler Fix

## Issue
Clicking route variant lines in the Route Explorer (Folium page) was not updating the stats panel.

## Root Cause
The original implementation used popup buttons with `onclick='updateStats()'`, but Folium popups are rendered in iframes which cannot access parent window JavaScript functions.

## Solution
Implemented direct click event handlers on polylines using Leaflet's event system:

### Changes Made

**File:** `/home/dataopske/Desktop/jav/utils/viz_utils.py`

1. **Removed popup buttons** from polylines
   - Changed from: `popup=f"<button onclick='updateStats({i})'>..."`
   - Changed to: `tooltip="Click to view detailed stats"`

2. **Added JavaScript click handlers** after LayerControl
   ```javascript
   // Find all polylines on the map
   // Identify variants by color
   // Attach click event listeners
   // Call updateStats(variantIndex) directly
   ```

3. **Color-based variant identification**
   - Green (`#34A853`) = Variant A (index 0)
   - Yellow (`#FBBC04`) = Variant B (index 1)
   - Red (`#EA4335`) = Variant C (index 2)

### How It Works

1. **Polyline Creation**
   - Each variant route is drawn with a specific color
   - Tooltip shows variant info on hover

2. **Click Handler Setup** (runs after map loads)
   - JavaScript finds all polylines using `map.eachLayer()`
   - Checks each polyline's color
   - Matches color to variant index
   - Attaches click event: `polyline.on('click', () => updateStats(variantIndex))`

3. **Stats Update**
   - User clicks colored route line
   - Click event triggers `updateStats(variantIndex)`
   - JavaScript updates all stat values in the floating panel
   - Cursor changes to pointer on hover

### Key Code

```javascript
// Color matching
if (color === '#34A853') {
    variantIndex = 0;  // Variant A
} else if (color === '#FBBC04') {
    variantIndex = 1;  // Variant B
} else if (color === '#EA4335') {
    variantIndex = 2;  // Variant C
}

// Click handler
polyline.on('click', function(e) {
    L.DomEvent.stopPropagation(e);
    updateStats(variantIndex);
});

// Cursor style
polyline.on('mouseover', function() {
    this._path.style.cursor = 'pointer';
});
```

## Benefits

1. **Works reliably** - No iframe restrictions
2. **Clean UX** - Click anywhere on the route line
3. **Visual feedback** - Cursor changes to pointer on hover
4. **Instant updates** - Stats panel updates immediately

## Testing

To verify the fix:
1. Navigate to **Route Explorer** page
2. Select any route
3. Hover over colored route lines - cursor should change to pointer
4. Click green line (Variant A) - stats should update
5. Toggle on yellow/red alternatives
6. Click them - stats should update to their values

## Result

✅ Click handlers now work properly in Streamlit's Folium integration
✅ Stats panel updates when clicking variant route lines
✅ Matches notebook behavior exactly

**Status:** 🟢 FIXED
