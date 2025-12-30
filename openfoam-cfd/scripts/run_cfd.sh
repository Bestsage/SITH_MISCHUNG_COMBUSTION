#!/bin/bash
# Loci-STREAM CFD Solver Wrapper
# Runs mesh generation, solver, and post-processing

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INPUT_DIR="${INPUT_DIR:-/data/input}"
OUTPUT_DIR="${OUTPUT_DIR:-/data/output}"
CASE_NAME="${CASE_NAME:-nozzle}"
NUM_PROCS="${NUM_PROCS:-4}"

usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --params FILE     JSON file with simulation parameters"
    echo "  --case NAME       Case name (default: nozzle)"
    echo "  --procs N         Number of MPI processes (default: 4)"
    echo "  --mesh-only       Only generate mesh, don't run solver"
    echo "  --help            Show this help message"
    echo ""
    echo "Environment variables:"
    echo "  INPUT_DIR         Input directory (default: /data/input)"
    echo "  OUTPUT_DIR        Output directory (default: /data/output)"
}

PARAMS_FILE=""
MESH_ONLY=0

while [[ $# -gt 0 ]]; do
    case $1 in
        --params)
            PARAMS_FILE="$2"
            shift 2
            ;;
        --case)
            CASE_NAME="$2"
            shift 2
            ;;
        --procs)
            NUM_PROCS="$2"
            shift 2
            ;;
        --mesh-only)
            MESH_ONLY=1
            shift
            ;;
        --help)
            usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

if [[ -z "$PARAMS_FILE" ]]; then
    echo "Error: --params is required"
    usage
    exit 1
fi

echo "=========================================="
echo "Loci-STREAM CFD Solver"
echo "=========================================="
echo "Case: $CASE_NAME"
echo "Params: $PARAMS_FILE"
echo "Processes: $NUM_PROCS"
echo ""

# Create directories
mkdir -p "$INPUT_DIR" "$OUTPUT_DIR"

# Step 1: Generate mesh
echo "[1/4] Generating mesh..."
python3 "$SCRIPT_DIR/generate_mesh.py" "$PARAMS_FILE" "$INPUT_DIR"

if [[ $MESH_ONLY -eq 1 ]]; then
    echo "Mesh generation complete (--mesh-only specified)"
    exit 0
fi

# Step 2: Convert UGRID to VOG (if Loci tools available)
echo "[2/4] Converting mesh to VOG format..."
cd "$INPUT_DIR"

if command -v ugrid2vog &> /dev/null; then
    ugrid2vog -in "$CASE_NAME"
    echo "  Created: $CASE_NAME.vog"
else
    echo "  Warning: ugrid2vog not found, using OpenFOAM fallback"
    # Create OpenFOAM mesh instead
    python3 "$SCRIPT_DIR/convert_to_openfoam.py" "$INPUT_DIR/${CASE_NAME}_mesh.json" "$INPUT_DIR/openfoam_case"
fi

# Step 3: Run solver
echo "[3/4] Running CFD solver..."

if command -v stream &> /dev/null; then
    # Run Loci-STREAM
    echo "  Using Loci-STREAM solver"
    cd "$INPUT_DIR"
    mpirun -np $NUM_PROCS stream -q solution "$CASE_NAME" 2>&1 | tee "$OUTPUT_DIR/solver.log"
    
elif [[ -d "/opt/openfoam" ]] || command -v simpleFoam &> /dev/null; then
    # Fallback to OpenFOAM
    echo "  Using OpenFOAM solver"
    source /opt/openfoam*/etc/bashrc 2>/dev/null || true
    
    cd "$INPUT_DIR/openfoam_case"
    
    # Run rhoCentralFoam for compressible flow
    if command -v rhoCentralFoam &> /dev/null; then
        mpirun -np $NUM_PROCS rhoCentralFoam -parallel 2>&1 | tee "$OUTPUT_DIR/solver.log"
    else
        echo "  Running simpleFoam (incompressible approximation)"
        simpleFoam 2>&1 | tee "$OUTPUT_DIR/solver.log"
    fi
else
    # Pure Python solver fallback
    echo "  Using Python CFD solver (simplified)"
    python3 "$SCRIPT_DIR/python_cfd_solver.py" "$PARAMS_FILE" "$OUTPUT_DIR"
fi

# Step 4: Post-process results
echo "[4/4] Post-processing results..."
python3 "$SCRIPT_DIR/postprocess.py" "$INPUT_DIR" "$OUTPUT_DIR" "$CASE_NAME"

echo ""
echo "=========================================="
echo "Simulation complete!"
echo "Results in: $OUTPUT_DIR"
echo "=========================================="
