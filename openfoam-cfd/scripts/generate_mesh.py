#!/usr/bin/env python3
"""
Rocket Nozzle Mesh Generator for Loci-STREAM
Generates axisymmetric mesh in UGRID format, then converts to VOG
"""

import numpy as np
import json
import sys
import struct
from pathlib import Path


def create_nozzle_geometry(params: dict) -> tuple:
    """
    Create nozzle wall profile from parameters
    Returns x coordinates and r (radius) coordinates
    """
    r_throat = params.get('r_throat', 0.02)
    r_chamber = params.get('r_chamber', 0.04)
    r_exit = params.get('r_exit', 0.06)
    l_chamber = params.get('l_chamber', 0.1)
    l_nozzle = params.get('l_nozzle', 0.15)
    l_plume = params.get('l_plume', l_nozzle * 2.0)
    
    nx = params.get('nx', 200)
    
    total_length = l_chamber + l_nozzle + l_plume
    x = np.linspace(0, total_length, nx)
    r = np.zeros_like(x)
    
    # Convergent section length
    l_conv = l_chamber * 0.3
    throat_x = l_chamber
    exit_x = l_chamber + l_nozzle
    
    for i, xi in enumerate(x):
        if xi < throat_x - l_conv:
            # Chamber (constant radius)
            r[i] = r_chamber
        elif xi <= throat_x:
            # Convergent section (smooth contraction)
            t = (xi - (throat_x - l_conv)) / l_conv
            # Cosine blend for smooth transition
            blend = (1.0 - np.cos(t * np.pi)) / 2.0
            r[i] = r_chamber - (r_chamber - r_throat) * blend
        elif xi <= exit_x:
            # Divergent section (Rao parabola approximation)
            t = (xi - throat_x) / l_nozzle
            # Parabolic expansion with slight modification for Rao contour
            r[i] = r_throat + (r_exit - r_throat) * (2*t - t**2)**0.85
        else:
            # Plume region (expanding cone)
            expansion_angle = 0.3  # ~17 degrees
            r[i] = r_exit + (xi - exit_x) * np.tan(expansion_angle)
    
    return x, r


def generate_structured_mesh(x_wall: np.ndarray, r_wall: np.ndarray, 
                             ny: int, stretch_factor: float = 1.2) -> dict:
    """
    Generate structured 2D axisymmetric mesh
    Uses geometric stretching near wall for boundary layer resolution
    """
    nx = len(x_wall)
    
    # Create node arrays
    nodes_x = np.zeros((ny, nx))
    nodes_r = np.zeros((ny, nx))
    
    for i in range(nx):
        # Radial distribution with geometric stretching
        # More points near wall (for boundary layer)
        eta = np.zeros(ny)
        for j in range(ny):
            if stretch_factor != 1.0:
                # Geometric stretching
                eta[j] = (stretch_factor**j - 1) / (stretch_factor**(ny-1) - 1)
            else:
                eta[j] = j / (ny - 1)
        
        nodes_x[:, i] = x_wall[i]
        nodes_r[:, i] = r_wall[i] * eta
    
    # Create quadrilateral cells (will be triangulated for UGRID)
    cells = []
    for j in range(ny - 1):
        for i in range(nx - 1):
            # Node indices (0-based)
            n0 = j * nx + i
            n1 = j * nx + (i + 1)
            n2 = (j + 1) * nx + (i + 1)
            n3 = (j + 1) * nx + i
            
            # Split quad into two triangles
            cells.append([n0, n1, n2])
            cells.append([n0, n2, n3])
    
    # Boundary faces
    # BC1: Inlet (left, i=0)
    inlet_faces = []
    for j in range(ny - 1):
        inlet_faces.append([j * nx, (j + 1) * nx])
    
    # BC2: Outlet (right, i=nx-1)
    outlet_faces = []
    for j in range(ny - 1):
        outlet_faces.append([j * nx + (nx - 1), (j + 1) * nx + (nx - 1)])
    
    # BC3: Axis (bottom, j=0)
    axis_faces = []
    for i in range(nx - 1):
        axis_faces.append([i, i + 1])
    
    # BC4: Wall (top, j=ny-1)
    wall_faces = []
    for i in range(nx - 1):
        wall_faces.append([(ny - 1) * nx + i, (ny - 1) * nx + (i + 1)])
    
    return {
        'nodes_x': nodes_x.flatten(),
        'nodes_r': nodes_r.flatten(),
        'cells': np.array(cells),
        'inlet_faces': inlet_faces,
        'outlet_faces': outlet_faces,
        'axis_faces': axis_faces,
        'wall_faces': wall_faces,
        'nx': nx,
        'ny': ny
    }


