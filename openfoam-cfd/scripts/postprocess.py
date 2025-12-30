#!/usr/bin/env python3
"""
Post-processing script for CFD results
Converts solver output to JSON format for the web interface
"""

import numpy as np
import json
import sys
from pathlib import Path


def read_loci_stream_output(output_dir: Path, case_name: str) -> dict:
    """
    Read Loci-STREAM output files and convert to our format
    """
    # Loci-STREAM outputs to ./output directory with .dat files
    output_path = output_dir / 'output'
    
    # Try to find the latest solution file
    solution_files = list(output_path.glob(f'{case_name}*.dat'))
    
    if not solution_files:
        # Try Tecplot format
        solution_files = list(output_path.glob(f'{case_name}*.plt'))
    
    if not solution_files:
        raise FileNotFoundError(f"No solution files found in {output_path}")
    
    # Read the latest file
    latest_file = sorted(solution_files)[-1]
    print(f"Reading solution from: {latest_file}")
    
    # Parse based on file type
    if latest_file.suffix == '.dat':
        return parse_dat_file(latest_file)
    elif latest_file.suffix == '.plt':
        return parse_tecplot_file(latest_file)
    else:
        raise ValueError(f"Unknown file format: {latest_file.suffix}")


def parse_dat_file(filepath: Path) -> dict:
    """Parse Loci-STREAM .dat output file"""
    data = {
        'x': [], 'r': [],
        'pressure': [], 'temperature': [],
        'mach': [], 'velocity_x': [], 'velocity_r': [],
        'density': []
    }
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Skip header lines
    data_started = False
    for line in lines:
        line = line.strip()
        if not line or line.startswith('#') or line.startswith('VARIABLES'):
            continue
        if line.startswith('ZONE'):
            data_started = True
            continue
        
        if data_started:
            values = line.split()
            if len(values) >= 6:
                data['x'].append(float(values[0]))
                data['r'].append(float(values[1]))
                data['density'].append(float(values[2]))
                data['velocity_x'].append(float(values[3]))
                data['velocity_r'].append(float(values[4]))
                data['pressure'].append(float(values[5]))
                
                # Calculate derived quantities
                rho = float(values[2])
                u = float(values[3])
                v = float(values[4])
                p = float(values[5])
                
                gamma = 1.2
                c = np.sqrt(gamma * p / max(rho, 1e-10))
                mach = np.sqrt(u**2 + v**2) / c
                data['mach'].append(mach)
                
                # Temperature (assuming ideal gas)
                R = 332.0  # Approximate for combustion products
                T = p / (rho * R)
                data['temperature'].append(T)
    
    return data


def parse_tecplot_file(filepath: Path) -> dict:
    """Parse Tecplot .plt file"""
    # Simplified Tecplot ASCII parser
    data = {
        'x': [], 'r': [],
        'pressure': [], 'temperature': [],
        'mach': [], 'velocity_x': [], 'velocity_r': [],
        'density': []
    }
    
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find data section
    lines = content.split('\n')
    reading_data = False
    
    for line in lines:
        line = line.strip()
        if 'ZONE' in line:
            reading_data = True
            continue
        
        if reading_data and line:
            try:
                values = [float(x) for x in line.split()]
                if len(values) >= 2:
                    data['x'].append(values[0])
                    data['r'].append(values[1])
                    if len(values) >= 3:
                        data['pressure'].append(values[2])
                    if len(values) >= 4:
                        data['temperature'].append(values[3])
                    if len(values) >= 5:
                        data['mach'].append(values[4])
            except ValueError:
                continue
    
    return data


def read_openfoam_output(case_dir: Path) -> dict:
    """Read OpenFOAM results"""
    # Find latest time directory
    time_dirs = [d for d in case_dir.iterdir() if d.is_dir() and d.name.replace('.', '').isdigit()]
    
    if not time_dirs:
        raise FileNotFoundError("No time directories found in OpenFOAM case")
    
    latest_time = sorted(time_dirs, key=lambda x: float(x.name))[-1]
    print(f"Reading OpenFOAM results from: {latest_time}")
    
    data = {
        'x': [], 'r': [],
        'pressure': [], 'temperature': [],
        'mach': [], 'velocity_x': [], 'velocity_r': [],
        'density': []
    }
    
    # Read pressure
    p_file = latest_time / 'p'
    if p_file.exists():
        data['pressure'] = parse_openfoam_field(p_file)
    
    # Read velocity
    U_file = latest_time / 'U'
    if U_file.exists():
        U = parse_openfoam_vector_field(U_file)
        data['velocity_x'] = [u[0] for u in U]
        data['velocity_r'] = [u[1] for u in U]
    
    # Read temperature
    T_file = latest_time / 'T'
    if T_file.exists():
        data['temperature'] = parse_openfoam_field(T_file)
    
    # Read cell centers for coordinates
    mesh_file = case_dir / 'constant' / 'polyMesh' / 'cellCentres'
    if mesh_file.exists():
        centers = parse_openfoam_vector_field(mesh_file)
        data['x'] = [c[0] for c in centers]
        data['r'] = [c[1] for c in centers]
    
    return data


