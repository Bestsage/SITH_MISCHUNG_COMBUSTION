from pydantic import BaseModel
from typing import Optional, List, Dict

# === GEOMETRY ===
class GeometryInput(BaseModel):
    # Throat
    r_throat: float  # m
    
    # Chamber
    L_chamber: float  # m
    r_chamber: Optional[float] = None  # m, if None calculate from contraction ratio
    contraction_ratio: Optional[float] = 3.0
    
    # Nozzle
    L_nozzle: float  # m
    expansion_ratio: float = 40.0
    nozzle_type: str = "conical"  # "conical" or "bell"
    theta_conv: float = 30.0  # deg
    theta_div: float = 15.0  # deg
    
    # Cooling
    n_channels: int = 48
    channel_width: float = 0.003  # m
    channel_depth: float = 0.003  # m
    wall_thickness: float = 0.001  # m

# === MATERIALS ===
class Material(BaseModel):
    name: str
    k: float  # W/mK - thermal conductivity
    T_melt: float  # K
    T_max: float  # K
    rho: float  # kg/m³
    E: float  # GPa - Young's modulus
    nu: float  # Poisson's ratio
    alpha: float  # 1e-6/K - thermal expansion
    sigma_y: float  # MPa - yield strength
    sigma_uts: float  # MPa - ultimate tensile strength
    color: str  # hex color for visualization

# === CEA ===
class CEAInput(BaseModel):
    fuel: str = "RP-1"
    oxidizer: str = "LOX"
    of_ratio: float = 2.5
    pc: float = 50.0  # bar
    pe: Optional[float] = None  # bar, if None use expansion ratio
    expansion_ratio: Optional[float] = None

class CEAResult(BaseModel):
    isp: float  # s
    c_star: float  # m/s
    cf: float
    t_chamber: float  # K
    t_throat: float  # K
    gamma: float
    mw: float  # g/mol
    
# === CONDITIONS ===
class OperatingConditions(BaseModel):
    pc: float  # Pa
    mr: float  # mixture ratio
    p_inlet: float  # Pa - coolant inlet pressure
    t_inlet: float  # K - coolant inlet temperature
    m_dot: float  # kg/s - total coolant mass flow
    k_wall: float  # W/mK - wall thermal conductivity

# === RESULTS ===
class SolverResult(BaseModel):
    x: List[float]  # axial positions
    t_wall: List[float]  # wall temperatures
    t_coolant: List[float]  # coolant temperatures
    p_coolant: List[float]  # coolant pressures
    t_out: float  # outlet temperature
    p_out: float  # outlet pressure
    max_t_wall: float
    
class PerformanceMetrics(BaseModel):
    isp_vac: float
    isp_sl: float
    thrust_vac: float
    thrust_sl: float
    c_star: float
    cf_vac: float
    cf_sl: float
