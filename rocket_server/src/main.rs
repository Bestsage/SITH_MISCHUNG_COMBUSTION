use axum::{
    routing::{get, post},
    http::{StatusCode, Method},
    Json, Router,
};
use tower_http::cors::{CorsLayer, Any};
use serde::{Deserialize, Serialize};
use std::net::SocketAddr;

mod materials;
mod cea_client;
mod geometry;
mod motor_definition;

use geometry::{GeometryParams, GeometryProfile};
use rocket_server::{CEARequest, CEAResponse};
use motor_definition::{MotorDefinition, CalculationResults};

// === SOLVER REQUEST ===
#[derive(Debug, Serialize, Deserialize)]
pub struct SolverRequest {
    pub geometry: GeometryInput,
    pub conditions: ConditionsInput,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GeometryInput {
    pub r_throat: f64,
    pub l_chamber: f64,
    pub l_nozzle: f64,
    pub n_channels: f64,
    pub channel_width: f64,
    pub channel_depth: f64,
    pub wall_thickness: f64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ConditionsInput {
    pub p_inlet: f64,
    pub t_inlet: f64,
    pub m_dot: f64,
    pub pc: f64,
    pub mr: f64,
    pub k_wall: f64,
}

// === HANDLERS ===
async fn root() -> &'static str {
    "🚀 Rocket Design API (Rust) - Online"
}

async fn get_materials() -> Json<serde_json::Value> {
    Json(serde_json::json!({
        "materials": materials::get_materials()
    }))
}

async fn calculate_cea(Json(payload): Json<CEARequest>) -> Result<Json<CEAResponse>, StatusCode> {
    match cea_client::call_cea_service(payload).await {
        Ok(result) => Ok(Json(result)),
        Err(_) => Err(StatusCode::INTERNAL_SERVER_ERROR),
    }
}

async fn run_solver(Json(payload): Json<SolverRequest>) -> Result<Json<serde_json::Value>, StatusCode> {
    // Extract parameters from payload
    let geom = &payload.geometry;
    let cond = &payload.conditions;
    
    // Geometry parameters
    let r_throat = geom.r_throat;  // m
    let l_total = geom.l_chamber + geom.l_nozzle;  // m
    let n_channels = geom.n_channels as usize;
    let w_channel = geom.channel_width;  // m
    let h_channel = geom.channel_depth;  // m
    let e_wall = geom.wall_thickness;  // m
    
    // Conditions
    let p_inlet = cond.p_inlet;  // Pa
    let t_inlet = cond.t_inlet;  // K
    let m_dot_total = cond.m_dot;  // kg/s coolant
    let pc = cond.pc;  // Pa chamber pressure
    let k_wall = cond.k_wall;  // W/mK wall conductivity
    
    // Coolant properties (approximate for RP-1/kerosene)
    let rho_cool = 800.0;  // kg/m³
    let cp_cool = 2100.0;  // J/kgK
    let mu_cool = 0.001;  // Pa.s
    let k_cool = 0.12;  // W/mK
    let pr_cool = cp_cool * mu_cool / k_cool;
    
    // Channel hydraulic diameter
    let a_channel = w_channel * h_channel;
    let p_wet = 2.0 * (w_channel + h_channel);
    let d_h = 4.0 * a_channel / p_wet;
    
    // Velocity per channel
    let m_dot_channel = m_dot_total / n_channels as f64;
    let v_cool = m_dot_channel / (rho_cool * a_channel);
    
    // Reynolds number
    let re = rho_cool * v_cool * d_h / mu_cool;
    
    // Friction factor (Haaland approximation)
    let roughness = 1e-6;  // m (smooth)
    let f = if re > 2300.0 {
        let a = -1.8 * ((6.9 / re) + (roughness / d_h / 3.7).powf(1.11)).ln() / 10.0_f64.ln();
        (1.0 / a).powi(2)
    } else {
        64.0 / re
    };
    
    // Gnielinski Nusselt number
    let nu = if re > 2300.0 {
        ((f / 8.0) * (re - 1000.0) * pr_cool) / 
        (1.0 + 12.7 * (f / 8.0).sqrt() * (pr_cool.powf(2.0/3.0) - 1.0))
    } else {
        3.66  // Laminar
    };
    
    // Coolant-side heat transfer coefficient
    let h_cool = nu * k_cool / d_h;
    
    // Bartz correlation for gas-side heat transfer (simplified)
    // hg = 0.026/Dt^0.2 * (mu^0.2 * Cp / Pr^0.6) * (Pc/cstar)^0.8 * (At/A)^0.9 * sigma
    let d_throat = 2.0 * r_throat;
    let gamma = 1.2;  // Typical for combustion products
    let t_chamber = 3500.0;  // K (from CEA or assumed)
    let c_star = 1700.0;  // m/s (typical)
    
    // Gas properties at chamber conditions (approximate)
    let mu_gas: f64 = 8e-5;  // Pa.s
    let cp_gas: f64 = 2000.0;  // J/kgK
    let pr_gas: f64 = 0.72;
    
    let bartz_base = 0.026_f64 / d_throat.powf(0.2) * 
                     (mu_gas.powf(0.2) * cp_gas / pr_gas.powf(0.6)) *
                     (pc / c_star).powf(0.8);
    
    // Discretize along the channel
    let n_points = 50;
    let dx = l_total / n_points as f64;
    
    let mut x_arr = Vec::with_capacity(n_points);
    let mut t_wall_arr = Vec::with_capacity(n_points);
    let mut t_coolant_arr = Vec::with_capacity(n_points);
    let mut p_coolant_arr = Vec::with_capacity(n_points);
    let mut q_flux_arr = Vec::with_capacity(n_points);
    
    let mut t_cool = t_inlet;
    let mut p_cool = p_inlet;
    
    for i in 0..n_points {
        let x = i as f64 * dx;
        x_arr.push(x);
        
        // Local area ratio (simplified: throat at l_chamber position)
        let throat_pos = geom.l_chamber;
        let area_ratio = if x < throat_pos {
            // Convergent: linear from 3.0 to 1.0
            3.0 - 2.0 * x / throat_pos
        } else {
            // Divergent: linear from 1.0 to expansion ratio
            1.0 + 39.0 * (x - throat_pos) / geom.l_nozzle
        };
        let area_ratio = area_ratio.max(1.0);
        
        // Local gas-side heat transfer coefficient
        let h_gas = bartz_base * (1.0 / area_ratio).powf(0.9);
        
        // Adiabatic wall temperature (recovery factor ~0.9)
        let local_gamma_factor = 1.0 + 0.5 * (gamma - 1.0);
        let t_aw = t_chamber / local_gamma_factor;  // Simplified
        
        // Solve 1D thermal resistance network
        // q = hg*(Taw - Twh) = k/e*(Twh - Twc) = hc*(Twc - Tcool)
        let r_gas = 1.0 / h_gas;
        let r_wall = e_wall / k_wall;
        let r_cool = 1.0 / h_cool;
        let r_total = r_gas + r_wall + r_cool;
        
        let q_flux = (t_aw - t_cool) / r_total;
        let t_wall_hot = t_aw - q_flux * r_gas;
        
        q_flux_arr.push(q_flux / 1e6);  // MW/m²
        t_wall_arr.push(t_wall_hot);
        t_coolant_arr.push(t_cool);
        p_coolant_arr.push(p_cool);
        
        // Update coolant temperature along channel
        // Perimeter cooled per unit length (assume full circumference)
        let r_local = r_throat * area_ratio.sqrt();
        let perimeter = 2.0 * std::f64::consts::PI * r_local;
        let q_absorbed = q_flux * perimeter * dx;
        t_cool += q_absorbed / (m_dot_total * cp_cool);
        
        // Pressure drop (Darcy-Weisbach)
        let dp = f * (dx / d_h) * (rho_cool * v_cool.powi(2) / 2.0);
        p_cool -= dp;
    }
    
    let max_t_wall = t_wall_arr.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    let max_q_flux = q_flux_arr.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    
    Ok(Json(serde_json::json!({
        "status": "success",
        "data": {
            "x": x_arr,
            "t_wall": t_wall_arr,
            "t_coolant": t_coolant_arr,
            "p_coolant": p_coolant_arr,
            "q_flux": q_flux_arr,
            "t_out": t_cool,
            "p_out": p_cool,
            "max_t_wall": max_t_wall,
            "max_q_flux": max_q_flux,
            "reynolds": re,
            "h_coolant": h_cool,
            "delta_p": (p_inlet - p_cool) / 1e5
        }
    })))
}

async fn generate_geometry(Json(payload): Json<GeometryParams>) -> Result<Json<GeometryProfile>, StatusCode> {
    let profile = payload.generate_profile(100);
    Ok(Json(profile))
}

async fn calculate_full(Json(motor): Json<MotorDefinition>) -> Result<Json<CalculationResults>, StatusCode> {
    // This endpoint processes a complete motor definition and returns all results
    
    // 1. Run CEA calculation
    let cea_req = CEARequest {
        fuel: motor.fuel.clone(),
        oxidizer: motor.oxidizer.clone(),
        of_ratio: motor.of_ratio,
        pc: motor.pc,
        expansion_ratio: 40.0,  // Will be calculated from pe
    };
    
    let cea_result = match cea_client::call_cea_service(cea_req).await {
        Ok(r) => r,
        Err(_) => return Err(StatusCode::INTERNAL_SERVER_ERROR),
    };
    
    // 2. Calculate geometry from CEA results and motor params
    let area_throat = (motor.mdot * cea_result.c_star) / (motor.pc * 1e5);  // m²
    let r_throat = (area_throat / std::f64::consts::PI).sqrt();
    let r_chamber = r_throat * motor.contraction_ratio.sqrt();
    
    // Calculate expansion ratio from pe
    let expansion_ratio = (motor.pc / motor.pe).powf(1.0 / cea_result.gamma) * 
                         ((cea_result.gamma + 1.0) / 2.0).powf(1.0 / (cea_result.gamma - 1.0));
    let r_exit = r_throat * expansion_ratio.sqrt();
    
    // Chamber length from L*
    let v_chamber = motor.lstar * area_throat;
    let l_chamber = v_chamber / (std::f64::consts::PI * r_chamber * r_chamber);
    
    // Nozzle length (80% bell)
    let l_nozzle = 0.8 * (r_exit - r_throat) / (motor.theta_e.to_radians().tan());
    
    // 3. Calculate performance
    let thrust_vac = motor.mdot * cea_result.isp_vac * 9.81;
    let thrust_sl = motor.mdot * cea_result.isp_sl * 9.81;
    
    // 4. Generate geometry profile for plotting (80% bell nozzle contour)
    let n_points = 100;
    let mut x_profile = Vec::with_capacity(n_points);
    let mut r_profile = Vec::with_capacity(n_points);
    let mut area_profile = Vec::with_capacity(n_points);
    let mut area_ratio_profile = Vec::with_capacity(n_points);
    
    let total_length = l_chamber + l_nozzle;
    let throat_x = l_chamber;
    
    // Throat radius of curvature (typical: 1.5 * r_throat for upstream, 0.382 * r_throat for downstream)
    let r_curve_upstream = 1.5 * r_throat;
    let r_curve_downstream = 0.382 * r_throat;
    
    // Bell nozzle parameters
    let theta_n_rad = motor.theta_n.to_radians();
    let theta_e_rad = motor.theta_e.to_radians();
    
    for i in 0..n_points {
        let x = (i as f64 / (n_points - 1) as f64) * total_length;
        x_profile.push(x);
        
        let r = if x < throat_x - r_curve_upstream {
            // Cylindrical chamber
            r_chamber
        } else if x < throat_x - r_curve_upstream * 0.3 {
            // Convergent section (smooth curve)
            let t = (x - (throat_x - r_curve_upstream)) / (r_curve_upstream * 0.7);
            let arc = r_curve_upstream * (1.0 - (1.0 - t.clamp(0.0, 1.0)).powi(2));
            r_chamber - (r_chamber - r_throat - r_curve_upstream) * t.clamp(0.0, 1.0).sqrt() - arc * 0.1
        } else if x < throat_x {
            // Throat upstream arc
            let dx = throat_x - x;
            let dy_sq = r_curve_upstream.powi(2) - dx.powi(2);
            if dy_sq > 0.0 {
                r_throat + r_curve_upstream - dy_sq.sqrt()
            } else {
                r_throat
            }
        } else if x < throat_x + r_curve_downstream {
            // Throat downstream arc
            let dx = x - throat_x;
            let dy_sq = r_curve_downstream.powi(2) - dx.powi(2);
            if dy_sq > 0.0 {
                r_throat + r_curve_downstream - dy_sq.sqrt()
            } else {
                r_throat + r_curve_downstream * (1.0 - theta_n_rad.cos())
            }
        } else {
            // 80% Bell nozzle parabola (Rao contour approximation)
            let x_start = throat_x + r_curve_downstream;
            let r_start = r_throat + r_curve_downstream * (1.0 - theta_n_rad.cos());
            let t = ((x - x_start) / (l_nozzle - r_curve_downstream)).clamp(0.0, 1.0);
            
            // Parabolic interpolation from theta_n to theta_e
            let theta = theta_n_rad * (1.0 - t) + theta_e_rad * t;
            let dr = (r_exit - r_start) * (2.0 * t - t * t); // Parabolic
            r_start + dr
        };
        r_profile.push(r.max(r_throat * 0.95));  // Ensure minimum
        
        let area = std::f64::consts::PI * r * r;
        area_profile.push(area);
        area_ratio_profile.push(area / area_throat);
    }
    
    let geometry_profile = motor_definition::GeometryProfile {
        x: x_profile,
        r: r_profile,
        area: area_profile,
        area_ratio: area_ratio_profile,
    };
    
    // 5. Mock thermal results (would call actual solver)
    let cooling_status = if motor.twall_max > 1300.0 {
        "CRITICAL".to_string()
    } else if motor.twall_max > 1000.0 {
        "WARNING".to_string()
    } else {
        "OK".to_string()
    };
    
    let results = CalculationResults {
        // CEA
        isp_vac: cea_result.isp_vac,
        isp_sl: cea_result.isp_sl,
        c_star: cea_result.c_star,
        cf_vac: thrust_vac / (motor.pc * 1e5 * area_throat),
        cf_sl: thrust_sl / (motor.pc * 1e5 * area_throat),
        t_chamber: cea_result.t_chamber,
        gamma: cea_result.gamma,
        mw: cea_result.mw,
        
        // Geometry
        r_throat,
        r_chamber,
        r_exit,
        l_chamber,
        l_nozzle,
        area_throat,
        area_exit: std::f64::consts::PI * r_exit * r_exit,
        expansion_ratio,
        
        // Performance
        thrust_vac,
        thrust_sl,
        mass_flow: motor.mdot,
        
        // Thermal (mock)
        max_heat_flux: 5.0,  // MW/m²
        max_wall_temp: 950.0,  // K
        coolant_temp_out: 340.0,  // K
        coolant_pressure_drop: 3.5,  // bar
        cooling_status,
        
        // Profiles
        thermal_profile: None,
        geometry_profile: Some(geometry_profile),
    };
    
    Ok(Json(results))
}

async fn get_wiki() -> Result<String, StatusCode> {
    match std::fs::read_to_string("../wiki.md") {
        Ok(content) => Ok(content),
        Err(_) => Err(StatusCode::NOT_FOUND)
    }
}

pub async fn create_app() -> Router {
    // CORS layer
    let cors = CorsLayer::new()
        .allow_origin(Any)
        .allow_methods([Method::GET, Method::POST])
        .allow_headers(Any);

    Router::new()
        .route("/", get(root))
        .route("/api/materials", get(get_materials))
        .route("/api/cea/calculate", post(calculate_cea))
        .route("/api/geometry/generate", post(generate_geometry))
        .route("/api/solve", post(run_solver))
        .route("/api/calculate/full", post(calculate_full))
        .route("/api/wiki", get(get_wiki))
        .layer(cors)
}

#[tokio::main]
async fn main() {
    let app = create_app().await;
    let addr = SocketAddr::from(([0, 0, 0, 0], 8000));
    
    println!("🚀 Rust Server listening on http://{}", addr);
    
    let listener = tokio::net::TcpListener::bind(addr).await.unwrap();
    axum::serve(listener, app).await.unwrap();
}
