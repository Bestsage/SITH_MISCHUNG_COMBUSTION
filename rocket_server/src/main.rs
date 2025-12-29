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
        "materials": materials::get_all_materials()
    }))
}

async fn calculate_cea(Json(payload): Json<CEARequest>) -> Result<Json<CEAResponse>, StatusCode> {
    match cea_client::call_cea_service(payload).await {
        Ok(result) => Ok(Json(result)),
        Err(_) => Err(StatusCode::INTERNAL_SERVER_ERROR),
    }
}

async fn run_solver(Json(payload): Json<SolverRequest>) -> Result<Json<serde_json::Value>, StatusCode> {
    // This will call the Python-based solver since rocket_core uses PyO3
    // We need to make an HTTP call to a Python service that wraps rocket_core
    
    // For now, return structured mock data that matches expected format
    let n_points = 50;
    let mut x = Vec::new();
    let mut t_wall = Vec::new();
    let mut t_coolant = Vec::new();
    let mut p_coolant = Vec::new();
    
    for i in 0..n_points {
        let pos = (i as f64 / n_points as f64) * 0.35; // 0 to 0.35m
        x.push(pos);
        
        // Mock temperature profile (higher at throat)
        let throat_factor = if pos < 0.15 {
            1.0 + (0.15 - pos) / 0.15 * 0.5
        } else {
            1.0 + (pos - 0.15) / 0.20 * 0.3
        };
        
        t_wall.push(800.0 * throat_factor);
        t_coolant.push(300.0 + 100.0 * throat_factor);
        p_coolant.push(60e5 - (i as f64 / n_points as f64) * 5e5);
    }
    
    Ok(Json(serde_json::json!({
        "status": "success",
        "data": {
            "x": x,
            "t_wall": t_wall,
            "t_coolant": t_coolant,
            "p_coolant": p_coolant,
            "t_out": t_coolant.last().unwrap_or(&350.0),
            "p_out": p_coolant.last().unwrap_or(&55e5),
            "max_t_wall": t_wall.iter().cloned().fold(f64::NEG_INFINITY, f64::max)
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
    
    // 4. Mock thermal results (would call actual solver)
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
        
        // Profiles (None for now, would be populated by solver)
        thermal_profile: None,
        geometry_profile: None,
    };
    
    Ok(Json(results))
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
