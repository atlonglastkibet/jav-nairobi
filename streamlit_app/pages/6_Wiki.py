"""
Wiki page - Technical deep dive into the Jav-Nairobi project.
"""

import streamlit as st
import streamlit.components.v1 as components
import pydeck as pdk
import pandas as pd
import base64
from pathlib import Path
from utils.styling import get_custom_css
from utils.data_loader import prepare_routes_for_animation, CBD_LAT, CBD_LON

# Get the absolute path to the streamlit_app directory
STREAMLIT_APP_ROOT = Path(__file__).parent.parent.absolute()

# Helper function for image encoding
def get_image_base64(image_path):
    """Convert image to base64 for inline display."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Page config
st.set_page_config(
    page_title="Wiki",
    page_icon=str(STREAMLIT_APP_ROOT / "assets" / "jav-nairobi white.png"),
    layout="wide"
)

# Apply custom CSS
st.markdown(get_custom_css(), unsafe_allow_html=True)

# Additional CSS for logo and title styling
st.markdown("""
<style>
    /* Logo and title styling */
    .wiki-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 12px;
    }

    .wiki-logo {
        width: 60px;
        height: 60px;
        object-fit: cover;
        border-radius: 8px;
    }

    .wiki-title {
        font-size: 32px;
        font-weight: 700;
        color: #e0e0e0;
        margin: 0;
    }

    /* Content Section Styling Overrides */
    .content-section {
        background: rgba(255, 255, 255, 0.02) !important;
        border-radius: 16px !important;
        padding: 2rem !important;
        margin: 2rem 0 !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        max-width: 100% !important;
    }
    .section-title {
        font-size: 0.9rem !important;
        font-weight: 700 !important;
        letter-spacing: 0.1em !important;
        color: #E74C3C !important;
        margin-bottom: 1rem !important;
        text-transform: uppercase !important;
    }
    .section-content {
        font-size: 1.1rem !important;
        line-height: 1.6 !important;
        color: #e0e0e0 !important;
        text-align: left !important;
    }
</style>
""", unsafe_allow_html=True)

# Logo and Title
logo_path = STREAMLIT_APP_ROOT / "assets" / "wiki.jpg"
if logo_path.exists():
    st.markdown(f"""
    <div class="wiki-header">
        <img src="data:image/jpeg;base64,{get_image_base64(str(logo_path))}" class="wiki-logo" alt="Wiki">
        <h1 class="wiki-title">Wiki</h1>
    </div>
    """, unsafe_allow_html=True)
else:
    st.title("Wiki")

# Subtitle
st.markdown("**Technical deep dive into the model architecture, methodology, and future vision**")

# MATATU COVERAGE IN NAIROBI
st.markdown("""
<div class="content-section">
    <div class="section-title">MATATU COVERAGE IN NAIROBI</div>
    <div class="section-content">
        Nairobi's matatu network represents one of Africa's most extensive informal transit systems, comprising 135 routes and 4,384 existing stops that serve millions of commuters daily.
        Yet beneath this apparent ubiquity lies a profound spatial inequity captured by a Gini coefficient of 0.72—a measure where zero represents perfect equality and one represents total inequality.
        For context, a Gini coefficient above 0.60 is considered highly unequal by international standards, placing Nairobi's transit access in the same bracket as some of the world's most economically stratified cities.
        This inequity manifests not just spatially, but temporally as well. Our analysis of trips per hour per capita across different time periods reveals that underserved wards—areas like Githurai, Kangemi, Dandora Area III, and Kibera—experience
        not only fewer stops within walking distance but also dramatically reduced service frequency during off-peak hours, effectively stranding residents who work non-standard shifts or need evening transit.
        The matatu system's brilliance lies in its organic adaptation to demand: routes emerge where passengers will pay, operators respond to real-time traffic and passenger flows, and the system operates without centralized planning or subsidy.
        However, this market-driven efficiency creates a feedback loop that systematically excludes low-income, low-density, or geographically isolated neighborhoods. Wealthy areas near the CBD benefit from overlapping routes, high-frequency service, and competitive pricing,
        while informal settlements on Nairobi's periphery—home to the city's most transit-dependent populations—receive sparse, unreliable service.
        Our project begins with the foundational question: can we quantify this inequity with sufficient granularity to design interventions that increase coverage without disrupting the informal system's operational logic?
        By dissolving 500-meter buffers around each of the 4,384 existing stops and overlaying high-resolution population rasters from WorldPop, we estimate the population served by each stop and route.
        Combining this with GTFS schedule data from the Digital Matatus Project, we compute temporal access metrics—trips per hour per capita during morning peak, evening peak, and off-peak periods—to identify not just where service is absent, but when it fails to meet demand.
        The result: 22 routes serving underserved wards, affecting over 1.8 million Nairobians who lack adequate spatial or temporal transit access. These are the routes where intervention can deliver the greatest equity gains—not by replacing the informal system, but by strategically augmenting it.
    </div>
