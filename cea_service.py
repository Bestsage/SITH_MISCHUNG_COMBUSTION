"""
Micro-service Python UNIQUEMENT pour NASA CEA
Port: 8001
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rocketcea.cea_obj import CEA_Obj
from typing import Optional

app = FastAPI(title="CEA Microservice")

# Add CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class CEARequest(BaseModel):
    fuel: str = "RP-1"
    oxidizer: str = "LOX"
    of_ratio: float = 2.5
    pc: float = 50.0  # bar
    expansion_ratio: float = 40.0
    pe: float = 1.013  # bar - exit pressure for expansion ratio calculation
    fac_cr: float = 0.0  # Finite Area Combustor contraction ratio (0 = infinite)

class CEAResponse(BaseModel):
    isp_vac: float
    isp_sl: float
    c_star: float
    t_chamber: float
    gamma: float
    mw: float
    eps_from_pe: float  # Expansion ratio calculated from exit pressure

@app.post("/cea", response_model=CEAResponse)
def calculate_cea(req: CEARequest):
    """Run NASA CEA calculation"""
    cea = CEA_Obj(oxName=req.oxidizer, fuelName=req.fuel)
    
    # Use finite area combustor if contraction ratio specified
    if req.fac_cr > 1.0:
        cea = CEA_Obj(oxName=req.oxidizer, fuelName=req.fuel, fac_CR=req.fac_cr)
    
    isp_vac, cstar, tc = cea.get_IvacCstrTc(Pc=req.pc, MR=req.of_ratio, eps=req.expansion_ratio)
    isp_sl = cea.get_Isp(Pc=req.pc, MR=req.of_ratio, eps=req.expansion_ratio)
    gamma = cea.get_Throat_MolWt_gamma(Pc=req.pc, MR=req.of_ratio, eps=req.expansion_ratio)[1]
    mw = cea.get_Throat_MolWt_gamma(Pc=req.pc, MR=req.of_ratio, eps=req.expansion_ratio)[0]
    
    # Calculate correct expansion ratio from exit pressure
    # This is the key fix - use CEA's proper isentropic calculation
    pc_over_pe = req.pc / req.pe
    try:
        eps_from_pe = cea.get_eps_at_PcOvPe(Pc=req.pc, MR=req.of_ratio, PcOvPe=pc_over_pe)
    except:
        # Fallback if method not available
        eps_from_pe = req.expansion_ratio
    
    return CEAResponse(
        isp_vac=isp_vac,
        isp_sl=isp_sl,
        c_star=cstar,
        t_chamber=tc,
        gamma=gamma,
        mw=mw,
        eps_from_pe=eps_from_pe
    )

@app.get("/propellants")
def get_propellants():
    """Get all available fuel and oxidizer cards from RocketCEA + extended lists"""
    try:
        from rocketcea.blends import fuelCards, oxCards
        
        # Extended fuels not in blends but supported by CEA
        extra_fuels = [
            "RP-1", "JP-4", "JP-5", "JP-10", "Jet-A", "Biodiesel",
            "C6H6", "C7H8", "C8H18", "C10H22", "C12H26",
            "B5H9", "B10H14", "Al", "Mg", "Li", "Be",
            "PBAN", "AN", "HMX", "RDX", "Syntin", "ALICE",
            "Aerozine-50", "Diborane", "Pentaborane", "Decaborane"
        ]
        
        # Extended oxidizers not in blends but supported by CEA
        extra_oxidizers = [
            "FLOX70", "FLOX80", "MON-1", "MON-10", "NTO", 
            "RFNA", "WFNA", "Ozone", "O3", "Oxygen", "Fluorine",
            "AK-20", "AK-27"
        ]
        
        # Combine blends + extras, remove duplicates
        all_fuel_names = set(fuelCards.keys()) | set(extra_fuels)
        all_ox_names = set(oxCards.keys()) | set(extra_oxidizers)
        
        fuels = []
        for name in all_fuel_names:
            try:
                card = fuelCards.get(name, "")
                fuels.append({
                    "name": name,
                    "type": "fuel",
                    "card": str(card)[:200] if card else "",
                    "source": "blends" if name in fuelCards else "cea_standard"
                })
            except:
                fuels.append({"name": name, "type": "fuel", "card": "", "source": "cea_standard"})
        
        oxidizers = []
        for name in all_ox_names:
            try:
                card = oxCards.get(name, "")
                oxidizers.append({
                    "name": name,
                    "type": "oxidizer",
                    "card": str(card)[:200] if card else "",
                    "source": "blends" if name in oxCards else "cea_standard"
                })
            except:
                oxidizers.append({"name": name, "type": "oxidizer", "card": "", "source": "cea_standard"})
        
        return {
            "fuels": sorted(fuels, key=lambda x: x["name"]),
            "oxidizers": sorted(oxidizers, key=lambda x: x["name"]),
            "fuel_count": len(fuels),
            "ox_count": len(oxidizers)
        }
    except Exception as e:
        return {"error": str(e), "fuels": [], "oxidizers": []}

@app.get("/health")
def health():
    return {"status": "ok", "service": "cea"}

if __name__ == "__main__":
    import uvicorn
    print("🔬 CEA Microservice starting on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)

