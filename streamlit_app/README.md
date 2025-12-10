# Jav-Nairobi Streamlit App

AI-Powered Transit Equity Optimization for Nairobi's Matatu Network

## Overview

This Streamlit application visualizes Graph Neural Network (GNN) powered route optimization recommendations to improve transit equity in Nairobi's matatu network.

## Features

### 🏠 Home Page
- Animated network visualization with Pydeck
- Interactive route arcs radiating from CBD
- Color-coded equity tiers
- Key metrics dashboard

### ℹ️ About Page
- Project methodology and approach
- GNN vs Traditional ML comparison
- Impact metrics and results
- Technology stack overview

### 🗺️ Route Explorer
- **NEW: Folium-based interactive visualization**
- Click route lines to view metrics in floating panel
- Road-snapped routes using OSMnx
- Toggle variants on/off with layer control
- Original vs recommended routes
- GNN scoring and metrics
- Detailed variant analysis

## Installation

### Option 1: Using Virtual Environment (Recommended)

```bash
# Navigate to the streamlit app directory
cd streamlit_app

# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

### Option 2: System-Wide Installation

If you prefer system-wide installation (not recommended on Arch/Manjaro due to PEP 668):

```bash
cd streamlit_app
pip install -r requirements.txt
```

**Note for Arch/Manjaro users**: System Python is externally managed. Use a virtual environment or install via `pacman` where possible.

### Data Files

Ensure data files are in place (relative to project root):
- `data/raw/digitalmatatu/GTFS_FEED_2019.zip`
- `data/training_output/route_recommendations_comprehensive.csv`
- `data/training_output/top_candidates.csv`
- `data/training_output/ward_summary.csv`

## Usage

Run the app locally:

```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## Project Structure

```
streamlit_app/
├── app.py                    # Main entry point
├── pages/
│   ├── 1_🏠_Home.py          # Home page with animation
│   ├── 2_ℹ️_About.py         # About page
│   └── 3_🗺️_Route_Explorer.py # Route comparison page
├── utils/
│   ├── data_loader.py        # Data loading utilities
│   └── styling.py            # CSS and theme configs
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## Data Sources

1. **Digital Matatus GTFS Feed** (2019): 135+ routes, 4,284 stops
2. **WorldMove Mobility Data**: 104,000+ trajectories
3. **OpenStreetMap**: Road network via OSMnx
4. **Kenya Census 2019**: Population density by ward

## Key Technologies

- **Streamlit** >= 1.28.0 - Web framework
- **Folium** >= 0.14.0 - Interactive mapping (Route Explorer)
- **streamlit-folium** >= 0.15.0 - Folium integration for Streamlit
- **OSMnx** >= 1.3.0 - Road network data and routing
- **Pydeck** >= 0.8.0 - 3D visualizations (Home page)
- **PyTorch Geometric** - GNN framework (used in model training)
- **gtfs-kit** - GTFS data processing
- **GeoPandas** - Geospatial analysis

## Model Performance

- **Accuracy**: 94%
- **Recall**: 96%
- **F1 Score**: 94%
- **Population Impact**: 1.8M newly served residents
- **Equity Improvement**: Gini coefficient 0.72 → 0.61

## Development

### Running in Development Mode

```bash
streamlit run app.py --server.runOnSave true
```

### Customization

- **Colors**: Edit `utils/styling.py` to change color scheme
- **Metrics**: Modify `utils/data_loader.py` to adjust calculations
- **Layout**: Page files in `pages/` directory

## Deployment

### Streamlit Cloud

1. Push code to GitHub repository
2. Connect repository to Streamlit Cloud
3. Deploy with `app.py` as main file

### Other Platforms

The app can be deployed to any platform supporting Python web apps:
- Heroku
- Google Cloud Run
- AWS Elastic Beanstalk

## Author

**David Kibet**
MSc Epidemiology & Data Science

## License

This project is part of academic research on urban transit equity.

## Acknowledgments

- Digital Matatus Project (GTFS data)
- WorldMove (Mobility data)
- OpenStreetMap contributors
