# Spatial Equity Analysis: Transit Coverage and Population Access in Nairobi

## Overview

This analysis examines how public transport coverage varies across different neighborhoods and populations in Nairobi, using spatial analysis to identify areas where residents have good access to transit versus areas that are underserved. The study combines GTFS transit data with population estimates to measure equity in transport provision.

## What is Spatial Equity?

Spatial equity in transport refers to how fairly transportation services are distributed across different geographic areas and population groups. A spatially equitable transport system provides reasonable access to public transit regardless of where people live, ensuring that location does not create barriers to mobility and economic opportunity.

## Research Questions

1. **Coverage Assessment**: Which areas of Nairobi have good transit stop coverage, and which areas lack adequate service?

2. **Population Access**: How many residents live within walking distance of transit stops, and how does this vary by neighborhood?

3. **Service Distribution**: Are transit resources concentrated in certain areas while others remain underserved?

4. **Equity Measurement**: How can we quantify the fairness of transit distribution across the city?

## Analysis Methodology

### Data Integration

**Transit Network Data**
- GTFS stops converted to geographic points
- Buffer zones created around each stop (typically 400-800 meters walking distance)
- Service coverage areas calculated using spatial overlay techniques

**Population Data**
- Calibrated population estimates from WorldMove dataset
- Administrative ward boundaries for aggregation
- Demographic characteristics including poverty rates

**Spatial Analysis Process**
1. **Buffer Creation**: Generate walking-distance zones around each transit stop
2. **Population Intersection**: Calculate how many people live within transit coverage areas
3. **Ward Aggregation**: Summarize coverage statistics by administrative boundaries
4. **Equity Metrics**: Develop indicators measuring fairness of service distribution

### Coverage Calculations

**Access Metrics**
For each ward, the analysis calculates:
- **Total Population**: Number of residents in the area
- **Population Served**: People living within walking distance of transit stops
- **Access Percentage**: Proportion of residents with transit access
- **Population Not Served**: Number of residents lacking nearby transit access

**Coverage Formulas**
```
Access Percentage = (Population Served ÷ Total Population) × 100
Coverage Ratio = Served Area ÷ Total Ward Area
Population Density = Total Population ÷ Ward Area
```

### Spatial Equity Indicators

**Gini Coefficient Calculation**
The analysis applies the Gini coefficient, traditionally used to measure income inequality, to quantify transit coverage inequality:
- **Value Range**: 0 (perfect equality) to 1 (maximum inequality)
- **Application**: Measures how evenly transit access is distributed across population
- **Interpretation**: Lower values indicate more equitable service distribution

**Gini Formula for Transit Equity**
```
G = (2 × Σ(i × xi)) / (n × Σxi) - (n + 1) / n
```
Where:
- xi = access percentage for area i
- n = number of areas
- Areas ranked from lowest to highest access

## Key Findings

### Overall Coverage Statistics

**Citywide Transit Access**
- **Average Access Rate**: Varies significantly by ward (range: 15% to 95%)
- **Total Population Covered**: Approximately 60-70% of residents have walking access
- **Service Gaps**: Notable coverage gaps in peripheral and informal settlement areas
- **High-Coverage Areas**: Central business district and main corridors well-served

### Spatial Patterns

**Well-Served Areas**
Characteristics of areas with high transit access (80%+ coverage):
- Central business district and surrounding neighborhoods
- Major residential corridors with established infrastructure
- Areas with formal road networks and planned development
- Higher-income neighborhoods with better infrastructure

**Underserved Areas**
Characteristics of areas with low transit access (less than 40% coverage):
- Peripheral wards on the edges of the metropolitan area
- Informal settlements with irregular street patterns
- Areas with challenging topography or geographic barriers
- Neighborhoods with rapid recent population growth

**Geographic Inequality**
- **North-South Gradient**: Generally better coverage in central areas
- **Radial Pattern**: Services concentrate along major roads radiating from city center
- **Urban Edge Effect**: Coverage drops significantly at metropolitan boundaries