def parse_openfoam_field(filepath: Path) -> list:
    """Parse OpenFOAM scalar field file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Find the data between ( and )
    start = content.find('(')
    end = content.rfind(')')
    
    if start == -1 or end == -1:
        return []
    
    data_str = content[start+1:end]
    values = [float(x) for x in data_str.split() if x.replace('.', '').replace('-', '').replace('e', '').isdigit()]
    
    return values


def parse_openfoam_vector_field(filepath: Path) -> list:
    """Parse OpenFOAM vector field file"""
    with open(filepath, 'r') as f:
        content = f.read()
    
    vectors = []
    # Find vector entries (x y z)
    import re
    pattern = r'\(([^)]+)\)'
    matches = re.findall(pattern, content)
    
    for match in matches:
        try:
            components = [float(x) for x in match.split()]
            if len(components) == 3:
                vectors.append(components)
        except ValueError:
            continue
    
    return vectors


def read_python_solver_output(output_dir: Path) -> dict:
    """Read output from our Python CFD solver"""
    result_file = output_dir / 'cfd_result.json'
    
    if not result_file.exists():
        raise FileNotFoundError(f"Python solver result not found: {result_file}")
    
    with open(result_file, 'r') as f:
        return json.load(f)


def main():
    if len(sys.argv) < 4:
        print("Usage: postprocess.py <input_dir> <output_dir> <case_name>")
        sys.exit(1)
    
    input_dir = Path(sys.argv[1])
    output_dir = Path(sys.argv[2])
    case_name = sys.argv[3]
    
    print(f"Post-processing CFD results...")
    print(f"  Input: {input_dir}")
    print(f"  Output: {output_dir}")
    print(f"  Case: {case_name}")
    
    result = None
    
    # Try different sources in order of preference
    try:
        # 1. Try Loci-STREAM output
        result = read_loci_stream_output(input_dir, case_name)
        print("  Source: Loci-STREAM")
    except FileNotFoundError:
        pass
    
    if result is None:
        try:
            # 2. Try OpenFOAM output
            of_case = input_dir / 'openfoam_case'
            result = read_openfoam_output(of_case)
            print("  Source: OpenFOAM")
        except FileNotFoundError:
            pass
    
    if result is None:
        try:
            # 3. Try Python solver output
            result = read_python_solver_output(output_dir)
            print("  Source: Python solver")
        except FileNotFoundError:
            pass
    
    if result is None:
        print("ERROR: No CFD results found!")
        sys.exit(1)
    
    # Validate and fill missing fields
    required_fields = ['x', 'r', 'pressure', 'temperature', 'mach', 
                       'velocity_x', 'velocity_r', 'density']
    
    n_points = len(result.get('x', []))
    
    for field in required_fields:
        if field not in result or len(result[field]) != n_points:
            print(f"  Warning: Missing or incomplete field '{field}', filling with zeros")
            result[field] = [0.0] * n_points
    
    # Add metadata if missing
    if 'nx' not in result:
        result['nx'] = int(np.sqrt(n_points))
    if 'ny' not in result:
        result['ny'] = n_points // result['nx']
    if 'converged' not in result:
        result['converged'] = True
    if 'iterations' not in result:
        result['iterations'] = 0
    if 'residual_history' not in result:
        result['residual_history'] = []
    
    # Save final result
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / 'cfd_result.json'
    
    with open(output_file, 'w') as f:
        json.dump(result, f)
    
    print(f"  Saved: {output_file}")
    print(f"  Points: {n_points}")
    print(f"  Mach range: {min(result['mach']):.2f} - {max(result['mach']):.2f}")
    print("Post-processing complete!")


if __name__ == "__main__":
    main()
