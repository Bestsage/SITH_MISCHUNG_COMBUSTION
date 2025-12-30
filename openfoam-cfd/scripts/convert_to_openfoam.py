#!/usr/bin/env python3
"""
Convert mesh to OpenFOAM format (blockMesh compatible)
Used as fallback when Loci-STREAM is not available
"""

import numpy as np
import json
import sys
from pathlib import Path


def create_openfoam_case(mesh_file: str, output_dir: str, params: dict = None):
    """
    Create a complete OpenFOAM case directory structure
    """
    mesh_path = Path(mesh_file)
    case_dir = Path(output_dir)
    
    # Load mesh
    with open(mesh_path, 'r') as f:
        mesh = json.load(f)
    
    # Create directory structure
    (case_dir / 'constant' / 'polyMesh').mkdir(parents=True, exist_ok=True)
    (case_dir / 'system').mkdir(parents=True, exist_ok=True)
    (case_dir / '0').mkdir(parents=True, exist_ok=True)
    
    # Extract mesh info
    x = np.array(mesh['x'])
    r = np.array(mesh['r'])
    nx = mesh['nx']
    ny = mesh['ny']
    
    # For 2D axisymmetric, we create a wedge mesh
    # OpenFOAM uses a 5-degree wedge for axisymmetric
    wedge_angle = 5.0 * np.pi / 180.0
    
    # Write blockMeshDict
    write_block_mesh_dict(case_dir, x, r, nx, ny, wedge_angle)
    
    # Write control files
    write_control_dict(case_dir, params)
    write_fv_schemes(case_dir)
    write_fv_solution(case_dir)
    write_thermophysical_properties(case_dir, params)
    write_turbulence_properties(case_dir)
    
    # Write initial conditions
    write_initial_conditions(case_dir, params)
    
    print(f"OpenFOAM case created: {case_dir}")


def write_block_mesh_dict(case_dir: Path, x: np.ndarray, r: np.ndarray, 
                          nx: int, ny: int, wedge_angle: float):
    """Write blockMeshDict for 2D axisymmetric wedge mesh"""
    
    # Get domain bounds
    x_min, x_max = x.min(), x.max()
    r_max = r.max()
    
    # Create wedge vertices
    # For a proper nozzle, we need to define the geometry
    # Simplified: rectangular domain that will be meshed
    
    content = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}

convertToMeters 1;

vertices
(
    // Back face (z < 0)
    ({x_min} 0 0)                                          // 0
    ({x_max} 0 0)                                          // 1
    ({x_max} {r_max * np.cos(wedge_angle)} {-r_max * np.sin(wedge_angle)})  // 2
    ({x_min} {r_max * np.cos(wedge_angle)} {-r_max * np.sin(wedge_angle)})  // 3
    
    // Front face (z > 0)
    ({x_min} 0 0)                                          // 4
    ({x_max} 0 0)                                          // 5
    ({x_max} {r_max * np.cos(wedge_angle)} {r_max * np.sin(wedge_angle)})   // 6
    ({x_min} {r_max * np.cos(wedge_angle)} {r_max * np.sin(wedge_angle)})   // 7
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({nx} {ny} 1) simpleGrading (1 1 1)
);

edges
(
);

boundary
(
    inlet
    {{
        type patch;
        faces
        (
            (0 4 7 3)
        );
    }}
    outlet
    {{
        type patch;
        faces
        (
            (1 2 6 5)
        );
    }}
    wall
    {{
        type wall;
        faces
        (
            (3 7 6 2)
        );
    }}
    axis
    {{
        type symmetryPlane;
        faces
        (
            (0 1 5 4)
        );
    }}
    front
    {{
        type wedge;
        faces
        (
            (0 3 2 1)
        );
    }}
    back
    {{
        type wedge;
        faces
        (
            (4 5 6 7)
        );
    }}
);

mergePatchPairs
(
);
"""
    
    with open(case_dir / 'system' / 'blockMeshDict', 'w') as f:
        f.write(content)


def write_control_dict(case_dir: Path, params: dict):
    """Write controlDict"""
    
    max_iter = params.get('max_iter', 5000) if params else 5000
    
    content = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}}

application     rhoCentralFoam;

startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         0.001;
deltaT          1e-8;

writeControl    adjustableRunTime;
writeInterval   1e-4;

purgeWrite      5;

writeFormat     ascii;
writePrecision  8;
writeCompression off;

timeFormat      general;
timePrecision   6;

runTimeModifiable true;

adjustTimeStep  yes;
maxCo           0.5;
maxDeltaT       1e-5;

functions
{{
    fieldAverage1
    {{
        type            fieldAverage;
        functionObjectLibs ("libfieldFunctionObjects.so");
        enabled         true;
        writeControl    writeTime;
        fields
        (
            U
            {{
                mean        on;
                prime2Mean  on;
                base        time;
            }}
            p
            {{
                mean        on;
                prime2Mean  on;
                base        time;
            }}
        );
    }}
}}
"""
    
    with open(case_dir / 'system' / 'controlDict', 'w') as f:
        f.write(content)


def write_fv_schemes(case_dir: Path):
    """Write fvSchemes"""
    
    content = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}

ddtSchemes
{
    default         Euler;
}

gradSchemes
{
    default         Gauss linear;
}

divSchemes
{
    default         none;
    div(tauMC)      Gauss linear;
}

laplacianSchemes
{
    default         Gauss linear corrected;
}

