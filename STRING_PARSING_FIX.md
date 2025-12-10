# String Parsing Fix - New Stops Not Appearing

## Root Cause #2: String Not Parsed to List

After fixing the candidates file issue, new stops still weren't appearing because **the `new_stops` column was never being parsed from a string to a list**.

## The Problem

The CSV file stores `new_stops` as a string:
```csv
"['CANDIDATE_Gatina Ward_3', 'CANDIDATE_Waithaka Ward_0', 'CANDIDATE_Waithaka Ward_1']"
```

But the code was treating it as if it were already a list:
```python
# WRONG - treats string as iterable of characters
new_top_ids = top_variant['new_stops']
new_top_df = selected_candidates[selected_candidates['stop_id'].isin(new_top_ids)]
```

This caused:
- `isin()` to check if stop_id is in the **string characters**, not the stop IDs
- Empty DataFrames (`new_top_df` had 0 rows)
- No markers added to the map

## The Fix

**Added `ast.literal_eval()` to parse strings to lists:**

### Location 1: Lines 117-141 (Parsing new stops for variants)
```python
import ast

# Parse new_stops from string to list
new_top_ids = ast.literal_eval(top_variant['new_stops']) if isinstance(top_variant['new_stops'], str) else top_variant['new_stops']
new_top_df = selected_candidates[selected_candidates['stop_id'].isin(new_top_ids)]
```

### Location 2: Lines 207-208 (Parsing for stats count)
```python
# Parse new_stops to get actual count
new_stops_parsed = ast.literal_eval(row['new_stops']) if isinstance(row['new_stops'], str) else row['new_stops']

variants_stats.append({
    ...
    'new_stops': int(len(new_stops_parsed)),  # Now gets correct count
    ...
})
```

## Debug Output Added

Added print statements to verify data is loading correctly:
```python
print(f"DEBUG: Route {route_id}, Variant {top_variant['variant_id']}")
print(f"DEBUG: new_top_ids = {new_top_ids}")
print(f"DEBUG: new_top_df has {len(new_top_df)} stops")
if len(new_top_df) > 0:
    print(f"DEBUG: First stop: {new_top_df.iloc[0]['stop_id']} at ({new_top_df.iloc[0]['lat']}, {new_top_df.iloc[0]['lon']})")
```

Expected output for route 70601000211:
```
DEBUG: Route 70601000211, Variant 70601000211_C
DEBUG: new_top_ids = ['CANDIDATE_Gatina Ward_3', 'CANDIDATE_Waithaka Ward_0', 'CANDIDATE_Waithaka Ward_1']
DEBUG: new_top_df has 3 stops
DEBUG: First stop: CANDIDATE_Gatina Ward_3 at (-1.292895, 36.758416)
DEBUG: Variant 70601000211_C has 3 new stops
```

## Impact

### Before Fix:
```python
new_top_ids = "['CANDIDATE_Gatina Ward_3', ...]"  # String
# isin() checks if 'CANDIDATE_Gatina Ward_3' is in "[', 'C', 'A', 'N', ..."
# Result: new_top_df = empty DataFrame
# Markers: 0 added
```

### After Fix:
```python
new_top_ids = ['CANDIDATE_Gatina Ward_3', ...]  # List
# isin() checks if 'CANDIDATE_Gatina Ward_3' is in the list
# Result: new_top_df = 3 rows with stop data
# Markers: 3 large green circles with white centers
```

## Complete Fix Summary

Three issues needed to be fixed:

1. **Wrong candidates file** → Changed to `all_candidates_equity.csv` ✅
2. **String not parsed** → Added `ast.literal_eval()` ✅
3. **Markers not prominent** → Enhanced with two-layer design ✅

## Files Modified

**File:** `utils/viz_utils.py`

**Lines 117-141:** Parse `new_stops` when loading variant data
```python
new_top_ids = ast.literal_eval(top_variant['new_stops']) if isinstance(top_variant['new_stops'], str) else top_variant['new_stops']
```

**Lines 137-141:** Parse `new_stops` in loop for all variants
```python
new_stops_list = ast.literal_eval(row['new_stops']) if isinstance(row['new_stops'], str) else row['new_stops']
df_new = selected_candidates[selected_candidates['stop_id'].isin(new_stops_list)]
```

**Lines 207-213:** Parse `new_stops` for correct count in stats
```python
new_stops_parsed = ast.literal_eval(row['new_stops']) if isinstance(row['new_stops'], str) else row['new_stops']
'new_stops': int(len(new_stops_parsed))
```

## Testing

Check Streamlit console for debug output:
1. Should see "DEBUG: new_top_df has 3 stops" (not 0)
2. Should see coordinates printed
3. Map should show 3 large green circles
4. Metrics panel should say "ADDING 3 stops"
5. Clicking stops should show popup with stop details

## Why This Happened

The notebook code likely parses the CSV differently or uses a method that automatically converts strings to lists. The Streamlit implementation uses raw pandas `read_csv()` which keeps the column as strings.

The fix ensures both implementations handle the data identically.
