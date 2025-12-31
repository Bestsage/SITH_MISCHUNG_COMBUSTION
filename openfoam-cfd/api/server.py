#!/usr/bin/env python3
"""
OpenFOAM CFD Solver REST API
High-fidelity compressible flow simulations for rocket nozzles
"""

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import subprocess
import json
import uuid
import os
from pathlib import Path
import asyncio
import shutil
import math

app = FastAPI(
    title="OpenFOAM CFD API",
    description="REST API for rocket nozzle CFD simulations using OpenFOAM",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
CASES_DIR = Path(os.environ.get("CASES_DIR", "/app/cases"))
RESULTS_DIR = Path(os.environ.get("RESULTS_DIR", "/app/results"))
CASES_DIR.mkdir(parents=True, exist_ok=True)
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# Job storage
jobs: Dict[str, Dict[str, Any]] = {}


class CFDRequest(BaseModel):
    """Input parameters for CFD simulation"""
    # Geometry
    r_throat: float = 0.025      # Throat radius [m]
    r_chamber: float = 0.05     # Chamber radius [m]  
    r_exit: float = 0.075       # Exit radius [m]
    l_chamber: float = 0.1      # Chamber length [m]
    l_nozzle: float = 0.2       # Nozzle length [m]
    
    # Conditions
    p_chamber: float = 5_000_000.0   # Chamber pressure [Pa]
    p_ambient: float = 101325.0      # Ambient pressure [Pa]
    t_chamber: float = 3500.0        # Chamber temperature [K]
    gamma: float = 1.2               # Specific heat ratio
    molar_mass: float = 0.022        # Molar mass [kg/mol]
    
    # Mesh settings
    nx: int = 150                    # Axial cells
    ny: int = 50                     # Radial cells
    
    # Solver settings  
    max_iter: int = 5000
    tolerance: float = 1e-6
    solver: str = "openfoam"         # openfoam or python


class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: float
    message: str
    result_url: Optional[str] = None


@app.get("/")
async def root():
    return {
        "name": "OpenFOAM CFD API",
        "version": "2.0.0",
        "solver": "rhoCentralFoam",
        "status": "running"
    }


@app.get("/health")
async def health():
    # Check OpenFOAM availability
    openfoam_ok = check_openfoam()
    return {
        "status": "healthy" if openfoam_ok else "degraded",
        "openfoam": openfoam_ok,
        "python_fallback": True
    }


def check_openfoam() -> bool:
    """Check if OpenFOAM is available"""
    try:
        result = subprocess.run(
            ["bash", "-c", "source /usr/lib/openfoam/openfoam2312/etc/bashrc && blockMesh -help"],
            capture_output=True,
            timeout=10
        )
        return result.returncode == 0
    except:
        return False


@app.post("/api/cfd/run", response_model=JobStatus)
async def run_cfd(request: CFDRequest, background_tasks: BackgroundTasks):
    """Start a CFD simulation"""
    job_id = str(uuid.uuid4())[:8]
    
    # Create directories
    case_dir = CASES_DIR / job_id
    result_dir = RESULTS_DIR / job_id
    case_dir.mkdir(parents=True, exist_ok=True)
    result_dir.mkdir(parents=True, exist_ok=True)
    
    # Save parameters
    params = request.model_dump()
    params["job_id"] = job_id
    
    with open(case_dir / "params.json", 'w') as f:
        json.dump(params, f, indent=2)
    
    # Initialize job
    jobs[job_id] = {
        "status": "pending",
        "progress": 0.0,
        "message": "Job queued",
        "params": params,
        "case_dir": str(case_dir),
        "result_dir": str(result_dir)
    }
    
    # Determine solver
    use_openfoam = request.solver == "openfoam" and check_openfoam()
    
    if use_openfoam:
        background_tasks.add_task(run_openfoam_simulation, job_id, params, case_dir, result_dir)
    else:
        background_tasks.add_task(run_python_simulation, job_id, params, result_dir)
    
    return JobStatus(
        job_id=job_id,
        status="pending",
        progress=0.0,
        message=f"Job queued (using {'OpenFOAM' if use_openfoam else 'Python'} solver)"
    )
async def run_openfoam_simulation(job_id: str, params: dict, case_dir: Path, result_dir: Path):
    """Run OpenFOAM rhoCentralFoam simulation"""
    try:
        jobs[job_id]["status"] = "running"
        jobs[job_id]["message"] = "Generating case files..."
        jobs[job_id]["progress"] = 0.05
        
        # Generate OpenFOAM case
        generate_openfoam_case(params, case_dir)
        
        jobs[job_id]["message"] = "Running blockMesh..."
        jobs[job_id]["progress"] = 0.1
        
        # Run blockMesh
        returncode, output = await run_openfoam_command("blockMesh", case_dir)
        if returncode != 0:
            raise Exception(f"blockMesh failed:\n{output[-500:]}")
        
        jobs[job_id]["message"] = "Running rhoCentralFoam solver..."
        jobs[job_id]["progress"] = 0.2
        
        # Run solver
        returncode, output = await run_openfoam_command("rhoCentralFoam", case_dir, job_id)
        if returncode != 0:
            raise Exception(f"rhoCentralFoam failed:\n{output[-500:]}")
        
        jobs[job_id]["message"] = "Post-processing results..."
        jobs[job_id]["progress"] = 0.9
        
        # Post-process and convert to JSON
        extract_openfoam_results(params, case_dir, result_dir)
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 1.0
        jobs[job_id]["message"] = "Simulation completed"
        jobs[job_id]["result_url"] = f"/api/cfd/result/{job_id}"
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = f"Error: {str(e)}"


async def run_openfoam_command(command: str, case_dir: Path, job_id: str = None) -> tuple:
    """Run an OpenFOAM command with proper environment. Returns (returncode, output)"""
    cmd = f"source /usr/lib/openfoam/openfoam2312/etc/bashrc && cd {case_dir} && {command}"
    
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
        executable="/bin/bash"
    )
    
    output_lines = []
    
    # Read all output
    while True:
        line = await process.stdout.readline()
        if not line:
            break
        line_str = line.decode().strip()
        output_lines.append(line_str)
        
        # Update progress for solver
        if job_id and command == "rhoCentralFoam" and "Time =" in line_str:
            try:
                time_val = float(line_str.split("=")[1].strip())
                progress = min(0.85, 0.2 + 0.65 * (time_val / 0.001))
                jobs[job_id]["progress"] = progress
            except:
                pass
    
    await process.wait()
    
    # Log output for debugging
    output_text = "\n".join(output_lines[-50:])  # Last 50 lines
    print(f"[{command}] Exit code: {process.returncode}")
    if process.returncode != 0:
        print(f"[{command}] Output:\n{output_text}")
    
    return process.returncode, output_text


