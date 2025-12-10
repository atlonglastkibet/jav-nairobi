# Route Explorer Issues and Fixes

## Problems Identified

### 1. **CRITICAL: Fake Population Data**
**Location:** `streamlit_app/utils/data_loader.py` line 747

**Problem:**
```python
df_stops['pop_within_500m'] = 1000  # Default population
```

The Streamlit app was assigning a fake population of 1000 to EVERY stop, instead of using the real population data from `stop_features_complete.csv`.

**Impact:**
- Wrong existing population (showed 44,000 instead of 567,543)
- Wrong calculations for all metrics
- Completely inaccurate coverage statistics

**Fix Applied:**
Now loads the actual `data/processed/stop_features_complete.csv` which contains real population data:
- Each stop has accurate `pop_within_500m` values
- Range: ~1,000 to 50,000+ people per stop
- Example: Stop 0001RLW has 27,759 people within 500m

---

### 2. **Population Calculation Logic**
**Location:** `utils/viz_utils.py` lines 179-206

**Original Problem:**
Tried to use non-existent `baseline_pop_served` column from variants_df.

**Correct Understanding:**
- `total_pop_served` in variants_df = **ADDITIONAL** population from new stops
- Need to calculate existing population by summing `pop_within_500m` for all existing stops
- Total = existing + additional

**Fix Applied:**
```python
# Calculate original population served by existing stops
orig_pop = 0
for stop_id in original_stops['stop_id']:
    stop_data = df[df['stop_id'] == stop_id]
    if len(stop_data) > 0:
        orig_pop += stop_data.iloc[0]['pop_within_500m']

# For each variant
new_pop = row['total_pop_served']  # Additional population
total_pop = orig_pop + new_pop
increase = (new_pop/orig_pop*100) if orig_pop > 0 else 0
```

---

### 3. **Missing New Stop Markers**
**Location:** `utils/viz_utils.py` lines 315-326

**Problem:**
New stops were using `folium.Marker` which may not display properly in some contexts.

**Fix Applied:**
Changed to `folium.CircleMarker` with:
- Radius: 8px
- Color: Matches route color (green for recommended, yellow/red for alternatives)
- fillColor and fillOpacity for solid appearance
- Enhanced popups with variant info

---

## Expected Results (Route 70601000211, Variant B)

### Notebook Output:
```
EXISTING: 44 stops
ADDING: 2 stops
Existing Population: 567,543
Adding: +29,278
Total: 596,821
+5% Coverage
```

### Streamlit Should Now Show:
```
EXISTING: 44 stops
ADDING: 2 stops (or 3 depending on variant)
Existing Population: 567,543
Adding: +29,278 (or similar)
Total: 596,821
+5% Coverage (or similar)
```

---

## Data Flow

### Notebook:
1. Loads `stop_features_complete.csv` directly as `df`
2. Has real population data for all stops
3. Calculates existing population by summing `pop_within_500m`
4. Uses `total_pop_served` from variants as additional population

### Streamlit (BEFORE fix):
1. Used GTFS stops only
2. Assigned fake 1000 population to all stops ❌
3. Wrong calculations everywhere

### Streamlit (AFTER fix):
1. Loads `stop_features_complete.csv` as `df` ✅
2. Has real population data ✅
3. Same calculation logic as notebook ✅
4. Accurate results ✅

---

## Files Modified

1. **streamlit_app/utils/data_loader.py** (lines 745-756)
   - Now loads real stop features data
   - Falls back to GTFS only if file missing

2. **utils/viz_utils.py** (lines 179-206)
   - Fixed population calculation logic
   - Correctly sums existing stop populations
   - Properly interprets `total_pop_served` as additional population

3. **utils/viz_utils.py** (lines 315-326, 364-374)
   - Changed markers to CircleMarker for visibility
   - Added proper colors matching route lines
   - Enhanced popups

---

## Testing Checklist

- [ ] Route Explorer loads without errors
- [ ] Population numbers match notebook (existing ~567k)
- [ ] New stops are visible as colored circles
- [ ] Clicking routes updates stats panel
- [ ] All variants show correct population calculations
- [ ] Percentage increases are accurate (~5%)

---

## Root Cause

The Streamlit implementation was created without access to the enriched stops data that the notebooks use. It fell back to basic GTFS stops with placeholder population values, causing all downstream calculations to be wrong.

The fix ensures both implementations use the same data source: `stop_features_complete.csv` with real population numbers from spatial analysis.
