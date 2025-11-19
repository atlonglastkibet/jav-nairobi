# WorldMove Data Integration: Population and Mobility Patterns for Nairobi

## Overview

This analysis processes and integrates population data from the WorldMove dataset, a global synthetic mobility platform covering over 1,600 cities. The notebook focuses on extracting and calibrating population estimates specifically for Nairobi's metropolitan area to support transport planning analysis.

## About WorldMove

WorldMove is a comprehensive synthetic mobility dataset developed by Tsinghua University's Future Intelligence Lab. It uses advanced diffusion-based generative models to create realistic urban mobility patterns from publicly available data sources. The dataset provides:

- Grid-based population distributions at 1km resolution
- Synthetic but statistically realistic mobility patterns
- Global coverage spanning 179 countries
- Integration-ready format for transport modeling

**Key Resources**
- Official Portal: WorldMove Dataset (FIB Lab)
- Research Foundation: ArXiv paper 2504.10506
- GitHub Repository: Comprehensive documentation and tools

## Data Components

### Grid Cell Coordinate System

**Structure**: 1,440 grid cells covering Nairobi metropolitan area
- Resolution: 1km x 1km cells
- Coordinate System: WGS84 (EPSG:4326)
- Format: JSON file with cell ID to longitude/latitude mapping
- Coverage: Complete Nairobi metropolitan boundary plus buffer areas

### Population Distribution Data

**Raw Population Grid**
- Format: NumPy array (30 x 48 cells)
- Total agents: 20.8 million synthetic individuals
- Distribution: Variable density across urban, suburban, and peri-urban areas
- Range: 23 to 280,940 individuals per cell

**Population Calibration Process**

The raw synthetic population requires calibration to match known demographic data:

1. **Boundary Definition**: Geographic masking using Nairobi administrative boundaries
2. **Point-in-Polygon Testing**: Automated classification of cells as inside/outside city limits
3. **Scaling Calculation**: Normalization to match Kenya National Bureau of Statistics estimates
4. **Final Calibration**: Adjustment from 20.8M synthetic agents to 4.8M actual population

**Calibration Formula**
```
Corrected Population = Raw Population ÷ Normalization Factor
Normalization Factor = Raw Inside Population ÷ Known Nairobi Population
```

Where:
- Raw Inside Population: 15.89 million (synthetic)
- Known Nairobi Population: 4.8 million (KNBS estimate)
- Normalization Factor: 3.31

## Administrative Integration

### Ward-Level Aggregation

**Kenya Wards Dataset**
- Source: Administrative boundaries shapefile
- Coverage: All 85 wards within Nairobi County
- Integration: Spatial join between population grid and ward polygons

**Population Allocation Process**
1. Spatial overlay of 1km grid cells with ward boundaries
2. Cell-to-ward assignment using geometric centroids
3. Population summation by ward administrative unit
4. Quality validation against census estimates

### Missing Data Handling

**Linear Regression Imputation**
For wards with zero population coverage (due to spatial join gaps):
- Predictor: 2009 Census population counts
- Target: Corrected WorldMove population estimates
- Model: Simple linear regression assuming consistent growth patterns
- Application: Imputation for 11 wards with missing coverage

## Results and Outputs

### Population Summary Statistics

**Corrected Metropolitan Population**
- Total: 6.27 million (including buffer areas)
- Inside Nairobi: 4.80 million (calibrated to KNBS)
- Outside city limits: 1.47 million (peri-urban areas)

**Spatial Distribution**
- Cells inside Nairobi: 505 out of 1,440 total grid cells
- Average density: Variable from sparse suburban to dense urban core
- Peak density areas: Central business district and major residential zones

### Interactive Visualization

**Population Density Map**
The analysis produces an interactive web map showing:
- Individual grid cells colored by population density
- Nairobi administrative boundary overlay
- Population statistics on hover and click
- Multiple basemap options for context

**Key Features**
- Color gradient from light (low density) to dark (high density)
- Popup information including cell ID, coordinates, and population
- Boundary highlighting for inside/outside classification
- Scalable visualization suitable for web deployment

### Data Products

**Processed Datasets**
1. **coord_df_corrected.csv**: Grid cells with calibrated population
2. **wards_nbo.csv**: Nairobi wards with geographic boundaries
3. **coord_with_wards.csv**: Grid cells assigned to ward areas
4. **wards_nbo_pop_imputed.csv**: Complete ward population estimates

## Quality Assurance

### Validation Checks

**Geographic Accuracy**
- Coordinate system consistency verification
- Boundary polygon topology validation
- Spatial join completeness assessment

**Population Reasonableness**
- Comparison with official census estimates
- Cross-validation with satellite-derived population data
- Sanity checks against known urban development patterns

**Data Completeness**
- Missing value identification and treatment
- Coverage gap analysis and resolution
- Administrative boundary alignment verification

## Applications

### Urban Planning Support
- Population-based service demand estimation
- Infrastructure capacity planning
- Demographic analysis for policy development

### Transport Planning Integration
- Stop location population catchment analysis
- Route demand forecasting
- Accessibility equity assessment

### Spatial Analysis Foundation
- Base layer for subsequent geographic analysis
- Integration with transit accessibility studies
- Foundation for equity and demographic research

## Technical Implementation

### Processing Pipeline
- Automated boundary processing using geometric operations
- Vectorized population calculations for performance
- Robust error handling for edge cases

### Spatial Analysis Tools
- GeoPandas for geographic data manipulation
- Folium for interactive web mapping
- NumPy for efficient numerical operations

### Performance Optimization
- Memory-efficient processing of large grid datasets
- Streamlined spatial operations
- Scalable visualization techniques

## Next Steps

This population foundation enables several downstream analyses:

1. **Equity Analysis**: Combining population with transport accessibility metrics
2. **Demand Modeling**: Using population density for service planning
3. **Coverage Assessment**: Evaluating transport provision relative to population
4. **Spatial Analysis**: Integration with road networks and other urban features

The calibrated population dataset serves as a crucial input for comprehensive transport equity and accessibility analysis throughout Nairobi.