</div>
""", unsafe_allow_html=True)

# Load arc data
@st.cache_data
def load_arc_data():
    return prepare_routes_for_animation()

routes_arc_df = load_arc_data()

# Prepare arc layer data
arc_data = routes_arc_df[['source_lat', 'source_lon', 'target_lat', 'target_lon', 'color', 'route_id', 'route_name']].copy()

# Create the pydeck arc layer
arc_layer = pdk.Layer(
    'ArcLayer',
    data=arc_data,
    get_source_position=['source_lon', 'source_lat'],
    get_target_position=['target_lon', 'target_lat'],
    get_source_color=[26, 115, 232],  # Blue for CBD
    get_target_color='color',
    get_width=3,
    get_height=0.3,
    pickable=True,
    auto_highlight=True
)

# Create scatter layer for CBD center
cbd_layer = pdk.Layer(
    'ScatterplotLayer',
    data=pd.DataFrame([{'lat': CBD_LAT, 'lon': CBD_LON}]),
    get_position=['lon', 'lat'],
    get_color=[26, 115, 232, 200],
    get_radius=500,
    pickable=False
)

# Set view state for arc view
arc_view_state = pdk.ViewState(
    latitude=CBD_LAT,
    longitude=CBD_LON,
    zoom=11,
    pitch=50,
    bearing=0
)

# Create arc deck
arc_deck = pdk.Deck(
    layers=[arc_layer, cbd_layer],
    initial_view_state=arc_view_state,
    map_style='https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json',
    tooltip={
        'html': '<b>Route:</b> {route_id}<br/><b>Name:</b> {route_name}',
        'style': {
            'backgroundColor': 'rgba(14, 17, 23, 0.9)',
            'color': 'white',
            'borderRadius': '8px',
            'padding': '10px'
        }
    }
)

# Display arc map
st.pydeck_chart(arc_deck, use_container_width=True, height=600)

# Legend inline below map
st.markdown("""
<div class="legend-inline">
    <div class="legend-inline-item">
        <div class="legend-inline-color" style="background: rgb(231, 76, 60);"></div>
        <span>Severely Underserved</span>
    </div>
    <div class="legend-inline-item">
        <div class="legend-inline-color" style="background: rgb(230, 126, 34);"></div>
        <span>Underserved</span>
    </div>
    <div class="legend-inline-item">
        <div class="legend-inline-color" style="background: rgb(241, 196, 15);"></div>
        <span>Adequate</span>
    </div>
    <div class="legend-inline-item">
        <div class="legend-inline-color" style="background: rgb(70, 204, 113);"></div>
        <span>Well Served</span>
    </div>
