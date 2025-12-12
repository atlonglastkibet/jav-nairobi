"""
GNN Stop Predictor Test - Testing improved map selection logic.
Click anywhere on the map to evaluate potential stop locations in real-time.
"""

import streamlit as st
import pydeck as pdk
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import torch
import torch.nn.functional as F
from torch_geometric.nn import GCNConv
from torch_geometric.data import Data
import base64
from pathlib import Path
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

# Add paths for imports
STREAMLIT_APP_ROOT = Path(__file__).parent.parent.absolute()
PROJECT_ROOT = STREAMLIT_APP_ROOT.parent

import sys
sys.path.insert(0, str(STREAMLIT_APP_ROOT))
from utils.styling import get_custom_css
from utils.data_loader import CBD_LAT, CBD_LON, prepare_routes_with_paths, get_stops_for_map

# Helper function for image encoding
def get_image_base64(image_path):
    """Convert image to base64 for inline display."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Page config
st.set_page_config(
    page_title="GNN Stop Predictor",
    page_icon=str(STREAMLIT_APP_ROOT / "assets" / "jav-nairobi white.png"),
    layout="wide"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Additional CSS
st.markdown("""
<style>
    .predictor-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 12px;
    }

    .predictor-title {
        font-size: 32px;
        font-weight: 700;
        color: #e0e0e0;
        margin: 0;
    }

    .score-gauge {
        background: rgba(30, 33, 40, 0.8);
        border-radius: 12px;
        padding: 24px;
        text-align: center;
    }

    .score-number {
        font-size: 64px;
        font-weight: 700;
        margin: 16px 0;
    }

    .score-excellent {
        color: rgb(70, 204, 113);
    }

    .score-good {
        color: rgb(241, 196, 15);
    }

    .score-poor {
        color: rgb(231, 76, 60);
    }

    .feature-bar {
        background: rgba(50, 53, 60, 0.6);
        border-radius: 4px;
        margin: 8px 0;
        padding: 8px;
    }

    .feature-name {
        font-size: 13px;
        color: #ccc;
        margin-bottom: 4px;
    }

    .feature-progress {
        background: rgba(70, 73, 80, 0.6);
        height: 8px;
        border-radius: 4px;
        overflow: hidden;
    }

    .feature-fill {
        height: 100%;
        background: linear-gradient(90deg, #1A73E8, #34A853);
        transition: width 0.3s ease;
    }

    .instruction-box {
        background: rgba(26, 115, 232, 0.1);
        border-left: 4px solid rgb(26, 115, 232);
        padding: 16px;
        border-radius: 4px;
        margin: 16px 0;
    }

    .result-card {
        background: rgba(30, 33, 40, 0.8);
        border-radius: 8px;
        padding: 16px;
        margin: 12px 0;
    }

    /* Content Section Styling from App.py */
    .content-section {
        background: rgba(255, 255, 255, 0.02);
        border-radius: 16px;
        padding: 2rem;
        margin: 2rem 0;
        border: 1px solid rgba(255, 255, 255, 0.05);
    }
    .section-title {
        font-size: 0.9rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        color: #E74C3C;
        margin-bottom: 1rem;
        text-transform: uppercase;
    }
    .section-content {
        font-size: 1.1rem;
        line-height: 1.6;
        color: #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Define GNN Model Architecture (must match training)
class GCN(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, hidden_channels)
        self.conv3 = GCNConv(hidden_channels, hidden_channels // 2)
        self.lin = torch.nn.Linear(hidden_channels // 2, out_channels)

    def forward(self, x, edge_index):
        x = self.conv1(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.3, training=self.training)

        x = self.conv2(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.3, training=self.training)

        x = self.conv3(x, edge_index)
        x = F.relu(x)
        x = F.dropout(x, p=0.3, training=self.training)

        x = self.lin(x)
        return x

# Load GNN model
@st.cache_resource
def load_gnn_model():
    """Load trained GNN model."""
    model_path = PROJECT_ROOT / "data" / "model" / "best_model.pt"

    if not model_path.exists():
        st.error(f"Model file not found at {model_path}")
        return None

    try:
        # Model expects 132 input features (35 numeric + one-hot encoded categoricals), 2 output classes
        model = GCN(in_channels=132, hidden_channels=128, out_channels=2)
        model.load_state_dict(torch.load(model_path, map_location=torch.device('cpu')))
        model.eval()
        return model
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

# Load candidate stops data
@st.cache_data
def load_candidates_data():
    """Load all candidate stops with features."""
    candidates_path = PROJECT_ROOT / "data" / "training_output" / "all_candidates_equity.csv"

    if not candidates_path.exists():
        st.error(f"Candidates file not found at {candidates_path}")
        return None

    df = pd.read_csv(candidates_path)
    return df

# Feature columns (must match training)
# Numeric features (35 total)
NUM_COLS = [
    'nearest_node_degree', 'distance_to_major_road', 'distance_to_nearest_stop',
    'stops_within_500m', 'stops_within_1km', 'pop_not_served_nearby',
    'poverty_rate_weighted_pop', 'route_count_serving', 'trips_per_day',
    'avg_headway_minutes', 'service_span_hours', 'routes_within_500m',
    'avg_speed_daily', 'avg_speed_peak', 'avg_speed_offpeak',
    'congestion_pct_daily', 'congestion_pct_peak', 'trip_count_daily',
    'trip_count_peak', 'demand_variability_cv', 'ward_pct_access',
    'ward_population', 'ward_poverty_rate', 'distance_to_cbd',
    'coverage_efficiency_nearby', 'demand_supply_ratio', 'network_accessibility',
    'pop_within_500m', 'trips_per_1k_pop_per_hour', 'subcounty_gini',
    'pop_score', 'coverage_score', 'access_score', 'poverty_score', 'quality_score'
]

# Categorical features (4 total, one-hot encoded)
CAT_COLS = ['ward', 'road_type', 'dominant_congestion_level', 'ward_category']

# Create preprocessing pipeline
@st.cache_resource
def create_preprocessor(_candidates_df):
    """Create and fit preprocessing pipeline on candidate data."""
    numeric_transformer = Pipeline([
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline([
        ("encoder", OneHotEncoder(handle_unknown="ignore", sparse_output=False))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, NUM_COLS),
            ("cat", categorical_transformer, CAT_COLS),
        ],
        remainder="drop"
    )

    # Fit on all candidate data
    preprocessor.fit(_candidates_df[NUM_COLS + CAT_COLS])
    return preprocessor

# Load data and model
model = load_gnn_model()
candidates_df = load_candidates_data()

if model is None or candidates_df is None:
    st.error("Failed to load required data. Please check model and data files.")
    st.stop()

# Create preprocessor
preprocessor = create_preprocessor(candidates_df)

# Load route data
@st.cache_data
def load_path_data():
    return prepare_routes_with_paths()

routes_path_df = load_path_data()

# Header
logo_path = STREAMLIT_APP_ROOT / "assets" / "gnn_pred.jpg"
if logo_path.exists():
    logo_img = f'<img src="data:image/jpeg;base64,{get_image_base64(logo_path)}" class="community-logo" style="width: 60px; height: 60px; border-radius: 50%;"/>'
else:
    logo_img = '🤖'

st.markdown(f"""
<div class="predictor-header">
    {logo_img}
    <h1 class="predictor-title">GNN Stop Predictor</h1>
</div>
""", unsafe_allow_html=True)

st.markdown("**Interactive stop quality evaluation using Graph Neural Networks**")

# Instructions
st.markdown("""
<div class="content-section">
    <div class="section-title">HOW IT WORKS</div>
    <div class="section-content">
        The GNN Stop Predictor leverages advanced Graph Neural Networks to evaluate potential transit stop locations in real-time. By analyzing over 40 distinct features—including population density, infrastructure access, and equity metrics—the model predicts the viability of new stops with high precision. The interactive map visualizes both existing network coverage (blue) and high-potential candidate locations (green). Simply select any point on the map to instantly generate a comprehensive quality score and detailed feature breakdown, empowering data-driven decisions for network expansion.
    </div>
</div>
""", unsafe_allow_html=True)

# Initialize session state for clicked coordinates
if 'clicked_lat' not in st.session_state:
    st.session_state.clicked_lat = -1.2921
if 'clicked_lon' not in st.session_state:
    st.session_state.clicked_lon = 36.8219

# Layout: Map on left, Results on right
col_map, col_results = st.columns([1.5, 1])

with col_map:
    # Prepare map data using the shared utility that includes BOTH existing and candidate stops
    all_stops = get_stops_for_map()
    
    # Reset index to ensure we can look up by index correctly
    all_stops = all_stops.reset_index(drop=True)

    # Create selected point layer
    selected_point_df = pd.DataFrame([{
        'lat': st.session_state.clicked_lat,
        'lon': st.session_state.clicked_lon,
        'color': [255, 255, 255, 255],  # White
        'size': 80
    }])

    # Create PyDeck layers
    scatter_layer = pdk.Layer(
        'ScatterplotLayer',
        id='stops-layer',  # Required for selection events
        data=all_stops,
        get_position='[lon, lat]',
        get_color='color',
        get_radius='size',
        radius_scale=1,
        radius_min_pixels=3,
        radius_max_pixels=12,
        pickable=True,
        auto_highlight=True,
        opacity=0.7
    )

    # Selected point layer (always on top)
    selected_layer = pdk.Layer(
        'ScatterplotLayer',
        data=selected_point_df,
        get_position='[lon, lat]',
        get_color='color',
        get_radius='size',
        radius_scale=1,
        radius_min_pixels=10,
        radius_max_pixels=15,
        pickable=False,
        opacity=1.0
    )

    view_state = pdk.ViewState(
        latitude=CBD_LAT,
        longitude=CBD_LON,
        zoom=10.3,
        pitch=0,
        bearing=0,
        min_zoom=9,
        max_zoom=15
    )

    # Create PathLayer for routes
    path_layer = pdk.Layer(
        'PathLayer',
        data=routes_path_df,
        get_path='path',
        get_color='color_with_alpha',
        get_width='width',
        width_min_pixels=1,
        width_max_pixels=3,
        pickable=False, # Disable picking for routes to avoid interfering with stops
        opacity=0.4
    )

    deck = pdk.Deck(
        layers=[path_layer, scatter_layer, selected_layer],
        initial_view_state=view_state,
        map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
        tooltip={
            'html': '<b>{stop_id}</b><br/>Ward: {ward}<br/>GNN Score: {gnn_probability:.2f}',
            'style': {
                'backgroundColor': 'rgba(14, 17, 23, 0.9)',
                'color': 'white',
                'borderRadius': '8px',
                'padding': '10px'
            }
        }
    )

    # Display the map with selection enabled
    event = st.pydeck_chart(
        deck,
        use_container_width=True,
        height=700,
        on_select="rerun",
        selection_mode="single-object",
        key="gnn_map_test"
    )

    # Handle selection event
    if event:
        if len(event.selection) > 0:
            # Try to get selected data - check multiple possible structures
            selected_data = None
            
            # 1. Direct layer access
            if 'stops-layer' in event.selection:
                selected_data = event.selection['stops-layer']
            
            # 2. Fallback: Check values if layer name mismatch or other structure
            elif hasattr(event, 'selection') and isinstance(event.selection, dict):
                # If there's any selection, take the first one
                values = list(event.selection.values())
                if len(values) > 0:
                    selected_data = values[0]

            if selected_data:
                # Check for indices (standard PyDeck selection)
                if 'indices' in selected_data and len(selected_data['indices']) > 0:
                    # Get the index of the clicked stop
                    idx = selected_data['indices'][0]

                    # Get the corresponding stop from our dataframe
                    if idx < len(all_stops):
                        clicked_stop = all_stops.iloc[idx]
                        
                        # Only update if changed to avoid infinite loops
                        if (clicked_stop['lat'] != st.session_state.clicked_lat or 
                            clicked_stop['lon'] != st.session_state.clicked_lon):
                            
                            st.session_state.clicked_lat = clicked_stop['lat']
                            st.session_state.clicked_lon = clicked_stop['lon']
                            st.rerun()

    # Legend
    st.markdown("""
    <div class="legend-inline">
        <div class="legend-inline-item">
            <div class="legend-inline-color" style="background: rgb(26, 115, 232);"></div>
            <span>Existing Stops</span>
        </div>
        <div class="legend-inline-item">
            <div class="legend-inline-color" style="background: rgb(70, 204, 113);"></div>
            <span>GNN Candidates</span>
        </div>
        <div class="legend-inline-item">
            <div class="legend-inline-color" style="background: rgb(255, 255, 255);"></div>
            <span>Selected Location</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Define second row for results (below the map/inputs columns)
row2_col1, row2_col2 = st.columns(2)

with col_results:
    st.markdown("### Evaluate Location")

    st.markdown("<br/>", unsafe_allow_html=True)

    # Input coordinates - sync with session state
    test_lat = st.number_input("Latitude", value=st.session_state.clicked_lat, format="%.6f", key="lat_input")
    test_lon = st.number_input("Longitude", value=st.session_state.clicked_lon, format="%.6f", key="lon_input")

    # Update session state if user manually changes inputs
    if test_lat != st.session_state.clicked_lat or test_lon != st.session_state.clicked_lon:
        st.session_state.clicked_lat = test_lat
        st.session_state.clicked_lon = test_lon
        # Optional: rerun to update map marker immediately
        # st.rerun() 

    st.markdown("""
    <div style="font-size: 12px; color: #888; margin-top: 8px;">
    Note: Analysis uses pre-computed GNN scores from the nearest candidate location.
    </div>
    """, unsafe_allow_html=True)

    # Analyze when button is pressed
    if st.button("Analyze Location", type="primary"):
        with st.spinner("Finding nearest candidate..."):
            # Find nearest candidate stop that has been evaluated by GNN
            distances = np.sqrt((candidates_df['lat'] - test_lat)**2 + (candidates_df['lon'] - test_lon)**2)
            nearest_idx = distances.idxmin()
            nearest_stop = candidates_df.iloc[nearest_idx]
            nearest_distance = distances[nearest_idx] * 111  # Convert to km (rough approximation)

            # Extract features for the point
            try:
                # Use pre-computed GNN probability (already in dataset)
                if 'gnn_probability' in nearest_stop and pd.notna(nearest_stop['gnn_probability']):
                    quality_score = nearest_stop['gnn_probability'] * 100
                else:
                    # Fallback: use quality_score if available
                    quality_score = nearest_stop.get('quality_score', 50)

                # Display results
                if quality_score >= 75:
                    score_class = "score-excellent"
                    verdict = "Excellent Location"
                    verdict_color = "rgb(70, 204, 113)"
                elif quality_score >= 50:
                    score_class = "score-good"
                    verdict = "Moderate Location"
                    verdict_color = "rgb(241, 196, 15)"
                else:
                    score_class = "score-poor"
                    verdict = "Poor Location"
                    verdict_color = "rgb(231, 76, 60)"

                st.markdown(f"""
                <div class="score-gauge">
                    <div style="font-size: 14px; color: #888;">Quality Score</div>
                    <div class="score-number {score_class}">{quality_score:.1f}%</div>
                    <div style="font-size: 16px; font-weight: 600; color: {verdict_color};">{verdict}</div>
                </div>
                """, unsafe_allow_html=True)

                # --- Location Details (Bottom Left) ---
                with row2_col1:
                    st.markdown("### Location Details")
                    
                    # Metrics Grid
                    m1, m2 = st.columns(2)
                    with m1:
                        st.metric(
                            "Nearest Candidate", 
                            f"{nearest_distance:.2f} km",
                            help="Distance to the closest GNN-evaluated stop candidate."
                        )
                        st.metric(
                            "Population (500m)", 
                            f"{int(nearest_stop['pop_within_500m']):,}",
                            help="Estimated number of residents within a 500m walking radius."
                        )
                        st.metric(
                            "Distance to CBD", 
                            f"{nearest_stop['distance_to_cbd']:.1f} km",
                            help="Straight-line distance to the Central Business District."
                        )
                    
                    with m2:
                        st.metric(
                            "Ward", 
                            f"{nearest_stop['ward']}",
                            help="Administrative ward where this location is situated."
                        )
                        st.metric(
                            "Existing Stops", 
                            f"{int(nearest_stop['stops_within_500m'])}",
                            help="Number of existing matatu stops within 500m."
                        )
                        st.metric(
                            "Ward Coverage", 
                            f"{nearest_stop['ward_pct_access']:.1f}%",
                            help="Percentage of ward population currently within 500m of a stop."
                        )

                # --- Feature Analysis (Bottom Right) ---
                with row2_col2:
                    st.markdown("### Feature Analysis")

                    # Top contributing features
                    feature_importance = {
                        'Population Density': nearest_stop['pop_within_500m'] / 10000 * 100,
                        'Infrastructure Access': (1 - nearest_stop['distance_to_major_road'] / 1000) * 100,
                        'Service Gap': (1 - min(nearest_stop['stops_within_500m'] / 5, 1)) * 100,
                        'Equity Impact': (1 - nearest_stop['ward_pct_access'] / 100) * 100,
                        'Poverty Score': nearest_stop['poverty_score'] if 'poverty_score' in nearest_stop else 50,
                        'Coverage Efficiency': nearest_stop['coverage_efficiency_nearby'] * 100 if 'coverage_efficiency_nearby' in nearest_stop else 50
                    }

                    # Prepare data for Radar Chart
                    categories = list(feature_importance.keys())
                    values = list(feature_importance.values())
                    
                    # Clamp values to 0-100
                    values = [max(0, min(100, v)) for v in values]

                    # Close the loop for radar chart
                    categories = [*categories, categories[0]]
                    values = [*values, values[0]]

                    fig = go.Figure(
                        data=[
                            go.Scatterpolar(
                                r=values,
                                theta=categories,
                                fill='toself',
                                name='Location Score',
                                line_color='rgb(70, 204, 113)',
                                fillcolor='rgba(70, 204, 113, 0.3)'
                            )
                        ],
                        layout=go.Layout(
                            polar=dict(
                                radialaxis=dict(
                                    visible=True,
                                    range=[0, 100],
                                    showticklabels=False,
                                    linecolor='rgba(255, 255, 255, 0.1)',
                                    gridcolor='rgba(255, 255, 255, 0.1)'
                                ),
                                angularaxis=dict(
                                    tickfont=dict(size=10, color='#ccc'),
                                    linecolor='rgba(255, 255, 255, 0.1)',
                                    gridcolor='rgba(255, 255, 255, 0.1)'
                                ),
                                bgcolor='rgba(0,0,0,0)'
                            ),
                            paper_bgcolor='rgba(0,0,0,0)',
                            plot_bgcolor='rgba(0,0,0,0)',
                            margin=dict(l=40, r=40, t=20, b=20),
                            showlegend=False,
                            height=300
                        )
                    )
                    
                    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            except Exception as e:
                st.error(f"Error running inference: {e}")
                st.code(str(e))

# Footer
st.markdown("""
<div class="app-footer">
    <div class="footer-text">
        <strong>JAV-NAIROBI</strong> &copy; 2025<br/>
        Built by <strong>David Kibet</strong><br/>
        <a href="mailto:atlonglastkibet@gmail.com">Email</a> |
        <a href="https://github.com/atlonglastkibet/jav-nairobi" target="_blank">Project Link</a>
    </div>
</div>
""", unsafe_allow_html=True)
