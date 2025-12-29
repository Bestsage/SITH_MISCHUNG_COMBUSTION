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

class CEAResponse(BaseModel):
    isp_vac: float
    isp_sl: float
    c_star: float
    t_chamber: float
    gamma: float
    mw: float

@app.post("/cea", response_model=CEAResponse)
def calculate_cea(req: CEARequest):
    """Run NASA CEA calculation"""
    cea = CEA_Obj(oxName=req.oxidizer, fuelName=req.fuel)
    
    isp_vac, cstar, tc = cea.get_IvacCstrTc(Pc=req.pc, MR=req.of_ratio, eps=req.expansion_ratio)
    isp_sl = cea.get_Isp(Pc=req.pc, MR=req.of_ratio, eps=req.expansion_ratio)
    gamma = cea.get_Throat_MolWt_gamma(Pc=req.pc, MR=req.of_ratio, eps=req.expansion_ratio)[1]
    mw = cea.get_Throat_MolWt_gamma(Pc=req.pc, MR=req.of_ratio, eps=req.expansion_ratio)[0]
    
    return CEAResponse(
        isp_vac=isp_vac,
        isp_sl=isp_sl,
        c_star=cstar,
        t_chamber=tc,
        gamma=gamma,
        mw=mw
    )

@app.get("/propellants")
def get_propellants():
    """Get all available fuel and oxidizer cards from RocketCEA"""
    try:
        from rocketcea.blends import fuelCards, oxCards
        
        fuels = []
        for name in fuelCards.keys():
            try:
                card = fuelCards[name]
                # Parse basic info from card
                fuels.append({
                    "name": name,
                    "type": "fuel",
                    "card": str(card)[:200] if card else ""
                })
            except:
                fuels.append({"name": name, "type": "fuel", "card": ""})
        
        oxidizers = []
        for name in oxCards.keys():
            try:
                card = oxCards[name]
                oxidizers.append({
                    "name": name,
                    "type": "oxidizer",
                    "card": str(card)[:200] if card else ""
                })
            except:
                oxidizers.append({"name": name, "type": "oxidizer", "card": ""})
        
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

