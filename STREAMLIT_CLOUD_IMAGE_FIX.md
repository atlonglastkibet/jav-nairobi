# Streamlit Cloud Image Path Fix

## Problem

When deploying to Streamlit Cloud, the app crashed with:
```
streamlit.runtime.media_file_storage.MediaFileStorageError: This app has encountered an error.
Error opening 'assets/jav-nairobi.png'
```

**Root Cause:** Relative paths don't work on Streamlit Cloud. The app was using:
```python
st.image("assets/jav-nairobi.png")
page_icon="assets/jav-nairobi white.png"
```

## Solution

Use absolute paths constructed with `pathlib.Path`:

### Files Fixed

#### 1. [streamlit_app/app.py](streamlit_app/app.py)
```python
from pathlib import Path

# Get the absolute path to the streamlit_app directory
STREAMLIT_APP_ROOT = Path(__file__).parent.absolute()

# Page config
st.set_page_config(
    page_title="",
    page_icon=str(STREAMLIT_APP_ROOT / "assets" / "jav-nairobi white.png"),
    ...
)

# Logo
logo_path = STREAMLIT_APP_ROOT / "assets" / "jav-nairobi.png"
st.image(str(logo_path))
```

#### 2. [streamlit_app/pages/1_Route_Explorer.py](streamlit_app/pages/1_Route_Explorer.py)
```python
# Already had STREAMLIT_APP_ROOT defined, just updated page_icon
st.set_page_config(
    page_title="Route Explorer",
    page_icon=str(STREAMLIT_APP_ROOT / "assets" / "jav-nairobi white.png"),
    ...
)
```

#### 3. [streamlit_app/pages/2_Wiki.py](streamlit_app/pages/2_Wiki.py)
```python
from pathlib import Path

# Get the absolute path to the streamlit_app directory
STREAMLIT_APP_ROOT = Path(__file__).parent.parent.absolute()

st.set_page_config(
    page_title="Wiki",
    page_icon=str(STREAMLIT_APP_ROOT / "assets" / "jav-nairobi white.png"),
    ...
)
```

#### 4. [streamlit_app/pages/3_Traffic.py](streamlit_app/pages/3_Traffic.py)
```python
# Already had STREAMLIT_APP_ROOT defined, just updated page_icon
st.set_page_config(
    page_title="Traffic",
    page_icon=str(STREAMLIT_APP_ROOT / "assets" / "jav-nairobi white.png"),
    ...
)
```

## Why This Works

### Local Development
- Relative paths work because the working directory is predictable
- `"assets/jav-nairobi.png"` resolves relative to CWD

### Streamlit Cloud
- Working directory can vary
- `Path(__file__)` always gives the script's location
- `.parent` navigates to parent directory
- `.absolute()` ensures full path
- Construct paths with `/` operator (works on all OS)

## Pattern to Use

**For any file in `streamlit_app/`:**
```python
from pathlib import Path

STREAMLIT_APP_ROOT = Path(__file__).parent.absolute()
asset_path = STREAMLIT_APP_ROOT / "assets" / "filename.png"
st.image(str(asset_path))
```

**For files in `streamlit_app/pages/`:**
```python
from pathlib import Path

STREAMLIT_APP_ROOT = Path(__file__).parent.parent.absolute()  # Note: .parent.parent
asset_path = STREAMLIT_APP_ROOT / "assets" / "filename.png"
st.image(str(asset_path))
```

## Verified Assets

All required assets exist in `streamlit_app/assets/`:
- ✅ `jav-nairobi.png` (16 KB)
- ✅ `jav-nairobi white.png` (10 KB)
- ✅ `traffic_lights.jpg` (26 KB)
- ✅ `route_explorer.jpg` (10 KB)
- ✅ `favicon.png` (5 KB)

## Testing

**Local:** All pages should work as before
**Streamlit Cloud:** All pages should now load without MediaFileStorageError

## Additional Notes

- The Traffic and Route Explorer pages use base64 encoding for some images (logo in header)
- Those already use absolute paths via `STREAMLIT_APP_ROOT`, so they work fine
- Only `st.image()` and `page_icon` needed fixing

## Status

✅ **Fixed** - All image paths now use absolute paths
✅ **Deployed** - Ready to redeploy to Streamlit Cloud
