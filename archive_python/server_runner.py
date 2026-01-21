
import threading
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import rocket_core
from cea_adapter import get_cea_data

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/solve")
def solve_endpoint(data: dict):
    geo = data.get('geometry')
    cond = data.get('conditions')
    try:
        res = rocket_core.solve_1d_channel(get_cea_data, geo, cond)
        return res
    except Exception as e:
        return {"error": str(e)}

def start_server():
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    start_server()
