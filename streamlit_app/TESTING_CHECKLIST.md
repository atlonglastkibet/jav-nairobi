# Testing Checklist for Jav-Nairobi Streamlit App

Use this checklist to verify the app works correctly before showcase.

## ✅ Pre-Launch Checks

### Data Files
- [ ] GTFS feed exists at: `../data/raw/digitalmatatu/GTFS_FEED_2019.zip`
- [ ] Route recommendations exist at: `../data/training_output/route_recommendations_comprehensive.csv`
- [ ] Top candidates exist at: `../data/training_output/top_candidates.csv`
- [ ] Ward summary exists at: `../data/training_output/ward_summary.csv`

### Dependencies
- [ ] Virtual environment activated
- [ ] Streamlit installed (`pip list | grep streamlit`)
- [ ] Pydeck installed (`pip list | grep pydeck`)
- [ ] All requirements installed (`pip install -r requirements.txt`)

## 🏠 Home Page Tests

### Visual Elements
- [ ] Page loads without errors
- [ ] Pydeck map renders
- [ ] Route arcs visible radiating from CBD
- [ ] Routes are color-coded (red, orange, yellow, green)
- [ ] Metrics panel visible at bottom
- [ ] Legend panel visible at bottom right
- [ ] All 4 metrics display correctly:
  - [ ] Routes: "136"
  - [ ] Stops: "4,284"
  - [ ] Impact: shows population
  - [ ] Wards: "88"

### Interactions
- [ ] Can hover over routes to see tooltip
- [ ] Tooltip shows route_id and route_name
- [ ] Map is zoomable and pannable
- [ ] Dark mode styling applied

## ℹ️ About Page Tests

### Content Sections
- [ ] Project Overview section loads
- [ ] Metrics cards display (94%, 1.8M, 15%)
- [ ] The Problem section visible
- [ ] Our Solution section visible
- [ ] GNN vs Traditional ML table renders correctly
- [ ] Impact & Results section loads
- [ ] Technology Stack badges visible
- [ ] Team & Contact section loads

### Styling
- [ ] Dark theme consistent
- [ ] All sections have proper spacing
- [ ] Text is readable (good contrast)
- [ ] Tables formatted correctly
- [ ] Tech badges styled properly

## 🗺️ Route Explorer Tests

### Route Selection
- [ ] Dropdown loads with route options
- [ ] Shows 27 routes (or however many have variants)
- [ ] Route selection updates the page
- [ ] Selected route info displays

### Map Visualization
- [ ] Map renders for selected route
- [ ] Original route (blue) visible
- [ ] Route path follows road network
- [ ] Original stops (blue circles) visible
- [ ] Map centers on selected route
- [ ] Can zoom and pan map
- [ ] Legend displays correctly

### Variant Panel
- [ ] Original route card displays
- [ ] Shows correct number of stops
- [ ] Variant cards render (A, B, C)
- [ ] Each variant shows:
  - [ ] GNN Score
  - [ ] New Stops count
  - [ ] Population served
  - [ ] Equity multiplier
- [ ] Variant cards have correct colors:
  - [ ] Variant A: Green border
  - [ ] Variant B: Yellow border
  - [ ] Variant C: Red border
- [ ] Expanders show detailed metrics
- [ ] "View Variant" buttons work (show success message)

### Multiple Route Tests
Test with at least 3 different routes:
- [ ] Route 1: ________________ (fill in route_id tested)
- [ ] Route 2: ________________
- [ ] Route 3: ________________
- [ ] All routes load correctly
- [ ] Variants display properly for each

## 🎨 Theme & Design Tests

### Dark Mode
- [ ] Background is dark (#0e1117)
- [ ] Text is light/white
- [ ] Good contrast throughout
- [ ] Panels are semi-transparent
- [ ] Buttons are styled (green)

### Responsive Design
- [ ] Works on full screen
- [ ] Works on smaller window (laptop size)
- [ ] Sidebar collapses properly
- [ ] Map scales correctly

### Navigation
- [ ] Sidebar shows all 3 pages
- [ ] Can navigate between pages
- [ ] Page state persists correctly
- [ ] Back button works in browser

## 🔧 Performance Tests

### Load Times
- [ ] First page load < 15 seconds
- [ ] Subsequent page loads < 2 seconds
- [ ] Route switching < 1 second
- [ ] Map rendering smooth (no lag)

### Memory
- [ ] No errors in browser console
- [ ] No Python errors in terminal
- [ ] App doesn't crash during use
- [ ] Can switch routes multiple times without issues

## 🐛 Error Handling

### Expected Errors (Should NOT occur)
- [ ] No "ModuleNotFoundError"
- [ ] No "FileNotFoundError"
- [ ] No "KeyError" in data loading
- [ ] No Streamlit errors
- [ ] No Pydeck rendering errors

### Edge Cases
- [ ] Selecting first route works
- [ ] Selecting last route works
- [ ] Rapid route switching works
- [ ] Refreshing page works

## 📱 Browser Compatibility

Test in at least 2 browsers:
- [ ] Chrome/Chromium
- [ ] Firefox
- [ ] Safari (if on Mac)

## 🎯 Showcase Readiness

### Demo Flow
- [ ] Can explain Home page (30 seconds)
- [ ] Can explain About page (1 minute)
- [ ] Can demo Route Explorer (2 minutes)
- [ ] Can answer questions about methodology

### Data Accuracy
- [ ] Metrics match your research
- [ ] Route counts are correct
- [ ] Population numbers accurate
- [ ] GNN scores match model output

### Polish
- [ ] No typos in text
- [ ] Professional appearance
- [ ] Smooth interactions
- [ ] Impressive visuals

## 🚀 Final Launch Test

Run this complete flow:
1. [ ] Close all browser tabs
2. [ ] Stop any running Streamlit instances
3. [ ] Launch app with `./run_app.sh`
4. [ ] App opens in browser automatically
5. [ ] Navigate through all 3 pages
6. [ ] Test Route Explorer with 3 routes
7. [ ] Check browser console (no errors)
8. [ ] Stop app cleanly (Ctrl+C)

## 📝 Notes & Issues

Document any issues found:

### Issue 1:
**Description:**
**Status:**
**Fix:**

### Issue 2:
**Description:**
**Status:**
**Fix:**

### Issue 3:
**Description:**
**Status:**
**Fix:**

---

## ✅ Sign-Off

- [ ] All critical tests passed
- [ ] App is showcase-ready
- [ ] Known issues documented
- [ ] Backup plan prepared

**Tested by:** _______________
**Date:** _______________
**Status:** _______________