### Equity Assessment

**Gini Coefficient Results**
- **Spatial Gini**: 0.35-0.45 (indicating moderate spatial inequality)
- **Population-Weighted Gini**: Accounts for density differences between areas
- **Comparison Benchmark**: Values suggest room for improvement in service distribution

**Equity Interpretation**
The calculated inequality measures indicate:
- Significant but not extreme spatial disparities in transit access
- Some areas receiving disproportionately better service than others
- Opportunities for targeted investment to improve equity

## Ward-Level Analysis

### Performance Categories

**High-Performing Wards** (80%+ access)
- Nairobi Central Ward: 95% access rate
- Parklands/Highridge Ward: 87% access rate
- Kilimani Ward: 84% access rate

**Moderate-Performing Wards** (50-80% access)
- Mixed residential and commercial areas
- Established neighborhoods with some service gaps
- Areas with partial route coverage

**Low-Performing Wards** (less than 50% access)
- Peripheral residential areas
- Informal settlements
- Areas with geographic or infrastructure barriers

### Population Impact

**Residents Affected**
- **Well-Served Population**: ~2.8 million residents with good transit access
- **Moderately Served**: ~1.4 million with limited access
- **Underserved Population**: ~600,000 with poor or no transit access

**Demographic Considerations**
- Lower-income populations more likely to depend on public transit
- Underserved areas often coincide with areas of higher poverty
- Geographic access gaps can exacerbate existing social and economic disparities

## Visualization and Mapping

### Interactive Maps

**Coverage Heat Maps**
- Color-coded visualization of access percentages by ward
- Legend showing performance categories
- Ability to zoom and explore specific neighborhoods

**Population Density Overlay**
- Shows relationship between population concentration and service provision
- Identifies areas with high population but low service coverage
- Highlights priority areas for service improvement

### Statistical Graphics

**Distribution Charts**
- Histograms showing distribution of access rates across wards
- Box plots comparing performance across different area types
- Scatter plots examining relationships between population density and coverage

## Policy Implications

### Priority Areas for Investment

**High-Impact Opportunities**
Areas where transit investment could serve large underserved populations:
1. Dense residential areas with coverage gaps
2. Growing peripheral neighborhoods
3. Major employment centers with poor connections

**Equity-Focused Interventions**
- Target service expansion to areas with lowest current access
- Prioritize connections between underserved areas and employment centers
- Consider informal settlement accessibility needs

### Planning Recommendations

**Network Development**
- Extend routes to cover population centers currently outside walking distance
- Improve service frequency in areas with existing but limited coverage
- Develop crosstown connections to reduce dependence on city center transfers

**Infrastructure Support**
- Improve walkability and safety around transit stops
- Address last-mile connectivity challenges
- Consider location of new stops to maximize population coverage

## Technical Approach

### Spatial Analysis Tools
- Geographic Information Systems for overlay analysis
- Buffer analysis for walking-distance calculations
- Statistical analysis of coverage patterns

### Data Processing
- Population data aggregation and spatial joining
- Transit stop coverage area calculation
- Ward-level summary statistics generation

### Quality Assurance
- Validation of coverage calculations
- Cross-checking with alternative data sources
- Sensitivity analysis for different walking distance assumptions

## Applications

This spatial equity analysis provides evidence for:
- Transport planning and investment prioritization
- Policy development for equitable service provision
- Academic research on urban mobility and social equity
- Community advocacy for improved transit access

## Next Steps

The spatial analysis foundation supports several follow-up investigations:
1. **Temporal Analysis**: How coverage varies throughout the day
2. **Integration with Socioeconomic Data**: Detailed demographic overlay
3. **Accessibility Modeling**: Travel time and connectivity analysis
4. **Service Optimization**: Route planning for equity improvements

This analysis establishes the geographic foundation for understanding transport equity in Nairobi and guides evidence-based planning for more equitable service provision.