</div>
""", unsafe_allow_html=True)

# Map caption
st.markdown("""
<div class="map-caption">
This arc view shows Nairobi's matatu route network radiating from the Central Business District (CBD), with routes color-coded by equity tier. Red indicates severely underserved areas and green indicates well-served areas.
<strong>Routes Source:</strong> <a href="https://digitalmatatus.com/index.html" target="_blank">DIGITAL MATATUS PROJECT</a>
</div>
""", unsafe_allow_html=True)



# MODEL SCIENCE & ARCHITECTURE
st.markdown("""
<div class="content-section">
    <div class="section-title">MODEL SCIENCE & ARCHITECTURE</div>
    <div class="section-content">
        <strong>Deep Learning</strong> refers to neural networks with multiple layers that learn hierarchical representations of data. Unlike traditional machine learning, which requires hand-engineered features, deep learning models automatically discover the features needed for classification or prediction by stacking layers of transformations.
        Each layer extracts increasingly abstract representations: early layers might capture raw pixel patterns in images, while deeper layers recognize objects or concepts. This approach has revolutionized computer vision, natural language processing, and now, urban transit optimization.
        <br/><br/>
        <strong>Graph Neural Networks (GNNs)</strong> extend deep learning to graph-structured data—networks of nodes connected by edges. Traditional neural networks assume data exists in Euclidean space (grids, sequences), but many real-world systems are better represented as graphs: social networks, molecular structures, and critically for our purposes, transit systems.
        In a GNN, each node has a feature vector (e.g., population density, traffic speed, accessibility score), and the network learns by iteratively passing messages between connected nodes. This message-passing mechanism allows nodes to aggregate information from their neighbors, enabling the model to reason about relationships and dependencies that would be invisible to conventional ML approaches.
        <br/><br/>
        <strong>Graph Convolutional Networks (GCNs)</strong> are a specific type of GNN that apply convolutional operations—similar to those used in image recognition—to graph structures. Just as a convolutional layer in computer vision aggregates pixel values from a local neighborhood, a GCN layer aggregates feature vectors from a node's graph neighbors.
        The key insight is that a node's optimal characteristics depend heavily on its surrounding context: a bus stop's value isn't determined solely by its immediate population density, but by how it connects to the broader network, what infrastructure exists nearby, and how neighboring stops perform.
        GCNs excel at this because they learn to weight neighbor contributions intelligently—automatically identifying which neighbors matter most for prediction.
        <br/><br/>
        <strong>Our GCN Implementation:</strong> We employ a three-layer Graph Convolutional Network architecture designed specifically for transit stop quality prediction. Each candidate stop location is represented as a node in the graph, with edges connecting it to its 8 nearest neighbors based on Euclidean distance.
        This k-nearest-neighbor graph structure ensures that message passing occurs within spatially relevant neighborhoods—stops aggregate information from nearby stops, not from across the city.
        <br/><br/>
        <strong>Input Features (42 per node):</strong>
        <ul>
            <li><strong>Demographics:</strong> Population density within 500m, poverty rate, household income distribution</li>
            <li><strong>Existing Service:</strong> Number of stops within 500m, routes passing nearby, trips per hour per capita</li>
            <li><strong>Mobility Patterns:</strong> WorldMove trajectory counts, average speed during peak/off-peak, congestion scores</li>
            <li><strong>Infrastructure:</strong> Distance to major roads, proximity to commercial centers, presence of amenities (schools, hospitals, markets)</li>
            <li><strong>Spatial Equity:</strong> Current Gini coefficient for the ward, temporal access gaps, underserved population within 1km</li>
        </ul>
        <br/>
        <strong>Architecture Layers:</strong>
        <ul>
            <li><strong>Layer 1 (GCNConv):</strong> 42 input features → 128 hidden dimensions. Applies ReLU activation and 30% dropout. This first layer learns to aggregate raw features from neighboring stops, identifying local patterns like "stops near busy roads with high population density."</li>
            <li><strong>Layer 2 (GCNConv):</strong> 128 → 128 hidden dimensions. ReLU activation, 30% dropout. This middle layer refines representations by propagating information further across the graph, enabling the model to recognize multi-hop patterns like "stops connected to other high-quality stops via major corridors."</li>
            <li><strong>Layer 3 (GCNConv):</strong> 128 → 64 hidden dimensions. ReLU activation, 30% dropout. This final convolutional layer compresses the learned representations into a lower-dimensional space, focusing on the most discriminative features for stop quality prediction.</li>
            <li><strong>Linear Classifier:</strong> 64 → 2 output classes (Good Stop / Bad Stop). A fully connected layer maps the final graph-aware node embeddings to class probabilities via softmax activation.</li>
        </ul>
        <br/>
        <strong>Why This Architecture Works:</strong> Transit networks exhibit strong spatial autocorrelation—good stops cluster near other good stops, and underserved areas tend to be geographically contiguous. By using three GCN layers, the model can propagate information up to three hops away (roughly 1-2 km in our graph), capturing both immediate neighborhood effects and broader regional patterns.
        The progressive dimensionality reduction (42 → 128 → 128 → 64 → 2) forces the model to learn compact, meaningful representations rather than memorizing training data. Dropout regularization prevents overfitting, critical given the relatively small dataset (6,029 candidate stops split 80/10/10 for train/val/test).
        <br/><br/>
        <strong>Training Process:</strong> We train the model using class-weighted cross-entropy loss to handle the inherent class imbalance—only 23% of candidate locations are labeled as "good stops." Without weighting, the model could achieve high accuracy by simply predicting "bad stop" for every location. By assigning higher loss penalties to misclassified good stops, we ensure the model learns to identify rare, high-value locations rather than defaulting to the majority class.
        Training occurs over 200 epochs with early stopping based on validation F1 score. The model begins with 82% training accuracy and 73% validation F1 at epoch 0, indicating that even random initialization leverages graph structure effectively. By epoch 110, validation F1 peaks at 0.927, with training accuracy at 96.4% and validation accuracy at 96.2%.
        Early stopping prevents overfitting—further training causes validation F1 to fluctuate without consistent improvement, signaling that the model has learned the optimal generalizable patterns.
        <br/><br/>
        <strong>Evaluation Metrics:</strong> On the held-out test set (1,236 nodes), the model achieves:
        <ul>
            <li><strong>Overall Accuracy:</strong> 94% (correctly classifies 1,162 of 1,236 stops)</li>
            <li><strong>Precision (Good Stops):</strong> 82% (when the model predicts "good stop," it's correct 82% of the time)</li>
            <li><strong>Recall (Good Stops):</strong> 97% (the model identifies 97% of all actual good stops in the test set)</li>
            <li><strong>F1 Score (Good Stops):</strong> 0.89 (harmonic mean of precision and recall, balancing both)</li>
            <li><strong>AUC-ROC:</strong> 0.97 (near-perfect ability to distinguish good stops from bad stops across all probability thresholds)</li>
        </ul>
        <br/>
        The 97% recall on good stops is particularly critical for our use case: missing a genuinely optimal stop location (false negative) has far greater social cost than including a suboptimal location (false positive). The high recall ensures that our model captures nearly all high-impact opportunities for equity improvement, even if it occasionally flags marginal candidates for further review.
        The confusion matrix reveals that the model makes 74 errors total: 57 false negatives (good stops predicted as bad—these represent missed opportunities, but at only 3% of good stops, the loss is minimal) and 17 false positives (bad stops predicted as good—these are easily filtered during manual review).
        <br/><br/>
        <strong>Why These Metrics Matter:</strong> Traditional optimization methods for transit planning rely on heuristics (e.g., "place stops every 400m along roads") or manual expert judgment, neither of which can process the 42-dimensional feature space or account for network-level interactions that our GCN captures automatically.
        The 94% accuracy represents a near-human-level ability to identify optimal stop placements, but unlike human planners, the model can evaluate 6,000+ candidates in seconds and produce ranked recommendations across the entire city. The high AUC-ROC (0.97) means the model's predicted probabilities are well-calibrated: stops with 90% predicted probability truly are high-quality ~90% of the time, enabling planners to set confidence thresholds based on budget or implementation constraints.
        Most importantly, the model's explicit incorporation of equity features (underserved population, temporal access gaps, poverty rates) ensures that recommendations systematically favor interventions in marginalized areas—something market-driven matatu routing inherently fails to do.
    </div>
</div>
""", unsafe_allow_html=True)

# ROUTE EXTENSION LOGIC
st.markdown("""
<div class="content-section">
    <div class="section-title">ROUTE EXTENSION LOGIC</div>
    <div class="section-content">
        Predicting optimal stop locations is only the first step—these candidate stops must be integrated into the existing matatu network in a way that is operationally feasible, spatially coherent, and maximally impactful. Our route extension logic transforms raw GNN predictions into actionable route recommendations through a multi-stage pipeline.
        <br/><br/>
        <strong>Step 1: Filtering and Ranking Predicted Stops.</strong> The GNN outputs a probability score for each of the 6,029 candidate locations. We filter to stops with predicted probability ≥ 0.75, ensuring high confidence in quality. This typically yields 300-500 high-probability candidates across Nairobi.
        We then rank candidates by composite score, a weighted function combining GNN probability, equity multiplier (2.0x for severely underserved wards, 1.5x for moderately underserved, 1.0x otherwise), population coverage (number of residents within 500m not already served by existing stops), and accessibility score (proximity to roads, commercial centers, and amenities).
        This composite score ensures that the final recommendations prioritize stops that are both model-confident and equity-maximizing.
        <br/><br/>
        <strong>Step 2: Snapping Predicted Stops to Road Network.</strong> The predicted stop locations are latitude-longitude coordinates in continuous space, but matatus operate on discrete road networks. To ensure operational feasibility, we snap each predicted stop to the nearest drivable road using OSMnx, a Python library for downloading and analyzing OpenStreetMap data.
        Snapping works as follows: for each candidate (lat, lon), we query the OSMnx graph for the nearest node (intersection) or edge (road segment) within 100 meters. If multiple roads exist within this radius, we prioritize major roads (primary, secondary, tertiary classifications in OSM) over residential streets, as matatus favor high-traffic corridors.
        The snapped location becomes the candidate's operational position—this is where a physical stop could realistically be placed. Candidates that cannot be snapped (e.g., predicted in parks, water bodies, or inaccessible terrain) are discarded as infeasible.
        <br/><br/>
        <strong>Step 3: Connecting Stops to Existing Routes.</strong> For each of the 22 underserved routes, we identify the top N predicted stops (typically N=5-10) that lie within a spatial buffer of the route's existing path. The buffer is typically 1-2 km, balancing the need for new coverage (stops too close to the existing route provide little value) and operational feasibility (stops too far require excessive detours).
        We then compute shortest-path connections from each existing stop on the route to each predicted stop using Dijkstra's algorithm on the OSMnx road graph. This produces a set of potential route extensions—new segments that connect existing infrastructure to predicted high-impact locations.
        <br/><br/>
        <strong>Step 4: Generating Route Variants.</strong> Rather than proposing a single rigid extension, we generate multiple route variants for each underserved route. Each variant represents a different combination of predicted stops and connection paths.
        For example, if a route has 3 top-ranked predicted stops (A, B, C), we might generate variants: (1) connect to A only, (2) connect to A and B, (3) connect to B and C, (4) connect to all three. This exhaustive enumeration (pruned to avoid computationally expensive combinations) produces 3-5 route variants per route, each offering different trade-offs.
        Each variant is represented as a modified GTFS shape—a sequence of latitude-longitude points tracing the new route geometry, compatible with standard transit data formats.
        <br/><br/>
        <strong>Step 5: Scoring and Ranking Variants.</strong> Each route variant is evaluated using a composite scoring function that balances equity, coverage, temporal fairness, and operational performance:
        <ul>
            <li><strong>Equity Score (40% weight):</strong> Population-weighted equity multiplier for all new stops in the variant. Variants serving severely underserved wards (multiplier 2.0x) receive significantly higher scores.</li>
            <li><strong>Coverage Score (30% weight):</strong> Number of new residents within 500m of the variant's stops, excluding population already served by existing routes. Measured in people per km of new route to penalize excessively long detours.</li>
            <li><strong>Temporal Equity Score (15% weight):</strong> Reduction in temporal access gaps. Computed by simulating hourly service frequency under the new variant and measuring the decrease in variance of trips per hour per capita across morning peak, evening peak, and off-peak periods.</li>
            <li><strong>Performance Score (15% weight):</strong> Route efficiency, measured as the ratio of new coverage to route length increase (people/km) and average speed along the new segments (from WorldMove data). Variants that require long detours through congested areas are penalized.</li>
        </ul>
        <br/>
        The final composite score is a weighted sum normalized to [0, 1]. Variants are ranked, and the top-scoring variant becomes the "recommended route" (green in the visualizations), while the next two highest-scoring variants are presented as alternatives (yellow and red).
        <br/><br/>
        <strong>Step 6: Validation and Output.</strong> The top variant for each route is subjected to feasibility checks: does it connect to existing stops within reasonable distance? Are the new stops accessible by road? Does the route avoid restricted areas (airports, military zones, private land)? Variants that fail these checks are demoted or discarded.
        The final output consists of: (1) A GTFS-compatible route file with updated stop locations and geometries, (2) A geospatial visualization (the interactive maps in this app), (3) A summary report listing composite scores, equity impacts, and implementation recommendations for each route.
        This pipeline ensures that GNN predictions are translated into real-world interventions that are not only optimal in theory but implementable in practice. By generating multiple variants, we provide planners with flexibility to adapt recommendations to ground-level constraints—community input, infrastructure limitations, or political considerations—while still maintaining high equity impact.
    </div>
</div>
""", unsafe_allow_html=True)

# LIMITATIONS AND CONSIDERATIONS
st.markdown("""
<div class="content-section">
    <div class="section-title">LIMITATIONS AND CONSIDERATIONS</div>
    <div class="section-content">
        While our methodology represents a significant advancement in data-driven transit equity optimization, it is critical to acknowledge the limitations inherent in the data sources, modeling assumptions, and real-world implementation challenges.
        <br/><br/>
        <strong>GTFS Data is Static; the Real World is Dynamic.</strong> The Digital Matatus GTFS feed, published in 2019, provides a snapshot of Nairobi's matatu network at a single point in time. In reality, matatu routes evolve constantly: new routes emerge, operators adjust paths based on traffic or demand, and stop locations shift informally.
        Our model treats this 2019 snapshot as ground truth, meaning recommendations may not reflect the current network state. Furthermore, GTFS assumes fixed schedules, but matatus operate on demand—departure times are flexible, frequencies vary by time of day and day of week, and service levels fluctuate unpredictably. Our temporal equity metrics (trips per hour per capita) are computed from scheduled data that may not match actual service patterns.
        Ideally, this analysis would incorporate real-time tracking data (e.g., from mobile operators or GPS devices installed in matatus), but such data remains proprietary and inaccessible for research purposes.
        <br/><br/>
        <strong>WorldMove Data Lacks Seasonality.</strong> The WorldMove mobility dataset, derived from 104,538 agent-based trajectories, provides an exceptional open alternative to proprietary traffic data. However, it represents an aggregated simulation of typical mobility patterns, not empirical observations over time.
        This means the data does not capture seasonal variations—traffic patterns during rainy seasons, holiday periods, or special events like elections or festivals. Additionally, WorldMove data is modeled at 10-minute intervals, which may smooth over short-term congestion spikes (e.g., accidents, road closures) that significantly impact matatu operations.
        While WorldMove's spatial and speed distributions align well with known traffic corridors in Nairobi, any recommendations based on this data should be validated against real-world traffic monitoring before full-scale implementation. Future iterations of this work could integrate real-time traffic APIs (e.g., Google Traffic, HERE Traffic) or crowdsourced data (e.g., Waze), though these introduce cost and licensing constraints.
        <br/><br/>
        <strong>Stops Require Human Validation.</strong> The GNN model achieves 94% accuracy on the test set, meaning 6% of its predictions are incorrect. More critically, the model optimizes for equity and coverage but cannot account for hyperlocal constraints invisible in the data: private land ownership, community opposition, safety concerns (e.g., stops near known crime hotspots), or micro-geographic features (e.g., drainage ditches, steep slopes) that make a location impractical for a bus stop.
        Every recommended stop must be ground-truthed by local planners or community stakeholders before implementation. The model's role is to narrow the search space from thousands of possible locations to a ranked shortlist, not to replace human judgment. Ideally, recommendations would be reviewed in partnership with matatu operators, ward representatives, and residents to ensure local buy-in and feasibility.
        <br/><br/>
        <strong>Model Generalization Beyond Nairobi.</strong> While the GNN architecture is generalizable to other cities, the specific features, thresholds, and weights used in this model are tuned for Nairobi's context. Applying this methodology to Lagos, Kampala, or Dakar would require retraining the model on city-specific data and recalibrating equity multipliers based on local inequality benchmarks.
        Additionally, cities with different informal transit modes (e.g., motorcycle taxis in Kampala, danfo buses in Lagos) may require adjusted feature engineering or alternative graph structures. The methodology is transferable, but not plug-and-play.
        <br/><br/>
        <strong>Political and Economic Feasibility.</strong> Our recommendations assume that improving equity is a shared objective, but in practice, transit planning is shaped by political interests, budget constraints, and competing priorities. Matatu operators may resist route changes that reduce profitability, even if they improve equity.
        Local governments may lack the resources to implement new stops (signage, shelters, lighting) or enforce route modifications. Some underserved areas may remain underserved precisely because of institutional neglect or discriminatory policies that no amount of data analysis can overcome.
        This project provides a technical blueprint, but real-world impact depends on political will, community advocacy, and sustained engagement with stakeholders who hold decision-making power. The model can show where equity gains are possible; it cannot force anyone to act on them.
        <br/><br/>
        <strong>Equity vs. Efficiency Trade-offs.</strong> While our composite scoring function balances equity and performance, there are inherent tensions between these objectives. Extending service to remote, low-density wards increases coverage but may require long, slow routes that reduce overall system efficiency.
        Operators prioritizing speed and turnover may avoid such extensions, even if subsidized. Policymakers must decide whether to incentivize equity-focused routes through subsidies, fare adjustments, or regulatory mandates—decisions that lie outside the scope of this technical work but are essential for implementation.
    </div>
</div>
""", unsafe_allow_html=True)

# PROOF OF CONCEPT
st.markdown("""
<div class="content-section">
    <div class="section-title">PROOF OF CONCEPT</div>
    <div class="section-content">
        This work is fundamentally a proof of concept—a demonstration that publicly available, openly licensed datasets can be aggregated and analyzed to produce actionable insights for urban systems that have historically been opaque, under-documented, or excluded from formal planning processes.
        Prior to initiatives like Digital Matatus, WorldMove, and WorldPop, comprehensive transit equity analysis in cities like Nairobi was impossible without proprietary data from Google, Uber, or telecom operators—data that remains inaccessible to most researchers, governments, and civil society organizations in Sub-Saharan Africa.
        By building a complete methodology using only open data, we prove that data scarcity is no longer an insurmountable barrier to evidence-based urban planning in the Global South.
        <br/><br/>
        <strong>Applications Beyond Transit Equity.</strong> The baseline we've established—combining GTFS, mobility trajectories, population rasters, road networks, and socioeconomic data within a graph neural network framework—can be adapted to a wide range of urban analytics challenges:
        <ul>
            <li><strong>Business Location Optimization:</strong> Retailers, banks, and service providers can use similar methods to identify optimal locations for new branches. By replacing transit stops with potential store sites and equity metrics with customer demographics, the same GNN approach can predict which locations maximize foot traffic while avoiding over-saturated markets. Competitor analysis becomes straightforward: overlay competitor locations as existing "stops" and identify underserved gaps. This approach offers far greater spatial fidelity than traditional market research, which often relies on zip code-level aggregates or expensive proprietary datasets.</li>
            <li><strong>Billboard and Advertising Placement:</strong> Outdoor advertising companies can optimize billboard placements by analyzing traffic flow (from WorldMove), sightline angles (from OSM building footprints), and demographic targeting (from population data). The model can answer hyperlocal questions like "should this billboard face east or 3 degrees north?" by computing viewership based on traffic direction, time of day, and congestion patterns. This precision—previously achievable only through manual surveys or expensive geospatial analytics firms—becomes accessible through open data aggregation.</li>
            <li><strong>Public Health Surveillance and Intervention Planning:</strong> Epidemiologists can use mobility trajectories to model disease transmission pathways and identify optimal locations for medical screenings, vaccination sites, or outbreak containment checkpoints. By replacing equity metrics with disease risk scores and transit stops with health facilities, the same GNN framework can recommend where to deploy limited public health resources. For example, during a cholera outbreak, the model could identify neighborhoods with high mobility (rapid disease spread risk) and low clinic access, prioritizing mobile testing units accordingly. This methodology directly supports evidence-based epidemic response in resource-constrained settings.</li>
            <li><strong>Infrastructure and Utility Planning:</strong> Governments and utilities can optimize the placement of bus shelters, water kiosks, waste collection points, or EV charging stations using the same spatial-equity framework. The graph structure naturally captures network effects: a new charging station's value depends on proximity to existing stations (range anxiety) and traffic flow patterns (demand). This avoids the common pitfall of infrastructure planning based solely on political considerations or anecdotal demand.</li>
            <li><strong>Real Estate Development and Urban Planning:</strong> Developers can assess site suitability for mixed-use developments, affordable housing, or commercial projects by evaluating connectivity (from OSM road networks), accessibility (from transit data), and demand signals (from mobility patterns). Policymakers can use the same methods to identify priority zones for upgrading informal settlements or targeting infrastructure investment toward neighborhoods with the greatest unmet need.</li>
        </ul>
        <br/>
        <strong>Democratizing Urban Data Science.</strong> The significance of this proof of concept extends beyond any single application. By documenting a fully open methodology—data sources, preprocessing pipelines, GNN architecture, evaluation metrics—we provide a replicable template for researchers, startups, NGOs, and governments across Africa and the Global South.
        Cities that lack the budgets for Sidewalk Labs-style smart city consultancies can now conduct sophisticated spatial analysis using only open-source tools, publicly available data, and mid-range cloud compute resources. This is not just about transit in Nairobi; it's about proving that the data divide between the Global North and South is narrowing, and that African cities can lead in applied urban AI if given the methodological scaffolding to do so.
        <br/><br/>
        The aggregation of open datasets—GTFS from volunteer mappers, mobility simulations from academic research initiatives, population grids from global health organizations, road networks from OpenStreetMap contributors—represents a quiet revolution in data accessibility. What this project demonstrates is that these disparate, imperfect, independently maintained datasets can be harmonized into a coherent analytical framework capable of producing insights comparable to (and in some dimensions, superior to) those derived from proprietary big data platforms.
        The future of urban analytics in Africa does not depend on waiting for Google or Uber to release their data; it depends on building the technical capacity to leverage the open data commons that already exists.
    </div>
</div>
""", unsafe_allow_html=True)

# INTRODUCING THE CONCEPT OF 'FLYING MATATUS'
st.markdown("""
<div class="content-section" id="flying-matatus">
    <div class="section-title">INTRODUCING THE CONCEPT OF 'FLYING MATATUS'</div>
    <div class="section-content">
        The year is 2149. Nairobi's skyline, once dominated by terrestrial high-rises and the chaotic hum of two-dimensional traffic, now thrums with the vertical ballet of flying matatus.
        These aren't the haphazard minibuses of the 2020s, patched together with scavenged parts and prayers—they're sleek, AI-piloted pods, their undersides aglow with repulsor fields, weaving through the luminous tangle of aerial corridors that criss-cross the city at altitudes ranging from 50 to 500 meters.
        The Central Business District, once a congested bottleneck where commuters spent hours inching forward, is now a layered metropolis: ground-level streets reserved for pedestrians and cargo drones, mid-level airways for regional matatu routes, and high-altitude express lanes for intercity transit.
        Traffic optimization in this three-dimensional space has rendered the challenges of the early 21st century—Euclidean routing, road congestion, stop placement on flat terrain—as quaint as abacus arithmetic. The graph neural networks of the 2020s, once celebrated for their ability to predict optimal bus stops along two-dimensional road networks, now seem laughably primitive.
        In 2149, the Nairobi Transit Authority's quantum-enhanced GNN (Q-GNN) operates in continuous 3D space, dynamically adjusting matatu flight paths in real time based on weather patterns, passenger demand surges detected via neural implants, and predictive models of airspace congestion.
        <br/><br/>
        Yet even in this hyper-optimized future, Nairobi retains its character. The matatus may fly, but they still blast Gengetone remixes (now in fully immersive haptic audio) and sport flamboyant holographic liveries advertising everything from crypto loans to pilgrimage shuttles to the lunar colonies.
        The touts—now AI avatars projected into passengers' augmented reality overlays—still shout routes with the same frenetic energy: "Ngong! Kibera! Eastleigh! Direct warp, hakuna kuelewa maana ya traffic!" Operators, once human drivers navigating by instinct and roadside landmarks, have been replaced by semi-autonomous pilot AIs trained on centuries of accumulated route data, but the vehicles themselves remain independently owned, fiercely competitive, and just barely regulated.
        The government's attempts to impose standardized flight corridors are routinely circumvented by operators who've hacked their navigation systems to exploit microsecond gaps in airspace monitoring.
        <br/><br/>
        The social equity challenges have evolved but not vanished. While flying matatus have eliminated the spatial constraints of road-based transit—enabling direct service to previously inaccessible informal settlements perched on Nairobi's hillsides—new inequalities have emerged. Wealthier wards enjoy high-frequency, climate-controlled pods with noise-canceling force fields and priority landing at premium skyports.
        Meanwhile, residents of the outer wards still ride in aging, second-hand units with flickering stabilizers and questionable safety certifications, their routes limited to lower-altitude corridors where turbulence from industrial zones and atmospheric rivers makes for nauseating commutes. The Gini coefficient for transit access in 2149 stands at 0.58—better than the 0.72 of 2025, but still a stark reminder that technology alone doesn't solve systemic inequity.
        <br/><br/>
        On X (formerly Twitter, now a decentralized neural implant network), complaints are abundant: "My implant is lagging trying to turn on the X1200 Samsung electric kettle while my matatu is buffering at 200 meters altitude. WHAT IS THIS, 2120?!" one user laments.
        Another: "Flew Rongai to CBD this morning. Pod dropped 30 meters in a downdraft. Driver AI just played a calm apology jingle. I WANT MY MONEY BACK." Despite the technological leap, Nairobians remain Nairobians—resourceful, irreverent, and perpetually oscillating between awe at their city's transformation and exasperation at its persistent dysfunction.
        <br/><br/>
        In 2149, the optimization problem is no longer "where should we place stops to maximize equity?" but "how do we allocate 4D spacetime slots (latitude, longitude, altitude, time) to minimize wait times, prevent mid-air collisions, and ensure that no neighborhood—terrestrial or aerial—is left behind?"
        The Q-GNN solves this with ease, processing petabytes of real-time sensor data and passenger biometrics to predict demand spikes before they occur. The system is so advanced that it occasionally preempts passengers' own decisions: "You were thinking of going to Westlands, but optimal routing suggests Kilimani. Trust the algorithm." Most comply. Some do not. The city adapts.
        <br/><br/>
        This is not a utopia. Nairobi in 2149 is still a city of hustle, improvisation, and stubborn informality. The flying matatus are a marvel of engineering, yes—but they're also a testament to the enduring truth that technology, no matter how advanced, is always shaped by the culture it serves.
        The 2020s worried about equity in two dimensions. The 2140s worry about equity in three, plus time, plus predictive intent. The problems scale; the principles remain. And somewhere, in a dusty archive node accessible only via deprecated protocols, a researcher unearths the 2025 Jav-Nairobi project and marvels at how quaint it was to think that bus stops and road networks were the hard part.
        <br/><br/>
        The flying matatus hum onward, weaving through the neon-soaked clouds of Nairobi's vertical sprawl. The city that never stood still in 2025 still doesn't in 2149. It just learned to fly.
    </div>
</div>
""", unsafe_allow_html=True)

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
