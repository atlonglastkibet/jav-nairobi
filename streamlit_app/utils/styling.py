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

    /* Map caption styling */
    .map-caption {
        font-size: 13px;
        color: var(--text-secondary);
        text-align: center;
        margin: 15px auto 30px;
        max-width: 800px;
        line-height: 1.6;
    }

    .map-caption a {
        color: var(--accent-green);
        text-decoration: none;
    }

    .map-caption a:hover {
        text-decoration: underline;
    }

    /* Inline metrics styling */
    .metrics-inline {
        display: flex;
        justify-content: center;
        gap: 60px;
        margin: 30px 0 50px;
        flex-wrap: wrap;
    }

    .metric-inline-item {
        text-align: center;
    }

    .metric-inline-number {
        font-size: 36px;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1;
    }

    .metric-inline-label {
        font-size: 11px;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 8px;
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

    /* Inline legend */
    .legend-inline {
        display: flex;
        justify-content: center;
        gap: 25px;
        margin: 15px 0;
        flex-wrap: wrap;
    }

    .legend-inline-item {
        display: flex;
        align-items: center;
        font-size: 12px;
        color: var(--text-secondary);
    }

    .legend-inline-color {
        width: 30px;
        height: 3px;
        margin-right: 8px;
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

    /* Content sections */
    .content-section {
        max-width: 100%;
        margin: 50px auto 40px;
        padding: 0 20px;
        scroll-margin-top: 80px;
    }

    .section-title {
        font-size: 24px;
        font-weight: 700;
        color: var(--accent-red);
        margin-bottom: 20px;
        letter-spacing: 0.5px;
    }

    .section-content {
        font-size: 15px;
        color: var(--text-primary);
        line-height: 1.8;
        text-align: justify;
    }

    .section-content a {
        color: var(--accent-green);
        text-decoration: none;
    }

    .section-content a:hover {
        text-decoration: underline;
    }

    /* Footer */
    .app-footer {
        text-align: center;
        margin: 60px 0 30px;
        padding: 30px 20px;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }

    .footer-text {
        font-size: 13px;
        color: var(--text-secondary);
        line-height: 1.6;
    }

    .footer-text a {
        color: var(--accent-green);
        text-decoration: none;
    }

    .footer-text a:hover {
        text-decoration: underline;
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
