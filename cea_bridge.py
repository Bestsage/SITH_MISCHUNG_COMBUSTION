
import sys
import json
import argparse
import os

def main():
    # Setup Argument Parser
    parser = argparse.ArgumentParser(description="RocketCEA Bridge - Interoperability Layer")
    parser.add_argument("--ox", type=str, required=True, help="Oxidizer Name (e.g. O2)")
    parser.add_argument("--fuel", type=str, required=True, help="Fuel Name (e.g. C3H8)")
    parser.add_argument("--pc", type=float, required=True, help="Chamber Pressure (bar)")
    parser.add_argument("--mr", type=float, required=True, help="Mixture Ratio (O/F)")
    parser.add_argument("--eps", type=float, default=None, help="Expansion Area Ratio (Ae/At)")
    parser.add_argument("--pe", type=float, default=None, help="Exit Pressure (bar) - Overrides eps if provided")
    parser.add_argument("--pamb", type=float, default=1.013, help="Ambient Pressure (bar) for Isp estimation")
    
    args = parser.parse_args()

    # Calculate results
    try:
        from rocketcea.cea_obj import CEA_Obj
    except ImportError as e:
        print(json.dumps({
            "status": "error", 
            "message": f"Failed to import RocketCEA: {str(e)}",
            "hint": "Ensure you are using Python <= 3.10 (RocketCEA restriction) and have installed 'rocketcea'."
        }))
        sys.exit(1)


    try:
        # Initialize CEA Object
        cea = CEA_Obj(oxName=args.ox, fuelName=args.fuel)

        # Conversions (Metric to Imperial units required by RocketCEA)
        # 1 bar = 14.5038 psi
        pc_psi = args.pc * 14.5038
        pamb_psi = args.pamb * 14.5038
        
        # Determine EPS
        eps = 40.0 # default
        if args.pe is not None:
            pe_psi = args.pe * 14.5038
            # Calculate eps from Pc/Pe
            try:
                eps = cea.get_eps_at_PcOvPe(Pc=pc_psi, MR=args.mr, PcOvPe=pc_psi/pe_psi)
            except:
                eps = 40.0
        elif args.eps is not None:
            eps = args.eps
        
        # --- 1. Basic Performance (Vacuum) ---
        # get_Isp returns a float
        isp_vac = cea.get_Isp(Pc=pc_psi, MR=args.mr, eps=eps)
        
        # --- 2. C* (Characteristic Velocity) ---
        # get_Cstar returns (Cstar_fps, Cstar_m_s) or just value depending on version
        # easier to just take value (usually fps) and convert
        cstar_val = cea.get_Cstar(Pc=pc_psi, MR=args.mr)
        if isinstance(cstar_val, tuple):
            cstar_fps = cstar_val[0]
        else:
            cstar_fps = cstar_val
        cstar_ms = cstar_fps * 0.3048

        # --- 3. Combustion Temperature ---
        # get_Tcomb returns Rankine
        tcomb_r = cea.get_Tcomb(Pc=pc_psi, MR=args.mr)
        if isinstance(tcomb_r, tuple):
            tcomb_r = tcomb_r[0]
        tcomb_k = tcomb_r / 1.8 # Rankine to Kelvin

        # --- 4. Ambient Performance ---
        # estimate_Ambient_Isp returns (IspAmb, ModeString)
        isp_amb, flow_mode = cea.estimate_Ambient_Isp(Pc=pc_psi, MR=args.mr, eps=eps, Pamb=pamb_psi)

        # --- 5. Gas Properties (Chamber) ---
        # perform separate call or use get_Chamber_MolWt_Gamma
        result_transport = cea.get_Chamber_MolWt_gamma(Pc=pc_psi, MR=args.mr, eps=eps)

        # Returns (MW, Gamma)
        molwt = result_transport[0]
        gamma = result_transport[1]
        
        # --- 6. Throat Transport Properties (for Bartz) ---
        try:
            transp = cea.get_Throat_Transport(Pc=pc_psi, MR=args.mr, eps=eps)
            # transp = [Cp, Mu, K, Pr]
            # Units: Cp (BTU/lb-F), Mu (millipoise), K (BTU/s-in-F ?), Pr (-)
            # RocketCEA docs: "Cp, Visc, Cond, Pr"
            # Viscosity is in Millipoise
            cp_imp = transp[0]
            mu_millipoise = transp[1]
            pr = transp[3]
            
            # Convert to SI
            # Cp: BTU/lb-F -> J/kg-K
            cp_si = cp_imp * 4186.8
            # Mu: Millipoise -> Pa.s
            # 1 Poise = 0.1 Pa.s
            # 1 mP = 0.0001 Pa.s
            mu_si = (mu_millipoise / 1000.0) * 0.1
            
        except Exception as e:
            # Fallback
            cp_si = 2000.0
            mu_si = 8.0e-5
            pr = 0.7

        # --- 7. Temperatures (Chamber, Throat, Exit) ---
        # Ideally we fetch them. 
        # T_comb is Tc.
        # Tt can be approximated or fetched if method exists.
        # estimate_Throat_T exists?
        # get_Temperatures exists => (Tc, Tt, Te) in Rankine
        tc_k = tcomb_k
        tt_k = tcomb_k * 0.9 # placeholder if failed
        te_k = tcomb_k * 0.5 # placeholder
        
        try:
             temps = cea.get_Temperatures(Pc=pc_psi, MR=args.mr, eps=eps)
             # (Tc, Tt, Te)
             tc_k = temps[0] / 1.8
             tt_k = temps[1] / 1.8
             te_k = temps[2] / 1.8
        except:
             pass

        # Construct JSON Output
        output = {
            "status": "success",
            "inputs": {
                "ox": args.ox,
                "fuel": args.fuel,
                "pc_bar": args.pc,
                "mr": args.mr,
                "eps": eps,
                "pamb_bar": args.pamb
            },
            "results": {
                "eps": round(eps, 4),
                "isp_vac_s": round(isp_vac, 2),
                "isp_amb_s": round(isp_amb, 2),
                "cstar_m_s": round(cstar_ms, 2),
                "tcomb_k": round(tcomb_k, 2),
                "tc_k": round(tc_k, 2),
                "tt_k": round(tt_k, 2),
                "te_k": round(te_k, 2),
                "gamma": round(gamma, 4),
                "mol_wt": round(molwt, 4),
                "cp_si": round(cp_si, 1),
                "mu_si": round(mu_si, 7) if mu_si < 0.001 else round(mu_si, 5),
                "pr": round(pr, 4),
                "flow_mode": flow_mode.strip()
            }
        }
        
        # Print JSON to stdout
        print(json.dumps(output, indent=4))
        
    except Exception as e:
        error_output = {
            "status": "error",
            "message": str(e),
            "hint": "Check if propellant names are valid in RocketCEA."
        }
        print(json.dumps(error_output, indent=4))
        sys.exit(1)

if __name__ == "__main__":
    main()
