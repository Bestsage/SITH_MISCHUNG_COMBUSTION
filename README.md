# Rocket Motor Design Plotter

**PROMETHEUS v6.1** - A comprehensive rocket engine design and analysis tool with regenerative cooling simulation

## Overview

Rocket Motor Design Plotter is an advanced Python application for designing and analyzing liquid rocket engines. Built on top of **RocketCEA** and **NASA's CEA (Chemical Equilibrium with Applications)** program (https://cearun.grc.nasa.gov/), it combines accurate thermochemical calculations with detailed thermal analysis using the Bartz equation, providing engineers and enthusiasts with a powerful tool for rocket motor design optimization.

### What is NASA CEA?

NASA CEA (Chemical Equilibrium with Applications) is the industry-standard software developed by NASA Glenn Research Center for calculating chemical equilibrium compositions and properties of complex mixtures. This application leverages CEA's extensive propellant database and thermochemical models to provide accurate performance predictions for rocket engines.

## Key Features

### 🔥 Thermochemical Analysis (NASA CEA)
- **NASA CEA Integration**: Direct integration with NASA's Chemical Equilibrium with Applications program
- **RocketCEA Library**: Uses the RocketCEA Python wrapper to access CEA calculations
- **Multi-Propellant Support**: Access to NASA's extensive database of fuels and oxidizers (500+ propellants)
- **Performance Metrics**: ISP (specific impulse), C*, chamber temperature, throat temperature, and exit conditions
- **Real-time Calculations**: Instant performance updates as design parameters change
- **Equilibrium Chemistry**: Full chemical equilibrium calculations for accurate combustion modeling

### 🌡️ Thermal Analysis (Bartz Method)
- **Heat Flux Distribution**: Calculates heat flux profiles along the entire engine geometry
- **Regenerative Cooling**: Advanced regenerative cooling analysis with customizable coolant properties
- **Wall Temperature Modeling**: Predicts hot-side and cold-side wall temperatures with conduction effects
- **Coolant Flow Requirements**: Determines required coolant mass flow rates with safety margins
- **Temperature Safety Validation**: Checks coolant temperatures against boiling points with pressure corrections (Clausius-Clapeyron)

### 📐 Geometry Design
- **Bell Nozzle Design**: Automatic generation of optimized bell nozzle contours using Bézier curves
- **Rao Method**: Implements truncated ideal contour for maximum efficiency
- **Parametric Control**: Adjustable contraction ratio, expansion ratio, bell angles
- **L* Optimization**: Chamber length optimization based on L-star methodology
- **2D Visualization**: Real-time cross-section view of engine geometry

### 📊 Analysis Tools
- **Parametric Studies**: 2D and 3D plots showing performance vs. design parameters
- **Multi-Variable Analysis**: Explore relationships between O/F ratio, chamber pressure, expansion ratio, etc.
- **Interactive Graphs**: Matplotlib-based visualizations with zoom and export capabilities
- **Performance Optimization**: Find optimal operating conditions for your design

### 🗄️ Propellant Database Explorer
- **Searchable Database**: Browse all available fuels, oxidizers, and coolants
- **Detailed Properties**: View thermochemical data, densities, reference temperatures
- **Copy-to-Design**: Instantly use any propellant in your engine design
- **Custom Coolants**: Support for non-propellant coolants (water, glycols, thermal oils)

### 💾 Export Capabilities
- **DXF Export**: Generate CAD-compatible drawings of the chamber and the nozzle for manufacturing
- **Full Reports**: Comprehensive text reports with all calculated parameters

## Installation

### Prerequisites
- Python 3.10 (required)
  - **Note:** This application is tested and confirmed to work with Python 3.10
  - **Not compatible with Python 3.14** due to dependency constraints
- pip (Python package manager)

### Required Dependencies

```bash
pip install tkinter matplotlib numpy rocketcea
```

### Optional Dependencies

For DXF export functionality:
```bash
pip install ezdxf
```

### Dependency Details
- **tkinter**: GUI framework (usually included with Python)
- **matplotlib**: Plotting and visualization
- **numpy**: Numerical computations
- **rocketcea**: NASA CEA wrapper for propellant calculations - **This is the core dependency that provides access to NASA CEA**
- **ezdxf**: CAD file export (optional)

### About RocketCEA

RocketCEA is a Python wrapper for NASA's CEA (Chemical Equilibrium with Applications) FORTRAN code. It provides a Python interface to the same calculations available at https://cearun.grc.nasa.gov/. When you install RocketCEA, it includes the compiled CEA code and propellant thermochemical database.

**More information:**
- RocketCEA Documentation: http://rocketcea.readthedocs.io/
- NASA CEA Web Interface: https://cearun.grc.nasa.gov/
- NASA CEA Official Page: https://www1.grc.nasa.gov/research-and-engineering/ceaweb/