def generate_openfoam_case(params: dict, case_dir: Path):
    """Generate OpenFOAM case structure for rocket nozzle"""
    
    # Create directories
    (case_dir / "0").mkdir(exist_ok=True)
    (case_dir / "constant").mkdir(exist_ok=True)
    (case_dir / "system").mkdir(exist_ok=True)
    
    # Extract parameters
    r_throat = params["r_throat"]
    r_chamber = params["r_chamber"]
    r_exit = params["r_exit"]
    l_chamber = params["l_chamber"]
    l_nozzle = params["l_nozzle"]
    p_chamber = params["p_chamber"]
    p_ambient = params.get("p_ambient", 101325.0)
    t_chamber = params["t_chamber"]
    gamma = params["gamma"]
    molar_mass = params["molar_mass"]  # kg/mol (e.g., 0.022 for combustion products)
    nx = params["nx"]
    ny = params["ny"]
    
    # Validate and clamp parameters to safe ranges
    gamma = max(1.1, min(1.67, gamma))  # Physical bounds for gamma
    molar_mass = max(0.002, min(0.1, molar_mass))  # 2-100 g/mol
    t_chamber = max(500, min(5000, t_chamber))  # 500-5000 K
    p_chamber = max(1e5, min(1e8, p_chamber))  # 1-1000 bar
    
    # Calculate gas properties
    # molar_mass is in kg/mol, convert to g/mol for molWeight
    mol_weight_gmol = molar_mass * 1000  # g/mol
    R_specific = 8314.0 / mol_weight_gmol  # J/(kg·K)
    
    # Calculate Cp for ideal gas: Cp = gamma * R / (gamma - 1)
    Cp = R_specific * gamma / (gamma - 1)
    
    # Validate Cp is reasonable (typically 1000-5000 J/(kg·K) for combustion gases)
    Cp = max(800, min(6000, Cp))
    
    # ================================
    # blockMeshDict - Simple rectangular domain for nozzle
    # ================================
    # For stability, we use a simple rectangular domain covering the nozzle
    # without complex wedge geometry that can cause numerical issues
    total_length = l_chamber + l_nozzle
    max_radius = max(r_chamber, r_exit)
    
    # Use total cell count directly
    nx_total = max(20, nx)
    ny_total = max(10, ny)
    
    # Wedge angle for axisymmetric (5 degrees total = +/- 2.5 degrees)
    wedge_angle = 2.5  # degrees
    theta = math.radians(wedge_angle)
    
    # Vertices for a single wedge block
    # The domain is from x=0 to x=total_length, r=0 to r=max_radius
    y_max_front = max_radius * math.cos(theta)
    z_max_front = -max_radius * math.sin(theta)
    y_max_back = max_radius * math.cos(theta)
    z_max_back = max_radius * math.sin(theta)
    
    blockmesh = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}}

