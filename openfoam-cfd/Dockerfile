# OpenFOAM CFD Solver Container
# Optimized for rocket nozzle compressible flow simulations

FROM opencfd/openfoam-default:2312

LABEL maintainer="SITH Combustion Project"
LABEL description="OpenFOAM CFD solver for rocket nozzle simulations"

USER root
ENV DEBIAN_FRONTEND=noninteractive

# Install Python and dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-numpy \
    python3-scipy \
    python3-matplotlib \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages for mesh generation and API
RUN pip3 install --no-cache-dir \
    fastapi \
    uvicorn \
    meshio \
    gmsh \
    numpy \
    scipy \
    matplotlib \
    aiofiles \
    httpx

# Create working directories
RUN mkdir -p /app/cases /app/results /app/scripts /app/api

# Copy scripts
COPY scripts/ /app/scripts/
COPY api/ /app/api/
RUN chmod +x /app/scripts/*.py /app/scripts/*.sh 2>/dev/null || true

WORKDIR /app

# Expose API port
EXPOSE 8001

# Override default OpenFOAM entrypoint
ENTRYPOINT ["/bin/bash", "-c"]

# Source OpenFOAM and run API server
CMD ["source /usr/lib/openfoam/openfoam2312/etc/bashrc && python3 /app/api/server.py"]