## Usage

### Starting the Application

```bash
python "moteur fusée design v6.py"
```

### Basic Workflow

1. **Configure Design Parameters** (Left Panel):
   - Enter engine name
   - Select oxidizer and fuel (CEA names)
   - Set chamber pressure and O/F ratio
   - Define mass flow rate
   - Adjust contraction and expansion ratios
   - Configure cooling parameters

2. **Run Analysis**:
   - Click "🔥 CALCULER TOUT (CEA + THERMIQUE)" button
   - View results in multiple tabs

3. **Explore Results**:
   - **Visualisation 2D**: Engine geometry cross-section
   - **Analyse Thermique**: Heat flux and temperature distributions
   - **Analyses Paramétriques**: Performance curves and surfaces
   - **Sortie NASA CEA**: Raw CEA output data
   - **Base de Données**: Browse propellant properties

### Example Configuration

**Simple Propane/LOX Engine:**
```
Engine Name: Test_Motor_001
Oxidizer: O2
Fuel: C3H8
Chamber Pressure: 12.0 bar
O/F Ratio: 2.8
Mass Flow: 0.5 kg/s
Contraction Ratio: 3.5
Exit Pressure: 1.013 bar
```

## Application Tabs

### 1. Visualisation 2D
Displays the engine geometry profile including:
- Combustion chamber
- Converging section
- Throat
- Diverging bell nozzle

### 2. Analyse Thermique (Bartz)
Shows thermal analysis results:
- Heat flux distribution along engine wall
- Gas temperature profile
- Wall temperature (hot-side and cold-side)
- Coolant requirements and validation
- Critical heating locations

### 3. Analyses Paramétriques
Interactive parametric studies:
- 2D curves: Single parameter sweeps
- 3D surfaces: Two-parameter analysis
- Customizable resolution and ranges
- Performance optimization studies

### 4. Sortie NASA CEA (Raw)
Complete NASA CEA output including:
- Species concentrations
- Transport properties (viscosity, thermal conductivity, Prandtl number)
- Thermodynamic properties (enthalpy, entropy, molecular weight)
- Detailed equilibrium data
- Same format as https://cearun.grc.nasa.gov/ output

### 5. Base de Données
Propellant database browser (NASA CEA Database):
- Search and filter capabilities
- Detailed property cards from NASA CEA thermochemical database
- CEA nomenclature reference (use exact CEA names)
- Quick copy to design parameters
- Access to 500+ propellants from NASA's database

## Design Parameters

### Propellant Parameters
- **Oxydant (CEA)**: Oxidizer name from CEA database (e.g., O2, N2O, H2O2)
- **Carburant (CEA)**: Fuel name from CEA database (e.g., C3H8, CH4, RP-1)
- **Ratio O/F (MR)**: Oxidizer-to-fuel mass ratio

### Chamber Parameters
- **Pression Chambre**: Chamber pressure (bar)
- **Débit Massique**: Total propellant mass flow rate (kg/s)
- **Contraction Ratio (Ac/At)**: Chamber area / throat area
- **L* (L-star)**: Characteristic chamber length (m)

### Nozzle Parameters
- **Pression Sortie Design**: Design exit pressure (bar)
- **Angle Entrée Bell**: Bell nozzle inlet angle (degrees)
- **Angle Sortie Bell**: Bell nozzle exit angle (degrees)
- **Pression Ambiante**: Ambient pressure for ISP calculation (bar)

### Cooling Parameters
- **Temp. Paroi Max**: Maximum allowable wall temperature (K)
- **Épaisseur Paroi**: Wall thickness (mm)
- **Conductivité Paroi**: Wall thermal conductivity (W/m-K)
- **Coolant**: Coolant selection (Auto uses fuel, or specify H2O, EG, etc.)
- **Débit Coolant**: Coolant mass flow (Auto or manual kg/s)
- **Coolant Pression**: Coolant circuit pressure (bar)
- **Coolant T entrée**: Coolant inlet temperature (K)
- **Coolant T sortie max**: Maximum coolant exit temperature (K)
- **Marge Sécurité Coolant**: Safety margin percentage (%)

## Technical Details

### Nozzle Contour Method
The application uses a **Rao-type bell nozzle** design with:
- Quadratic Bézier curve for smooth contour
- Optimized expansion for minimum length
- Customizable inlet and exit angles
- Throat radius calculation based on mass flow and C*

### Thermal Analysis Method
**Bartz Equation** for convective heat transfer:
```
hg = 0.026 / (Dt^0.2) × (μ^0.2 × Cp) / (Pr^0.6) × (Pc / C*)^0.8
```