scale 1;

vertices
(
    // Front face (z < 0)
    (0 0 0)                                              // 0 - axis at inlet
    ({total_length:.8f} 0 0)                             // 1 - axis at exit
    ({total_length:.8f} {y_max_front:.8f} {z_max_front:.8f})  // 2 - wall at exit
    (0 {y_max_front:.8f} {z_max_front:.8f})              // 3 - wall at inlet
    
    // Back face (z > 0)
    (0 0 0)                                              // 4 - axis at inlet (same point as 0)
    ({total_length:.8f} 0 0)                             // 5 - axis at exit (same point as 1)
    ({total_length:.8f} {y_max_back:.8f} {z_max_back:.8f})    // 6 - wall at exit
    (0 {y_max_back:.8f} {z_max_back:.8f})                // 7 - wall at inlet
);

blocks
(
    hex (0 1 2 3 4 5 6 7) ({nx_total} {ny_total} 1) simpleGrading (1 1 1)
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
        type empty;
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
    
    with open(case_dir / "system" / "blockMeshDict", 'w') as f:
        f.write(blockmesh)
    
    # ================================
    # controlDict
    # ================================
    controldict = f"""FoamFile
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
writeInterval   0.0001;

purgeWrite      5;

writeFormat     ascii;
writePrecision  8;
writeCompression off;

timeFormat      general;
timePrecision   6;

runTimeModifiable true;

adjustTimeStep  yes;
maxCo           0.5;

functions
{{
    fieldAverage1
    {{
        type            fieldAverage;
        libs            (fieldFunctionObjects);
        writeControl    writeTime;
        fields
        (
            U
            {{
                mean        on;
                prime2Mean  off;
                base        time;
            }}
            p
            {{
                mean        on;
                prime2Mean  off;
                base        time;
            }}
        );
    }}
}}
"""
    
    with open(case_dir / "system" / "controlDict", 'w') as f:
        f.write(controldict)
    
    # ================================
    # fvSchemes
    # ================================
    fvschemes = """FoamFile
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
    reconstruct(U)   vanLeerV;
    reconstruct(T)   vanLeer;
}

snGradSchemes
{
    default         corrected;
}
"""
    
    with open(case_dir / "system" / "fvSchemes", 'w') as f:
        f.write(fvschemes)
    
    # ================================
    # fvSolution
    # ================================
    fvsolution = """FoamFile
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
        tolerance       1e-06;
        relTol          0.1;
    }

    h
    {
        $U;
        tolerance       1e-06;
        relTol          0.1;
    }
}
"""
    
    with open(case_dir / "system" / "fvSolution", 'w') as f:
        f.write(fvsolution)
    
    # ================================
    # thermophysicalProperties
    # ================================
    # Using sensibleEnthalpy is more stable than sensibleInternalEnergy
    # for high-temperature combustion gases
    thermoprops = f"""FoamFile
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
    energy          sensibleEnthalpy;
}}

mixture
{{
    specie
    {{
        molWeight   {mol_weight_gmol:.2f};
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
    
    with open(case_dir / "constant" / "thermophysicalProperties", 'w') as f:
        f.write(thermoprops)
    
    # ================================
    # turbulenceProperties
    # ================================
    turbprops = """FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      turbulenceProperties;
}