interpolationSchemes
{
    default         linear;
    reconstruct(rho) vanLeer;
    reconstruct(U)  vanLeerV;
    reconstruct(T)  vanLeer;
}

snGradSchemes
{
    default         corrected;
}

fluxRequired
{
    default         no;
}
"""
    
    with open(case_dir / 'system' / 'fvSchemes', 'w') as f:
        f.write(content)


def write_fv_solution(case_dir: Path):
    """Write fvSolution"""
    
    content = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}

solvers
{
    "(rho|rhoU|rhoE)"
    {
        solver          diagonal;
    }

    U
    {
        solver          smoothSolver;
        smoother        GaussSeidel;
        tolerance       1e-09;
        relTol          0.01;
    }

    e
    {
        $U;
        tolerance       1e-09;
        relTol          0.01;
    }
}
"""
    
    with open(case_dir / 'system' / 'fvSolution', 'w') as f:
        f.write(content)


def write_thermophysical_properties(case_dir: Path, params: dict):
    """Write thermophysicalProperties"""
    
    gamma = params.get('gamma', 1.2) if params else 1.2
    molar_mass = params.get('molar_mass', 0.025) if params else 0.025
    
    # Calculate Cp from gamma and R
    R = 8.314 / molar_mass
    Cv = R / (gamma - 1)
    Cp = gamma * Cv
    
    content = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      thermophysicalProperties;
}}

thermoType
{{
    type            hePsiThermo;
    mixture         pureMixture;
    transport       const;
    thermo          hConst;
    equationOfState perfectGas;
    specie          specie;
    energy          sensibleInternalEnergy;
}}

mixture
{{
    specie
    {{
        molWeight   {molar_mass * 1000:.2f};  // g/mol
    }}
    thermodynamics
    {{
        Cp          {Cp:.1f};
        Hf          0;
    }}
    transport
    {{
        mu          1.8e-5;
        Pr          0.7;
    }}
}}
"""
    
    with open(case_dir / 'constant' / 'thermophysicalProperties', 'w') as f:
        f.write(content)


def write_turbulence_properties(case_dir: Path):
    """Write turbulenceProperties (laminar for now)"""
    
    content = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      turbulenceProperties;
}

simulationType  laminar;
"""
    
    with open(case_dir / 'constant' / 'turbulenceProperties', 'w') as f:
        f.write(content)


def write_initial_conditions(case_dir: Path, params: dict):
    """Write initial condition files"""
    
    p_chamber = params.get('p_chamber', 1e6) if params else 1e6
    t_chamber = params.get('t_chamber', 3000) if params else 3000
    gamma = params.get('gamma', 1.2) if params else 1.2
    molar_mass = params.get('molar_mass', 0.025) if params else 0.025
    
    R = 8.314 / molar_mass
    rho = p_chamber / (R * t_chamber)
    c = np.sqrt(gamma * p_chamber / rho)
    u_inlet = 0.3 * c
    
    # Pressure
    p_content = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}}

dimensions      [1 -1 -2 0 0 0 0];

internalField   uniform {p_chamber};

boundaryField
{{
    inlet
    {{
        type            fixedValue;
        value           uniform {p_chamber};
    }}
    outlet
    {{
        type            waveTransmissive;
        field           p;
        psi             thermo:psi;
        gamma           {gamma};
        fieldInf        {p_chamber * 0.01};
        lInf            0.1;
        value           uniform {p_chamber * 0.01};
    }}
    wall
    {{
        type            zeroGradient;
    }}
    axis
    {{
        type            symmetryPlane;
    }}
    front
    {{
        type            wedge;
    }}
    back
    {{
        type            wedge;
    }}
}}
"""
    
    with open(case_dir / '0' / 'p', 'w') as f:
        f.write(p_content)
    
    # Velocity
    U_content = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}}

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform ({u_inlet} 0 0);

boundaryField
{{
    inlet
    {{
        type            fixedValue;
        value           uniform ({u_inlet} 0 0);
    }}
    outlet
    {{
        type            zeroGradient;
    }}
    wall
    {{
        type            slip;
    }}
    axis
    {{
        type            symmetryPlane;
    }}
    front
    {{
        type            wedge;
    }}
    back
    {{
        type            wedge;
    }}
}}
"""
    
    with open(case_dir / '0' / 'U', 'w') as f:
        f.write(U_content)
    
    # Temperature
    T_content = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      T;
}}

dimensions      [0 0 0 1 0 0 0];

internalField   uniform {t_chamber};

boundaryField
{{
    inlet
    {{
        type            fixedValue;
        value           uniform {t_chamber};
    }}
    outlet
    {{
        type            zeroGradient;
    }}
    wall
    {{
        type            zeroGradient;
    }}
    axis
    {{
        type            symmetryPlane;
    }}
    front
    {{
        type            wedge;
    }}
    back
    {{
        type            wedge;
    }}
}}
"""
    
    with open(case_dir / '0' / 'T', 'w') as f:
        f.write(T_content)


def main():
    if len(sys.argv) < 3:
        print("Usage: convert_to_openfoam.py <mesh.json> <output_dir> [params.json]")
        sys.exit(1)
    
    mesh_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    params = None
    if len(sys.argv) > 3:
        with open(sys.argv[3], 'r') as f:
            params = json.load(f)
    
    create_openfoam_case(mesh_file, output_dir, params)


if __name__ == "__main__":
    main()
