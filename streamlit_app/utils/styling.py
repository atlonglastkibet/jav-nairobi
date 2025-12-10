"""
CSS styling and theme configuration for dark mode.
"""

def get_custom_css():
    """Return custom CSS for dark theme matching pydeck's charcoal."""
    return """
    <style>
    :root {
        --bg-primary: #0e1117;
        --bg-secondary: #161a1e;
        --bg-charcoal: #0e0e0e;
        --text-primary: #ffffff;
        --text-secondary: #b8bcc8;
        --accent-red: #E74C3C;
        --accent-orange: #E67E22;
        --accent-yellow: #F1C40F;
        --accent-green: #46cc71;
    }

    /* Main app container - match pydeck deep charcoal */
    .main {
        background-color: var(--bg-charcoal) !important;
    }

    /* Match streamlit's main background to pydeck */
    .stApp {
        background-color: var(--bg-charcoal) !important;
    }

    /* Block container */
    .block-container {
        background-color: var(--bg-charcoal) !important;
    }

    /* Sidebar to match */
    [data-testid="stSidebar"] {
        background-color: var(--bg-charcoal) !important;
    }

    [data-testid="stSidebarNav"] {
        background-color: var(--bg-charcoal) !important;
    }

    [data-testid="stSidebarContent"] {
        background-color: var(--bg-charcoal) !important;
    }

    /* Header area */
    header[data-testid="stHeader"] {
        background-color: var(--bg-charcoal) !important;
    }

    /* Main content area */
    section[data-testid="stMain"] {
        background-color: var(--bg-charcoal) !important;
    }

    /* All divs inside main */
    section[data-testid="stMain"] > div {
        background-color: var(--bg-charcoal) !important;
    }

    /* Metrics panel styling */
    .metrics-container {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(14, 17, 23, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        z-index: 999;
        display: flex;
        gap: 30px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
    }

    .metric-item {
        text-align: center;
        min-width: 120px;
    }

    .metric-number {
        font-size: 32px;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1.2;
    }

    .metric-label {
        font-size: 12px;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 5px;
    }

    .metric-subtext {
        font-size: 10px;
        color: var(--text-secondary);
        margin-top: 5px;
        font-style: italic;
    }

    /* Variant cards */
    .variant-card {
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }

    .variant-card:hover {
        border-color: var(--accent-green);
        box-shadow: 0 4px 12px rgba(52, 168, 83, 0.3);
    }

    .variant-card.selected {
        border-color: var(--accent-green);
        background: rgba(52, 168, 83, 0.1);
    }

    .variant-header {
        font-size: 16px;
        font-weight: 600;
        color: var(--text-primary);
        margin-bottom: 10px;
    }

    .variant-stat {
        display: flex;
        justify-content: space-between;
        padding: 6px 0;
        border-bottom: 1px solid rgba(255,255,255,0.1);
    }

    .variant-stat:last-child {
        border-bottom: none;
    }

    .variant-stat-label {
        color: var(--text-secondary);
        font-size: 13px;
    }

    .variant-stat-value {
        color: var(--text-primary);
        font-weight: 600;
        font-size: 13px;
    }

    /* Legend */
    .legend-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(14, 17, 23, 0.85);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        padding: 15px;
        z-index: 999;
        min-width: 200px;
    }

    .legend-title {
        font-weight: 600;
        margin-bottom: 10px;
        color: var(--text-primary);
        font-size: 14px;
    }

    .legend-item {
        display: flex;
        align-items: center;
        margin: 8px 0;
        font-size: 12px;
        color: var(--text-primary);
    }

    .legend-color {
        width: 28px;
        height: 3px;
        margin-right: 10px;
        border-radius: 2px;
    }

    /* Buttons */
    .stButton > button {
        background-color: var(--accent-green);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 10px 20px;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    .stButton > button:hover {
        background-color: #3ba868;
        box-shadow: 0 4px 12px rgba(52, 168, 83, 0.4);
    }

    /* Sidebar */
    .css-1d391kg {
        background-color: var(--bg-secondary);
    }

    /* Headers */
    h1, h2, h3 {
        color: var(--text-primary);
    }

    /* Streamlit elements */
    .stSelectbox label {
        color: var(--text-primary);
        font-weight: 500;
    }

    /* Remove default streamlit padding for full-screen maps */
    .fullscreen-map {
        margin: -1rem;
        margin-top: -5rem;
    }

    /* About page sections */
    .about-section {
        background: var(--bg-secondary);
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 20px;
    }

    .about-section h2 {
        color: var(--accent-green);
        margin-bottom: 15px;
    }

    .tech-badge {
        display: inline-block;
        background: rgba(52, 168, 83, 0.2);
        color: var(--accent-green);
        padding: 6px 12px;
        border-radius: 6px;
        margin: 5px;
        font-size: 13px;
        font-weight: 500;
    }

    /* Comparison table */
    .comparison-table {
        width: 100%;
        border-collapse: collapse;
        margin: 20px 0;
    }

    .comparison-table th {
        background: var(--bg-secondary);
        color: var(--accent-green);
        padding: 12px;
        text-align: left;
        border-bottom: 2px solid var(--accent-green);
    }

    .comparison-table td {
        padding: 12px;
        border-bottom: 1px solid rgba(255,255,255,0.1);
        color: var(--text-primary);
    }

    .comparison-table tr:hover {
        background: rgba(52, 168, 83, 0.05);
    }
    </style>
    """