With local corrections for:
- Diameter ratio effects
- Temperature-dependent gas properties
- Wall conduction through thickness
- Coolant-side heat transfer

### Coolant Analysis
- Pressure-dependent boiling point (Clausius-Clapeyron)
- Critical temperature limits
- Heat capacity considerations
- Mass flow requirements with safety margins
- Validation against available fuel flow

## Output Parameters

### Performance
- **ISP Sol**: Sea-level specific impulse (s)
- **ISP Vide**: Vacuum specific impulse (s)
- **Poussée**: Thrust force (kN)
- **C***: Characteristic velocity (m/s)

### Thermal
- **Flux Max**: Maximum heat flux (MW/m²)
- **Flux Moyen**: Average heat flux (MW/m²)
- **Puissance Therm**: Total thermal power (kW)
- **hg au Col**: Heat transfer coefficient at throat (W/m²-K)

### Geometry
- **Ø Col**: Throat diameter (mm)
- **Ø Sortie**: Exit diameter (mm)
- **Ø Chambre**: Chamber diameter (mm)
- **L Chambre**: Chamber length (mm)
- **L Bell**: Bell nozzle length (mm)
- **ε (Epsilon)**: Expansion ratio (Ae/At)

### Temperatures
- **T Gaz Chambre**: Chamber gas temperature (K)
- **T Gaz Col**: Throat gas temperature (K)
- **T Paroi Hot**: Hot-side wall temperature (K)
- **T Paroi Cold**: Cold-side wall temperature (K)

## Common Propellants

### Oxidizers
- **O2 / LOX**: Liquid oxygen (most common)
- **N2O**: Nitrous oxide (self-pressurizing)
- **H2O2**: Hydrogen peroxide (90%+)
- **N2O4**: Nitrogen tetroxide (hypergolic)

### Fuels
- **C3H8**: Propane (easy to handle)
- **CH4 / LCH4_NASA**: Methane (high performance)
- **RP-1 / RP1**: Rocket-grade kerosene (dense, storable)
- **C2H5OH**: Ethanol (green propellant)
- **LH2**: Liquid hydrogen (highest ISP)
- **MMH / UDMH**: Hypergolic fuels

### Coolants
- **Auto**: Uses fuel in regenerative cooling
- **H2O / Water**: Water cooling (external circuit)
- **EG**: Ethylene glycol
- **LN2**: Liquid nitrogen (cryogenic)

## Troubleshooting

### Common Issues

**"Ergols inconnus" (Unknown propellants)**
- Check CEA naming: Use database tab to find correct names
- Examples: Use "O2" not "LOX", "C3H8" not "Propane"

**"Refroidissement insuffisant" (Insufficient cooling)**
- Increase coolant mass flow rate
- Lower coolant exit temperature
- Increase wall thickness
- Use better conductor material (higher k)
- Increase coolant inlet pressure

**"T entrée >= T ébullition" (Inlet temp too high)**
- Reduce coolant inlet temperature below boiling point
- Increase coolant circuit pressure
- Select different coolant

**Zero C* or ISP**
- Check chamber pressure > exit pressure
- Verify O/F ratio is reasonable (typically 1.5-4.0)
- Ensure valid propellant combination

## Contributing

Contributions are welcome! Areas for improvement:
- Additional nozzle contour methods (MOC, TIC)
- Film cooling analysis
- Injector design tools
- Combustion stability analysis
- More detailed material property databases

## License

This project is open source. Please check for specific license terms.

## Acknowledgments

- **NASA Glenn Research Center**: For developing the CEA (Chemical Equilibrium with Applications) program
- **NASA CEA Web**: https://cearun.grc.nasa.gov/ - Web interface for CEA calculations
- **RocketCEA**: Python wrapper for NASA CEA by Charlie Taylor (https://github.com/sonofeft/RocketCEA)
- **Bartz Equation**: Heat transfer correlation for rocket engines
- **Rao Method**: Optimum thrust chamber contour design

### CEA Data Source

All thermochemical data and performance calculations are powered by NASA's CEA program. The propellant properties, equilibrium chemistry, and transport properties come directly from NASA's validated thermochemical database, ensuring accurate and reliable results for rocket engine design.

## References

1. **NASA CEA Website**: https://cearun.grc.nasa.gov/
2. **CEA Documentation**: Gordon, S. and McBride, B.J., "Computer Program for Calculation of Complex Chemical Equilibrium Compositions and Applications", NASA Reference Publication 1311, 1994
3. **RocketCEA Documentation**: http://rocketcea.readthedocs.io/

---

**Version**: PROMETHEUS v6.1 (Regen Cooling)  
**Last Updated**: 2024  
**Author**: Bestsage
