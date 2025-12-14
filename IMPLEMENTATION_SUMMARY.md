# Main Page Implementation - Changes Required

## Current Progress
✅ Added "THE PROJECT" section before equity gap
✅ Removed emojis from narratives

## Remaining Tasks

### 1. Ward Equity Dashboard
- [ ] Replace PyDeck with Folium choropleth (dark mode)
- [ ] Use CartoDB dark-matter-gl-style
- [ ] Keep before/after toggle functionality
- [ ] Match notebook implementation from `notebooks/03_equity_analysis(spatial).ipynb`

### 2. Stop Intelligence Section
- [ ] Change existing stops from gray to BLUE dots
  - Current: `[150, 150, 150]` → Change to: `COLORS['existing_route']` which is `[26, 115, 232]` (blue)
- [ ] Add ward boundaries overlay to PyDeck map
  - Use GeoJsonLayer with ward geometries
  - Low opacity fill, white stroke
- [ ] Fix GNN score display in tooltips
  - Currently showing `{gnn_score}` in braces
  - Should show actual numeric value: `{gnn_score:.2f}`
- [ ] Fix population display in tooltips
  - Currently showing `{pop_within_500m}` in braces
  - Should show formatted number: `{pop_within_500m:,}`

### 3. Community Stories
- [ ] Update link to point to Community Stories page (when created)
- [ ] Currently links to `pages/1_Optimised_Routes.py`
- [ ] Should eventually link to `pages/2_Community_Impact.py`

### 4. Methodology Sections
- [ ] Convert expander sections to prose format (like IMPACT section)
- [ ] Remove "DATA SOURCES" and "PREPROCESSING" expanders
- [ ] Create full narrative sections instead
- [ ] Match style of existing "THE PROJECT", "IMPACT", "THE FUTURE" sections

## Data Loading Notes
- Ward geometries: `data/processed/wards_full_gdf.csv`
- Contains WKT geometry strings that need parsing with shapely.wkt.loads()
- Has columns: ward, subcounty, population, pct_access, pop_served, poverty_rate

## Folium Implementation Reference
From notebook cell d6cb2f11:
```python
# Format and create Folium choropleth
m = wards_map_display.explore(
    column='pct_access',
    cmap='YlOrRd',
    legend=True,
    tiles='CartoDB positron',  # Change to 'CartoDB dark_matter'
    style_kwds={'color': 'black', 'weight': 0.5}
)
```

## Next Steps
1. Test current changes
2. Implement Folium ward map
3. Fix stop colors and tooltips
4. Add ward boundaries to stop map
5. Convert methodology to prose