def write_ugrid_ascii(mesh: dict, filename: str):
    """
    Write mesh in AFLR3 UGRID ASCII format
    """
    nodes_x = mesh['nodes_x']
    nodes_r = mesh['nodes_r']
    cells = mesh['cells']
    n_nodes = len(nodes_x)
    n_tris = len(cells)
    
    # Boundary faces
    inlet = mesh['inlet_faces']
    outlet = mesh['outlet_faces']
    axis = mesh['axis_faces']
    wall = mesh['wall_faces']
    n_boundary_faces = len(inlet) + len(outlet) + len(axis) + len(wall)
    
    with open(filename, 'w') as f:
        # Header: n_nodes, n_tris, n_quads, n_tets, n_pyramids, n_prisms, n_hexes
        f.write(f"{n_nodes} {n_boundary_faces} {n_tris} 0 0 0 0\n")
        
        # Nodes (x, y, z) - for 2D axisymmetric, z=0
        for i in range(n_nodes):
            f.write(f"{nodes_x[i]:.10e} {nodes_r[i]:.10e} 0.0\n")
        
        # Boundary faces (edges in 2D) with boundary markers
        # BC1=inlet, BC2=outlet, BC3=axis, BC4=wall
        for face in inlet:
            f.write(f"{face[0]+1} {face[1]+1} 1\n")
        for face in outlet:
            f.write(f"{face[0]+1} {face[1]+1} 2\n")
        for face in axis:
            f.write(f"{face[0]+1} {face[1]+1} 3\n")
        for face in wall:
            f.write(f"{face[0]+1} {face[1]+1} 4\n")
        
        # Triangle cells (1-indexed)
        for cell in cells:
            f.write(f"{cell[0]+1} {cell[1]+1} {cell[2]+1}\n")


def write_ugrid_binary(mesh: dict, filename: str):
    """
    Write mesh in AFLR3 UGRID binary format (.b8.ugrid)
    """
    nodes_x = mesh['nodes_x']
    nodes_r = mesh['nodes_r']
    cells = mesh['cells']
    n_nodes = len(nodes_x)
    n_tris = len(cells)
    
    inlet = mesh['inlet_faces']
    outlet = mesh['outlet_faces']
    axis = mesh['axis_faces']
    wall = mesh['wall_faces']
    n_boundary_faces = len(inlet) + len(outlet) + len(axis) + len(wall)
    
    with open(filename, 'wb') as f:
        # Header
        header = struct.pack('7i', n_nodes, n_boundary_faces, n_tris, 0, 0, 0, 0)
        f.write(header)
        
        # Nodes
        for i in range(n_nodes):
            f.write(struct.pack('3d', nodes_x[i], nodes_r[i], 0.0))
        
        # Boundary faces with markers
        for face in inlet:
            f.write(struct.pack('3i', face[0]+1, face[1]+1, 1))
        for face in outlet:
            f.write(struct.pack('3i', face[0]+1, face[1]+1, 2))
        for face in axis:
            f.write(struct.pack('3i', face[0]+1, face[1]+1, 3))
        for face in wall:
            f.write(struct.pack('3i', face[0]+1, face[1]+1, 4))
        
        # Triangles
        for cell in cells:
            f.write(struct.pack('3i', cell[0]+1, cell[1]+1, cell[2]+1))