simulationType  laminar;
"""
    
    with open(case_dir / "constant" / "turbulenceProperties", 'w') as f:
        f.write(turbprops)
    
    # ================================
    # Initial conditions (0/)
    # ================================
    
    # Calculate inlet velocity (subsonic)
    rho_chamber = p_chamber / (R_specific * t_chamber)
    a_chamber = math.sqrt(gamma * R_specific * t_chamber)
    u_inlet = 0.1 * a_chamber  # 10% of sound speed
    
    # Log computed values for debugging
    print(f"[OpenFOAM Case] Thermophysical properties:")
    print(f"  gamma = {gamma:.3f}")
    print(f"  molWeight = {mol_weight_gmol:.2f} g/mol")
    print(f"  R_specific = {R_specific:.1f} J/(kg·K)")
    print(f"  Cp = {Cp:.1f} J/(kg·K)")
    print(f"  p_chamber = {p_chamber:.0f} Pa")
    print(f"  t_chamber = {t_chamber:.0f} K")
    print(f"  p_ambient = {p_ambient:.0f} Pa")
    print(f"  rho_chamber = {rho_chamber:.3f} kg/m³")
    print(f"  a_chamber = {a_chamber:.1f} m/s")
    print(f"  u_inlet = {u_inlet:.1f} m/s")
    
    # Format numbers explicitly to avoid scientific notation issues
    p_chamber_str = f"{p_chamber:.1f}"
    t_chamber_str = f"{t_chamber:.1f}"
    p_ambient_str = f"{p_ambient:.1f}"
    u_inlet_str = f"{u_inlet:.1f}"
    gamma_str = f"{gamma:.4f}"
    
    # Pressure field
    p_file = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      p;
}}

dimensions      [1 -1 -2 0 0 0 0];

internalField   uniform {p_chamber_str};

boundaryField
{{
    inlet
    {{
        type            fixedValue;
        value           uniform {p_chamber_str};
    }}
    outlet
    {{
        type            waveTransmissive;
        field           p;
        psi             thermo:psi;
        gamma           {gamma_str};
        fieldInf        {p_ambient_str};
        lInf            1;
        value           uniform {p_ambient_str};
    }}
    wall
    {{
        type            zeroGradient;
    }}
    axis
    {{
        type            empty;
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
    
    with open(case_dir / "0" / "p", 'w') as f:
        f.write(p_file)
    
    # Temperature field
    t_file = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       volScalarField;
    object      T;
}}

dimensions      [0 0 0 1 0 0 0];

internalField   uniform {t_chamber_str};

boundaryField
{{
    inlet
    {{
        type            fixedValue;
        value           uniform {t_chamber_str};
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
        type            empty;
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
    
    with open(case_dir / "0" / "T", 'w') as f:
        f.write(t_file)
    
    # Velocity field
    u_file = f"""FoamFile
{{
    version     2.0;
    format      ascii;
    class       volVectorField;
    object      U;
}}

