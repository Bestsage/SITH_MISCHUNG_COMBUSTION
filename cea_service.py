"""
Micro-service Python UNIQUEMENT pour NASA CEA
Port: 8001
"""
from fastapi import FastAPI
from pydantic import BaseModel
from rocketcea.cea_obj import CEA_Obj

app = FastAPI(title="CEA Microservice")

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

if __name__ == "__main__":
    import uvicorn
    print("🔬 CEA Microservice starting on port 8001...")
    uvicorn.run(app, host="0.0.0.0", port=8001)
