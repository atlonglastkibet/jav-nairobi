"""
Route Explorer page - Direct Folium HTML embedding for full interactivity.
Preserves all notebook features including click-to-view stats.
"""

import streamlit as st
import streamlit.components.v1 as components
import sys
import base64
from pathlib import Path

# Add paths for imports
PROJECT_ROOT = Path(__file__).parent.parent.parent
STREAMLIT_APP_ROOT = Path(__file__).parent.parent

# Helper function for image encoding
def get_image_base64(image_path):
    """Convert image to base64 for inline display."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Add streamlit_app to path first for its utils
sys.path.insert(0, str(STREAMLIT_APP_ROOT))
from utils.data_loader import get_routes_with_variants, prepare_folium_route_data
from utils.styling import get_custom_css

# Now add project root and import viz_utils
sys.path.insert(0, str(PROJECT_ROOT))

# Import viz_utils explicitly from project root
import importlib.util
spec = importlib.util.spec_from_file_location("viz_utils", PROJECT_ROOT / "utils" / "viz_utils.py")
viz_utils = importlib.util.module_from_spec(spec)
spec.loader.exec_module(viz_utils)
plot_route_variants_folium = viz_utils.plot_route_variants_folium

# Page config
st.set_page_config(
    page_title="Route Explorer",
    page_icon=str(STREAMLIT_APP_ROOT / "assets" / "jav-nairobi white.png"),
    layout="wide"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Additional CSS for full-width embedding
st.markdown("""
<style>
    /* Remove default padding for full-width map */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0;
        max-width: 100%;
        padding-left: 1rem;
        padding-right: 1rem;
    }

    /* Style for route selector */
    .stSelectbox {
        margin-bottom: 16px;
    }

    /* Logo and title styling */
    .route-explorer-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 12px;
    }

    .route-explorer-logo {
        width: 60px;
        height: 60px;
        object-fit: cover;
        border-radius: 8px;
    }

    .route-explorer-title {
        font-size: 32px;
        font-weight: 700;
        color: #e0e0e0;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# Logo and Title
logo_path = STREAMLIT_APP_ROOT / "assets" / "route_explorer.jpg"
if logo_path.exists():
    st.markdown(f"""
    <div class="route-explorer-header">
        <img src="data:image/jpeg;base64,{get_image_base64(str(logo_path))}" class="route-explorer-logo" alt="Route Explorer">
        <h1 class="route-explorer-title">Route Explorer</h1>
    </div>
    """, unsafe_allow_html=True)
else:
    st.title("🚍 Route Explorer")

# Load OSMnx graph (cached)
@st.cache_resource
def load_osmnx_graph():
    """Load Nairobi road network graph."""
    import osmnx as ox
    from pathlib import Path

    # Path to cached graph (same as in notebooks)
    graph_path = PROJECT_ROOT / "data" / "processed" / "nairobi_drive.graphml"

    try:
        # Try to load cached graph first
        if graph_path.exists():
            G = ox.load_graphml(str(graph_path))
            return G
        else:
            # Fallback: download from OSM
            st.warning("Downloading road network from OpenStreetMap (this may take a few minutes)...")
            G = ox.graph_from_place("Nairobi, Kenya", network_type='drive')
            # Save for next time
            ox.save_graphml(G, str(graph_path))
            return G
    except Exception as e:
        st.error(f"Could not load road network: {e}")
        return None

# Load routes with variants
routes_list = get_routes_with_variants()

if len(routes_list) == 0:
    st.error("No routes with variants found. Please check data loading.")
    st.stop()

# Route selection
route_options = {r['display_name']: r['route_id'] for r in routes_list}
selected_display = st.selectbox(
    "Select a route:",
    options=list(route_options.keys()),
    index=0
)

selected_route_id = route_options[selected_display]

# Load data for Folium visualization
with st.spinner("Loading route data..."):
    folium_data = prepare_folium_route_data(selected_route_id)

if folium_data is None:
    st.error(f"Could not load data for route {selected_route_id}")
    st.stop()

# Load road network graph
with st.spinner("Loading road network..."):
    G = load_osmnx_graph()

if G is None:
    st.warning("Road network unavailable. Visualization will use straight lines between stops.")
    st.stop()

# Generate Folium map and get HTML
with st.spinner("Generating interactive map..."):
    try:
        folium_map = plot_route_variants_folium(
            route_id=folium_data['route_id'],
            G=G,
            route_geometries=folium_data['route_geometries'],
            variants_df=folium_data['variants_df'],
            selected_candidates=folium_data['selected_candidates'],
            feed=folium_data['feed'],
            df=folium_data['df'],
            max_variants_to_plot=3,
            output_path=None  # Don't save to file
        )

        # Get the HTML representation of the Folium map
        folium_html = folium_map._repr_html_()

        # Embed the HTML directly using Streamlit's components
        components.html(folium_html, height=800, scrolling=False)

    except Exception as e:
        st.error(f"Error generating map: {e}")
        import traceback
        st.code(traceback.format_exc())

# Instructions and Info (below map)
st.markdown("---")

st.markdown("### 📖 How to Use")
st.markdown("""
**Interactive Controls:**
- 🗺️ **Click colored route lines** on the map to view detailed metrics in the floating stats panel
- 🔍 **Toggle layers** using the control in the top-right corner of the map
- 📍 **Hover over stops** to see stop details
- 🔄 **Compare variants** by toggling multiple routes and clicking to compare their stats
- 💡 **Click any route line** to update the left panel with that variant's statistics

**Color Legend:**
- 🔵 **Blue** = Existing route and stops
- 🟢 **Green** = Recommended extension (Variant A - highest GNN score)
- 🟡 **Yellow** = Alternative 1 (Variant B)
- 🔴 **Red** = Alternative 2 (Variant C)

**Features:**
- **Floating Stats Panel** (left) - Shows real-time metrics for selected variant
- **Route Header** (top-left) - Displays current route and selected variant
- **Legend** (bottom-right) - Quick reference for route types
- **Layer Control** (top-right) - Toggle route visibility
""")

st.markdown("---")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### 🎯 Recommended Extension")
    st.markdown("""
    Green routes represent the highest-scoring GNN recommendation, optimized for:
    - Maximum equity impact
    - Population coverage
    - Temporal service balance
    """)

with col2:
    st.markdown("### 📊 Metrics Explained")
    st.markdown("""
    - **Score**: Overall GNN recommendation score
    - **Equity**: Multiplier for underserved areas
    - **Coverage**: Population accessibility
    - **Temporal**: Time-based service equity
    """)

with col3:
    st.markdown("### 🔄 Alternative Variants")
    st.markdown("""
    Yellow and red routes show alternative extension options with different trade-offs between equity, coverage, and feasibility.
    """)