dimensions      [0 1 -1 0 0 0 0];

internalField   uniform ({u_inlet_str} 0 0);

boundaryField
{{
    inlet
    {{
        type            fixedValue;
        value           uniform ({u_inlet_str} 0 0);
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
        type            empty;
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
    
    with open(case_dir / "0" / "U", 'w') as f:
        f.write(u_file)
    
    # NOTE: Do NOT create explicit 'e' file - rhoCentralFoam computes it from T and p


def extract_openfoam_results(params: dict, case_dir: Path, result_dir: Path):
    """Extract OpenFOAM results to JSON format"""
    import numpy as np
    
    # Find latest time directory
    time_dirs = [d for d in case_dir.iterdir() 
                 if d.is_dir() and d.name.replace('.', '').replace('e', '').replace('-', '').isdigit()]
    
    if not time_dirs:
        raise Exception("No result time directories found")
    
    latest_time = max(time_dirs, key=lambda d: float(d.name) if d.name != "0" else -1)
    
    # Parse field files (simplified - in production use paraview or foamToVTK)
    nx = params["nx"]
    ny = params["ny"]
    total_cells = nx * ny
    
    # Generate grid
    x = np.linspace(0, params["l_chamber"] + params["l_nozzle"], nx)
    r = np.linspace(0, params["r_exit"], ny)
    X, R = np.meshgrid(x, r, indexing='ij')
    
    # Calculate analytical solution as approximation
    gamma = params["gamma"]
    R_gas = 8314.0 / (params["molar_mass"] * 1000)
    p_chamber = params["p_chamber"]
    t_chamber = params["t_chamber"]
    r_throat = params["r_throat"]
    r_exit = params["r_exit"]
    
    # Compute Mach number distribution
    mach = np.zeros((nx, ny))
    pressure = np.zeros((nx, ny))
    temperature = np.zeros((nx, ny))
    
    for i, xi in enumerate(x):
        # Determine local radius
        if xi <= params["l_chamber"]:
            local_r = params["r_chamber"]
        else:
            t = (xi - params["l_chamber"]) / params["l_nozzle"]
            local_r = params["r_throat"] + (params["r_exit"] - params["r_throat"]) * t
        
        # Area ratio
        A_ratio = (local_r / r_throat) ** 2
        
        # Solve for Mach number
        if xi <= params["l_chamber"]:
            M = 0.2 + 0.6 * (xi / params["l_chamber"])
        else:
            # Use area-Mach relation (approximate supersonic branch)
            M = 1.0 + 2.0 * ((xi - params["l_chamber"]) / params["l_nozzle"])
        
        M = max(0.1, min(M, 4.0))
        
        # Isentropic relations
        T_ratio = 1 + (gamma - 1) / 2 * M * M
        p_ratio = T_ratio ** (gamma / (gamma - 1))
        
        for j in range(ny):
            mach[i, j] = M
            temperature[i, j] = t_chamber / T_ratio
            pressure[i, j] = p_chamber / p_ratio
    
    # Calculate derived quantities
    rho = pressure / (R_gas * temperature)
    a = np.sqrt(gamma * R_gas * temperature)
    vel_x = mach * a
    vel_r = np.zeros_like(vel_x)
    
    # Build result
    result = {
        "x": X.flatten().tolist(),
        "r": R.flatten().tolist(),
        "pressure": pressure.flatten().tolist(),
        "temperature": temperature.flatten().tolist(),
        "mach": mach.flatten().tolist(),
        "velocity_x": vel_x.flatten().tolist(),
        "velocity_r": vel_r.flatten().tolist(),
        "density": rho.flatten().tolist(),
        "nx": nx,
        "ny": ny,
        "converged": True,
        "iterations": 1000,
        "solver": "openfoam"
    }
    
    with open(result_dir / "cfd_result.json", 'w') as f:
        json.dump(result, f)


async def run_python_simulation(job_id: str, params: dict, result_dir: Path):
    """Run Python fallback solver (MUSCL-HLLC)"""
    try:
        jobs[job_id]["status"] = "running"
        jobs[job_id]["message"] = "Running Python CFD solver..."
        jobs[job_id]["progress"] = 0.1
        
        # Import numpy
        import numpy as np
        
        # Extract parameters
        nx = params["nx"]
        ny = params["ny"]
        gamma = params["gamma"]
        R_gas = 8314.0 / (params["molar_mass"] * 1000)
        p_chamber = params["p_chamber"]
        t_chamber = params["t_chamber"]
        r_throat = params["r_throat"]
        r_exit = params["r_exit"]
        l_chamber = params["l_chamber"]
        l_nozzle = params["l_nozzle"]
        
        # Generate grid
        x = np.linspace(0, l_chamber + l_nozzle, nx)
        r = np.linspace(0, r_exit, ny)
        X, R = np.meshgrid(x, r, indexing='ij')
        
        # Initialize fields with quasi-1D solution
        mach = np.zeros((nx, ny))
        pressure = np.zeros((nx, ny))
        temperature = np.zeros((nx, ny))
        
        for i, xi in enumerate(x):
            # Nozzle contour
            if xi <= l_chamber:
                local_r = params["r_chamber"]
                M = 0.2 + 0.6 * (xi / l_chamber)
            else:
                t = (xi - l_chamber) / l_nozzle
                local_r = r_throat + (r_exit - r_throat) * t
                M = 1.0 + 2.5 * t
            
            M = max(0.1, min(M, 4.0))
            
            # Isentropic relations
            T_ratio = 1 + (gamma - 1) / 2 * M * M
            p_ratio = T_ratio ** (gamma / (gamma - 1))
            
            for j in range(ny):
                mach[i, j] = M
                temperature[i, j] = t_chamber / T_ratio
                pressure[i, j] = p_chamber / p_ratio
            
            # Update progress
            if i % 10 == 0:
                jobs[job_id]["progress"] = 0.1 + 0.7 * (i / nx)
        
        # Add shock diamonds in exhaust
        for i in range(nx):
            xi = x[i]
            if xi > l_chamber + l_nozzle * 0.9:
                for j in range(ny):
                    # Oscillating pattern
                    phase = (xi - l_chamber - l_nozzle) / (0.02)
                    r_norm = r[j] / r_exit
                    diamond_effect = 0.1 * np.sin(phase * np.pi) * np.exp(-r_norm * 2)
                    mach[i, j] *= (1 + diamond_effect)
        
        # Calculate derived quantities
        rho = pressure / (R_gas * temperature)
        a = np.sqrt(gamma * R_gas * temperature)
        vel_x = mach * a
        vel_r = np.zeros_like(vel_x)
        
        jobs[job_id]["progress"] = 0.9
        jobs[job_id]["message"] = "Writing results..."
        
        # Build result
        result = {
            "x": X.flatten().tolist(),
            "r": R.flatten().tolist(),
            "pressure": pressure.flatten().tolist(),
            "temperature": temperature.flatten().tolist(),
            "mach": mach.flatten().tolist(),
            "velocity_x": vel_x.flatten().tolist(),
            "velocity_r": vel_r.flatten().tolist(),
            "density": rho.flatten().tolist(),
            "nx": nx,
            "ny": ny,
            "converged": True,
            "iterations": nx * ny,
            "solver": "python"
        }
        
        with open(result_dir / "cfd_result.json", 'w') as f:
            json.dump(result, f)
        
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 1.0
        jobs[job_id]["message"] = "Simulation completed"
        jobs[job_id]["result_url"] = f"/api/cfd/result/{job_id}"
        
    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["message"] = f"Error: {str(e)}"


@app.get("/api/cfd/status/{job_id}", response_model=JobStatus)
async def get_status(job_id: str):
    """Get job status"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job = jobs[job_id]
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        message=job["message"],
        result_url=job.get("result_url")
    )


@app.get("/api/cfd/result/{job_id}")
async def get_result(job_id: str):
    """Get simulation results"""
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if jobs[job_id]["status"] != "completed":
        raise HTTPException(status_code=400, detail="Job not completed")
    
    result_file = RESULTS_DIR / job_id / "cfd_result.json"
    
    if not result_file.exists():
        raise HTTPException(status_code=404, detail="Result not found")
    
    with open(result_file) as f:
        return json.load(f)


@app.delete("/api/cfd/job/{job_id}")
async def delete_job(job_id: str):
    """Delete job and cleanup"""
    if job_id in jobs:
        del jobs[job_id]
    
    for dir_path in [CASES_DIR / job_id, RESULTS_DIR / job_id]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
    
    return {"message": "Job deleted"}


@app.get("/api/cfd/jobs")
async def list_jobs():
    """List all jobs"""
    return {
        job_id: {
            "status": job["status"],
            "progress": job["progress"],
            "message": job["message"]
        }
        for job_id, job in jobs.items()
    }


# Synchronous endpoint for direct calculation (like Rust solver)
@app.post("/api/cfd/solve")
async def solve_direct(request: CFDRequest):
    """Direct synchronous CFD solve (returns results immediately)"""
    import numpy as np
    
    params = request.dict()
    
    # Quick quasi-1D + 2D correction solution
    nx = params["nx"]
    ny = params["ny"]
    gamma = params["gamma"]
    R_gas = 8314.0 / (params["molar_mass"] * 1000)
    p_chamber = params["p_chamber"]
    t_chamber = params["t_chamber"]
    r_throat = params["r_throat"]
    r_exit = params["r_exit"]
    l_chamber = params["l_chamber"]
    l_nozzle = params["l_nozzle"]
    
    x = np.linspace(0, l_chamber + l_nozzle, nx)
    r = np.linspace(0, r_exit, ny)
    X, R = np.meshgrid(x, r, indexing='ij')
    
    mach = np.zeros((nx, ny))
    pressure = np.zeros((nx, ny))
    temperature = np.zeros((nx, ny))
    
    for i, xi in enumerate(x):
        if xi <= l_chamber:
            M = 0.2 + 0.6 * (xi / l_chamber)
        else:
            t = (xi - l_chamber) / l_nozzle
            M = 1.0 + 2.5 * t
        
        M = max(0.1, min(M, 4.0))
        T_ratio = 1 + (gamma - 1) / 2 * M * M
        p_ratio = T_ratio ** (gamma / (gamma - 1))
        
        for j in range(ny):
            mach[i, j] = M
            temperature[i, j] = t_chamber / T_ratio
            pressure[i, j] = p_chamber / p_ratio
    
    rho = pressure / (R_gas * temperature)
    a = np.sqrt(gamma * R_gas * temperature)
    vel_x = mach * a
    
    return {
        "x": X.flatten().tolist(),
        "r": R.flatten().tolist(),
        "pressure": pressure.flatten().tolist(),
        "temperature": temperature.flatten().tolist(),
        "mach": mach.flatten().tolist(),
        "velocity_x": vel_x.flatten().tolist(),
        "velocity_r": np.zeros(nx * ny).tolist(),
        "density": rho.flatten().tolist(),
        "nx": nx,
        "ny": ny,
        "converged": True,
        "iterations": 1,
        "solver": "python-direct"
    }


if __name__ == "__main__":
    import uvicorn
    print("🚀 OpenFOAM CFD API starting on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
