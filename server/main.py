
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import sys
import os

# Allow imports from project root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(
    title="Rocket Design API",
    description="Backend for Rocket Motor Design Plotter v2.0",
    version="2.0.0"
)

# CORS (Allow frontend access)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import data
from data.materials import get_all_materials, get_material

@app.get("/")
def read_root():
    return {"status": "online", "message": "Rocket Design API is running 🚀"}

@app.get("/config")
def get_config():
    """Returns application configuration parameters."""
    return {"theme": "dark"}

# === MATERIALS ENDPOINTS ===
@app.get("/api/materials")
def list_materials():
    """Get all available materials"""
    return {"materials": get_all_materials()}

@app.get("/api/materials/{material_name}")
def get_material_info(material_name: str):
    """Get specific material properties"""
    mat = get_material(material_name)
    if not mat:
        raise HTTPException(status_code=404, detail="Material not found")
    return mat

# === CEA ENDPOINT ===
@app.post("/api/cea/calculate")
def calculate_cea(data: dict):
    """Run NASA CEA calculation"""
    try:
        from rocketcea.cea_obj import CEA_Obj
        
        fuel = data.get("fuel", "RP-1")
        oxidizer = data.get("oxidizer", "LOX")
        of_ratio = data.get("of_ratio", 2.5)
        pc = data.get("pc", 50.0)  # bar
        expansion_ratio = data.get("expansion_ratio", 40.0)
        
        cea = CEA_Obj(oxName=oxidizer, fuelName=fuel)
        
        # Get performance at chamber conditions
        isp_vac, cstar, tc = cea.get_IvacCstrTc(Pc=pc, MR=of_ratio, eps=expansion_ratio)
        isp_sl = cea.get_Isp(Pc=pc, MR=of_ratio, eps=expansion_ratio)
        
        # Get additional properties
        gamma = cea.get_Throat_MolWt_gamma(Pc=pc, MR=of_ratio, eps=expansion_ratio)[1]
        mw = cea.get_Throat_MolWt_gamma(Pc=pc, MR=of_ratio, eps=expansion_ratio)[0]
        
        return {
            "status": "success",
            "results": {
                "isp_vac": isp_vac,
                "isp_sl": isp_sl,
                "c_star": cstar,
                "t_chamber": tc,
                "gamma": gamma,
                "mw": mw,
                "of_ratio": of_ratio,
                "pc": pc
            }
        }
    except Exception as e:
        return {"status": "error", "message": str(e)}

# === SOLVER ENDPOINT (existing) ===
@app.post("/api/solve")
def run_solver(data: dict):
    """
    Executes the Rust 1D Solver.
    Body should contain 'geometry' and 'conditions' dicts.
    """
    try:
        import rocket_core
        from cea_adapter import get_cea_data
        
        geo = data.get("geometry", {
            "r_throat": 0.03,
            "L_chamber": 0.15, 
            "L_nozzle": 0.20,
            "n_channels": 48.0,
            "channel_width": 0.003,
            "channel_depth": 0.003,
            "wall_thickness": 0.001
        })
        
        cond = data.get("conditions", {
            "p_inlet": 60e5,
            "t_inlet": 300.0,
            "m_dot": 5.0,
            "pc": 50e5,
            "mr": 2.5,
            "k_wall": 340.0
        })

        result = rocket_core.solve_1d_channel(get_cea_data, geo, cond)
        return {"status": "success", "data": result}
        
    except ImportError:
        return {"status": "error", "message": "Rocket Core not found"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# === FULL CALCULATION ENDPOINT ===
@app.post("/api/calculate/full")
def calculate_full(data: dict):
    """
    Complete calculation pipeline:
    1. Run CEA
    2. Generate geometry
    3. Run thermal solver
    4. Calculate performance
    """
    try:
        # Extract inputs
        geometry = data.get("geometry", {})
        cea_params = data.get("cea", {})
        cooling = data.get("cooling", {})
        material_name = data.get("material", "GlidCop AL-15")
        
        # Get material properties
        material = get_material(material_name)
        if not material:
            return {"status": "error", "message": "Invalid material"}
        
        # Run CEA
        cea_result = calculate_cea(cea_params)
        if cea_result.get("status") != "success":
            return cea_result
        
        # Prepare solver inputs
        geo = {
            "r_throat": geometry.get("r_throat", 0.03),
            "L_chamber": geometry.get("L_chamber", 0.15),
            "L_nozzle": geometry.get("L_nozzle", 0.20),
            "n_channels": cooling.get("n_channels", 48.0),
            "channel_width": cooling.get("channel_width", 0.003),
            "channel_depth": cooling.get("channel_depth", 0.003),
            "wall_thickness": cooling.get("wall_thickness", 0.001)
        }
        
        cond = {
            "p_inlet": cooling.get("p_inlet", 60e5),
            "t_inlet": cooling.get("t_inlet", 300.0),
            "m_dot": cooling.get("m_dot", 5.0),
            "pc": cea_params.get("pc", 50.0) * 1e5,  # bar to Pa
            "mr": cea_params.get("of_ratio", 2.5),
            "k_wall": material["k"]
        }
        
        # Run solver
        solver_result = run_solver({"geometry": geo, "conditions": cond})
        
        return {
            "status": "success",
            "cea": cea_result["results"],
            "thermal": solver_result.get("data"),
            "material": material,
            "geometry": geo
        }
        
    except Exception as e:
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)