def generate_vars_file(params: dict, filename: str):
    """
    Generate Loci-STREAM .vars run control file
    """
    p_chamber = params.get('p_chamber', 1000000.0)
    t_chamber = params.get('t_chamber', 3000.0)
    gamma = params.get('gamma', 1.2)
    molar_mass = params.get('molar_mass', 0.025)
    max_iter = params.get('max_iter', 5000)
    
    # Calculate gas properties
    R = 8.314 / molar_mass  # Specific gas constant
    rho_chamber = p_chamber / (R * t_chamber)
    
    # Estimate inlet velocity (subsonic, M~0.3)
    c_chamber = np.sqrt(gamma * p_chamber / rho_chamber)
    v_inlet = 0.3 * c_chamber
    
    # Dynamic viscosity (Sutherland's law approximation)
    mu_ref = 1.8e-5
    T_ref = 300.0
    S = 110.4
    mu = mu_ref * (t_chamber / T_ref)**1.5 * (T_ref + S) / (t_chamber + S)
    
    vars_content = f"""// Loci-STREAM run control file for rocket nozzle simulation
// Generated automatically by SITH Combustion
{{
    // Grid file information
    grid_file_info: <file_type=VOG, Lref=1 m>
    
    // Boundary conditions
    boundary_conditions:
    <
        BC_1=incompressibleInlet(v={v_inlet:.4f} m/s, T={t_chamber:.1f} K),  // Inlet
        BC_2=fixedPressureOutlet(p={p_chamber * 0.01:.1f} Pa),              // Outlet (low pressure)
        BC_3=symmetry,                                                       // Axis
        BC_4=noslip                                                          // Wall
    >
    
    // Initial conditions
    initialCondition: <rho={rho_chamber:.4f} kg/m/m/m, v={v_inlet:.1f} m/s, p={p_chamber:.1f} Pa, T={t_chamber:.1f} K>
    
    // Thermodynamic properties
    chemistry_model: air_1s0r
    transport_model: const_viscosity
    mu: {mu:.6e}
    gamma: {gamma}
    Rgas: {R:.4f}
    
    // Flow properties
    flowRegime: turbulent
    turbulenceModel: Menter_SST
    flowCompressibility: compressible
    
    // Time integration
    timeIntegrator: BDF
    timeStep: 1.0e-7
    numTimeSteps: {max_iter}
    convergenceTolerance: 1.0e-6
    maxIterationsPerTimeStep: 20
    
    // Spatial discretization
    inviscidFlux: Roe
    limiter: Venkatakrishnan
    gradientMethod: leastSquares
    
    // Linear solvers
    momentumEquationOptions: <linearSolver=SGS, relaxationFactor=0.7, maxIterations=10>
    pressureCorrectionEquationOptions: <linearSolver=PETSC, relaxationFactor=0.3, maxIterations=50>
    energyEquationOptions: <linearSolver=SGS, relaxationFactor=0.8, maxIterations=10>
    turbulenceEquationOptions: <linearSolver=SGS, relaxationFactor=0.7, maxIterations=10>
    
    // Output
    print_freq: 100
    plot_freq: 500
    restart_freq: 1000
}}
"""
    
    with open(filename, 'w') as f:
        f.write(vars_content)


def main():
    if len(sys.argv) < 2:
        print("Usage: generate_mesh.py <params.json> [output_dir]")
        print("  params.json: JSON file with nozzle parameters")
        print("  output_dir: Directory for output files (default: /data/input)")
        sys.exit(1)
    
    params_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "/data/input"
    
    # Load parameters
    with open(params_file, 'r') as f:
        params = json.load(f)
    
    print(f"Generating mesh for nozzle simulation...")
    print(f"  Throat radius: {params.get('r_throat', 0.02)} m")
    print(f"  Chamber radius: {params.get('r_chamber', 0.04)} m")
    print(f"  Exit radius: {params.get('r_exit', 0.06)} m")
    
    # Generate geometry
    x_wall, r_wall = create_nozzle_geometry(params)
    
    # Generate mesh
    ny = params.get('ny', 80)
    mesh = generate_structured_mesh(x_wall, r_wall, ny, stretch_factor=1.15)
    
    print(f"  Mesh size: {mesh['nx']} x {mesh['ny']} = {len(mesh['nodes_x'])} nodes")
    print(f"  Cells: {len(mesh['cells'])} triangles")
    
    # Write mesh files
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    case_name = params.get('case_name', 'nozzle')
    
    # ASCII UGRID (for debugging)
    ugrid_file = output_path / f"{case_name}.ugrid"
    write_ugrid_ascii(mesh, str(ugrid_file))
    print(f"  Written: {ugrid_file}")
    
    # Generate .vars file
    vars_file = output_path / f"{case_name}.vars"
    generate_vars_file(params, str(vars_file))
    print(f"  Written: {vars_file}")
    
    # Save mesh data as JSON for direct use
    mesh_json = {
        'x': mesh['nodes_x'].tolist(),
        'r': mesh['nodes_r'].tolist(),
        'cells': mesh['cells'].tolist(),
        'nx': mesh['nx'],
        'ny': mesh['ny']
    }
    with open(output_path / f"{case_name}_mesh.json", 'w') as f:
        json.dump(mesh_json, f)
    
    print("Mesh generation complete!")


if __name__ == "__main__":
    main()
