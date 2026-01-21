
from rocketcea.cea_obj import CEA_Obj

def get_cea_data(pc_bar, mr, eps):
    # Dummy mock for quick test, or real if successful
    # print(f"CEA Mock Call: Pc={pc_bar}, MR={mr}")
    return {
        "isp": 300.0,
        "cstar": 1500.0,
        "t_comb": 3500.0,
        "gamma": 1.2,
        "mw": 24.0,
        "cp": 2000.0,
        "visc": 0.0001,
        "cond": 0.5,
        "prandtl": 0.7
    }

if __name__ == "__main__":
    import rocket_core
    import time
    
    print("🚀 Calling Rust 1D Solver...")
    
    geo = {
        "r_throat": 0.03, # 30mm
        "L_chamber": 0.15,
        "L_nozzle": 0.20,
        "n_channels": 48.0,
        "channel_width": 0.003,
        "channel_depth": 0.003,
        "wall_thickness": 0.001
    }
    
    cond = {
        "p_inlet": 60e5, # 60 bar
        "t_inlet": 300.0,
        "m_dot": 5.0, # kg/s total
        "pc": 50e5, # 50 bar
        "mr": 2.5,
        "k_wall": 340.0 # Copper
    }
    
    start = time.time()
    result = rocket_core.solve_1d_channel(
        get_cea_data,
        geo,
        cond
    )
    dt = time.time() - start
    
    print(f"✅ Solver Finished in {dt*1000:.2f} ms")
    print(f"   Steps: {len(result['x'])}")
    print(f"   Max T_wall: {max(result['t_wall']):.1f} K")
    print(f"   Outlet T_coolant: {result['t_out']:.1f} K")
    print(f"   Outlet P_coolant: {result['p_out']/1e5:.2f} bar")
    
    # === OPTIMIZER TEST ===
    print("\n🧬 Testing Rust Genetic Optimizer...")
    start_opt = time.time()
    
    # 3 Vars: dim=3
    bounds_min = [0.0, 0.0, 0.0]
    bounds_max = [10.0, 10.0, 10.0]
    
    best_design = rocket_core.run_optimization(
        get_cea_data,
        geo, # Template
        cond, # Template
        bounds_min,
        bounds_max,
        20, # Pop size
        10  # Generations
    )
    dt_opt = time.time() - start_opt
    print(f"✅ Optimizer Finished in {dt_opt*1000:.2f} ms")
    print(f"   Best Design Vector: {best_design}")

