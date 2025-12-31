use axum::{
    http::{Method, StatusCode},
    response::sse::{Event, Sse},
    routing::{get, post},
    Json, Router,
};
use futures::stream::Stream;
use serde::{Deserialize, Serialize};
use std::convert::Infallible;
use std::net::SocketAddr;
use tokio::sync::mpsc;
use tokio_stream::wrappers::ReceiverStream;
use tower_http::cors::{Any, CorsLayer};

mod cea_client;
mod cfd_solver;
mod geometry;
mod materials;
mod motor_definition;

use cfd_solver::{CFDRequest, CFDResult, ProgressUpdate};
use geometry::{GeometryParams, GeometryProfile};
use motor_definition::{CalculationResults, MotorDefinition};
use rocket_server::{CEARequest, CEAResponse};

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

/// CFD 2D axisymmetric solver endpoint
/// This is computationally intensive and runs in a blocking thread
async fn run_cfd(Json(payload): Json<CFDRequest>) -> Result<Json<CFDResult>, (StatusCode, String)> {
    // Run heavy computation in blocking thread pool with panic catching
    let result = tokio::task::spawn_blocking(move || {
        std::panic::catch_unwind(|| cfd_solver::run_cfd_simulation(payload))
    })
    .await
    .map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Task join error: {:?}", e),
        )
    })?;

    match result {
        Ok(cfd_result) => {
            // Check for NaN/Inf in results (would cause JSON serialization issues)
            if cfd_result
                .mach
                .iter()
                .any(|v| v.is_nan() || v.is_infinite())
            {
                return Err((
                    StatusCode::INTERNAL_SERVER_ERROR,
                    "Solver diverged: NaN/Inf in Mach field".to_string(),
                ));
            }
            Ok(Json(cfd_result))
        }
        Err(_) => Err((
            StatusCode::INTERNAL_SERVER_ERROR,
            "CFD solver panicked - try reducing grid size or iterations".to_string(),
        )),
    }
}

/// CFD solver with SSE streaming for progress updates
async fn run_cfd_stream(
    Json(payload): Json<CFDRequest>,
) -> Sse<impl Stream<Item = Result<Event, Infallible>>> {
    let (tx, rx) = mpsc::channel::<Result<Event, Infallible>>(100);

    // Spawn blocking task for CFD computation
    tokio::task::spawn_blocking(move || {
        let tx_clone = tx.clone();

        // Progress callback that sends SSE events
        let progress_callback = move |update: ProgressUpdate| {
            let event_data = serde_json::to_string(&update).unwrap_or_default();
            let event = Event::default().event("progress").data(event_data);
            let _ = tx_clone.blocking_send(Ok(event));
        };

        // Run simulation with progress
        let result = std::panic::catch_unwind(std::panic::AssertUnwindSafe(|| {
            cfd_solver::run_cfd_simulation_with_progress(payload, progress_callback)
        }));

        // Send final result
        match result {
            Ok(cfd_result) => {
                // Check for valid result
                let is_valid = !cfd_result
                    .mach
                    .iter()
                    .any(|v| v.is_nan() || v.is_infinite());

                if is_valid {
                    let result_data = serde_json::to_string(&cfd_result).unwrap_or_default();
                    let event = Event::default().event("result").data(result_data);
                    let _ = tx.blocking_send(Ok(event));
                } else {
                    let event = Event::default()
                        .event("error")
                        .data("Solver diverged: NaN/Inf in results");
                    let _ = tx.blocking_send(Ok(event));
                }
            }
            Err(_) => {
                let event = Event::default().event("error").data("CFD solver panicked");
                let _ = tx.blocking_send(Ok(event));
            }
        }

        // Send done event
        let event = Event::default().event("done").data("complete");
        let _ = tx.blocking_send(Ok(event));
    });

    Sse::new(ReceiverStream::new(rx)).keep_alive(axum::response::sse::KeepAlive::default())
}

async fn run_solver(
    Json(payload): Json<SolverRequest>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    // Extract parameters from payload
    let geom = &payload.geometry;
    let cond = &payload.conditions;

    // Geometry parameters
    let r_throat = geom.r_throat; // m
    let l_total = geom.l_chamber + geom.l_nozzle; // m
    let n_channels = geom.n_channels as usize;
    let w_channel = geom.channel_width; // m
    let h_channel = geom.channel_depth; // m
    let e_wall = geom.wall_thickness; // m

    // Conditions
    let p_inlet = cond.p_inlet; // Pa
    let t_inlet = cond.t_inlet; // K
    let m_dot_total = cond.m_dot; // kg/s coolant
    let pc = cond.pc; // Pa chamber pressure
    let k_wall = cond.k_wall; // W/mK wall conductivity

    // Coolant properties (approximate for RP-1/kerosene)
    let rho_cool = 800.0; // kg/m³
    let cp_cool = 2100.0; // J/kgK
    let mu_cool = 0.001; // Pa.s
    let k_cool = 0.12; // W/mK
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
    let roughness = 1e-6; // m (smooth)
    let f = if re > 2300.0 {
        let a = -1.8 * ((6.9 / re) + (roughness / d_h / 3.7).powf(1.11)).ln() / 10.0_f64.ln();
        (1.0 / a).powi(2)
    } else {
        64.0 / re
    };

    // Gnielinski Nusselt number
    let nu = if re > 2300.0 {
        ((f / 8.0) * (re - 1000.0) * pr_cool)
            / (1.0 + 12.7 * (f / 8.0).sqrt() * (pr_cool.powf(2.0 / 3.0) - 1.0))
    } else {
        3.66 // Laminar
    };

    // Coolant-side heat transfer coefficient
    let h_cool = nu * k_cool / d_h;

    // Bartz correlation for gas-side heat transfer (simplified)
    // hg = 0.026/Dt^0.2 * (mu^0.2 * Cp / Pr^0.6) * (Pc/cstar)^0.8 * (At/A)^0.9 * sigma
    let d_throat = 2.0 * r_throat;
    let gamma = 1.2; // Typical for combustion products
    let t_chamber = 3500.0; // K (from CEA or assumed)
    let c_star = 1700.0; // m/s (typical)

    // Gas properties at chamber conditions (approximate)
    let mu_gas: f64 = 8e-5; // Pa.s
    let cp_gas: f64 = 2000.0; // J/kgK
    let pr_gas: f64 = 0.72;

    let bartz_base = 0.026_f64 / d_throat.powf(0.2)
        * (mu_gas.powf(0.2) * cp_gas / pr_gas.powf(0.6))
        * (pc / c_star).powf(0.8);

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
        let t_aw = t_chamber / local_gamma_factor; // Simplified

        // Solve 1D thermal resistance network
        // q = hg*(Taw - Twh) = k/e*(Twh - Twc) = hc*(Twc - Tcool)
        let r_gas = 1.0 / h_gas;
        let r_wall = e_wall / k_wall;
        let r_cool = 1.0 / h_cool;
        let r_total = r_gas + r_wall + r_cool;

        let q_flux = (t_aw - t_cool) / r_total;
        let t_wall_hot = t_aw - q_flux * r_gas;

        q_flux_arr.push(q_flux / 1e6); // MW/m²
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

async fn generate_geometry(
    Json(payload): Json<GeometryParams>,
) -> Result<Json<GeometryProfile>, StatusCode> {
    let profile = payload.generate_profile(100);
    Ok(Json(profile))
}

async fn calculate_full(
    Json(motor): Json<MotorDefinition>,
) -> Result<Json<CalculationResults>, StatusCode> {
    // This endpoint processes a complete motor definition and returns all results

    // 1. Run CEA calculation with exit pressure for correct expansion ratio
    let cea_req = CEARequest {
        fuel: motor.fuel.clone(),
        oxidizer: motor.oxidizer.clone(),
        of_ratio: motor.of_ratio,
        pc: motor.pc,
        expansion_ratio: 40.0, // Initial estimate, will use eps_from_pe
        pe: motor.pe,          // Pass exit pressure for correct eps calculation
        fac_cr: motor.contraction_ratio, // Use finite area combustor
    };

    let cea_result = match cea_client::call_cea_service(cea_req).await {
        Ok(r) => r,
        Err(_) => return Err(StatusCode::INTERNAL_SERVER_ERROR),
    };

    // 2. Calculate geometry from CEA results and motor params
    let area_throat = (motor.mdot * cea_result.c_star) / (motor.pc * 1e5); // m²
    let r_throat = (area_throat / std::f64::consts::PI).sqrt();
    let r_chamber = r_throat * motor.contraction_ratio.sqrt();

    // Use correct expansion ratio from CEA (calculated from exit pressure)
    // This replaces the wrong formula that was giving huge values
    let expansion_ratio = if cea_result.eps_from_pe > 1.0 {
        cea_result.eps_from_pe
    } else {
        // Fallback: use a reasonable approximation based on pressure ratio
        // Approximate: eps ≈ 1 + 0.5 * ln(Pc/Pe) for small motors
        1.0 + 0.5 * (motor.pc / motor.pe).ln()
    };
    let r_exit = r_throat * expansion_ratio.sqrt();

    // Chamber length from L*
    let v_chamber = motor.lstar * area_throat;
    let l_chamber = v_chamber / (std::f64::consts::PI * r_chamber * r_chamber);

    // Nozzle length - corrected formula for 80% bell
    // Using Rao's approximation: L_n = 0.8 * (sqrt(eps) - 1) * R_t / tan(15°)
    // Where 15° is the average half-angle for conical equivalent
    let avg_half_angle = 15.0_f64.to_radians();
    let l_nozzle = 0.8 * (expansion_ratio.sqrt() - 1.0) * r_throat / avg_half_angle.tan();

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

    // === Pre-Calculate Convergent Geometry ===
    let r_u = 1.5 * r_throat; // Chamber-to-Cone radius
    let r_d_conv = 1.5 * r_throat; // Cone-to-Throat radius (Standard Rao is 1.5 for convergent side)
    let theta_conv = motor.theta_n.to_radians();

    // Geometric points relative to throat (x=0 at throat, growing negative upstream)
    let x_throat_arc_start = -r_d_conv * theta_conv.sin();
    let y_throat_arc_start = r_throat + r_d_conv * (1.0 - theta_conv.cos());

    let h_cone =
        r_chamber - r_throat - r_u * (1.0 - theta_conv.cos()) - r_d_conv * (1.0 - theta_conv.cos());
    let h_cone = h_cone.max(0.0);

    let l_cone = h_cone / theta_conv.tan();

    let x_cone_start = x_throat_arc_start - l_cone;
    let x_chamber_arc_start = x_cone_start - r_u * theta_conv.sin();

    let l_conv_geometric = -x_chamber_arc_start;

    // === Pre-Calculate Divergent Geometry (Initial Arc) ===
    let r_d_div = 0.382 * r_throat; // Throat-to-Parabola radius (Standard Rao)
                                    // Initial parabolic angle (approximate, usually 20-30 deg depending on expansion)
                                    // We'll calculate the angle where the arc matches the average parabola slope or just use a fixed small angle
                                    // For simplicity and smoothness, let's use a fixed transition angle or finding where parabola starts
    let theta_div_start = 28.0_f64.to_radians(); // Typical start angle for parabola
    let x_div_arc_end = r_d_div * theta_div_start.sin();

    // Parabola parameters
    // We need to fit a parabola from (x_div_arc_end, y_div_arc_end) to (l_nozzle, r_exit)
    // This is complex to splice perfectly.
    // Simplified approach: Use arc for x < x_div_arc_end, then blend/switch to parabola.
    // Better simplified approach for this tool:
    // Just enforce the divergent arc for a small distance, then standard bell curve shifted.

    for i in 0..n_points {
        let x = (i as f64 / (n_points - 1) as f64) * total_length;
        x_profile.push(x);

        let r = if x < throat_x - l_conv_geometric {
            r_chamber
        } else if x <= throat_x {
            // ARC-LINE-ARC Convergent Section
            let x_local = -(throat_x - x);

            if x_local > x_throat_arc_start {
                // Convergent Throat Arc (Radius 1.5 Rt)
                let y_center = r_throat + r_d_conv;
                y_center - (r_d_conv * r_d_conv - x_local * x_local).max(0.0).sqrt()
            } else if x_local > x_cone_start {
                // Straight Cone
                y_throat_arc_start + (x_throat_arc_start - x_local) * theta_conv.tan()
            } else if x_local > x_chamber_arc_start {
                // Chamber Arc
                let x_center = x_chamber_arc_start;
                let y_center = r_chamber - r_u;
                let dx = x_local - x_center;
                y_center + (r_u * r_u - dx * dx).max(0.0).sqrt()
            } else {
                r_chamber
            }
        } else {
            // Divergent Section
            let x_local = x - throat_x;

            if x_local < x_div_arc_end {
                // Divergent Throat Arc (Radius 0.382 Rt)
                // Circle centered at (0, Rt + 0.382Rt)
                let y_center = r_throat + r_d_div;
                y_center - (r_d_div * r_d_div - x_local * x_local).max(0.0).sqrt()
            } else {
                // Parabolic Bell (Simplified)
                // We maintain the 80% bell generic shape but blend it from the arc
                let t = x_local / l_nozzle;
                let t = t.clamp(0.0, 1.0);
                r_throat + (r_exit - r_throat) * (2.0 * t - t * t).powf(0.85)
            }
        };

        r_profile.push(r);

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
        max_heat_flux: 5.0,         // MW/m²
        max_wall_temp: 950.0,       // K
        coolant_temp_out: 340.0,    // K
        coolant_pressure_drop: 3.5, // bar
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
        Err(_) => Err(StatusCode::NOT_FOUND),
    }
}

/// Run CFD on external solver (Docker/OpenFOAM)
/// This calls the CFD API container running on the Proxmox server
#[derive(Debug, Serialize, Deserialize)]
struct ExternalCFDRequest {
    #[serde(flatten)]
    params: CFDRequest,
    solver: Option<String>, // "openfoam" or "python"
}

#[derive(Debug, Serialize, Deserialize)]
struct ExternalJobResponse {
    job_id: String,
    status: String,
    progress: f64,
    message: String,
    result_url: Option<String>,
}

async fn run_cfd_external(
    Json(payload): Json<ExternalCFDRequest>,
) -> Result<Json<serde_json::Value>, (StatusCode, String)> {
    // Get the OpenFOAM CFD API URL from environment
    // In Docker Compose, this will be http://openfoam-cfd:8001
    let openfoam_url =
        std::env::var("OPENFOAM_URL").unwrap_or_else(|_| "http://openfoam-cfd:8001".to_string());

    let client = reqwest::Client::new();

    // Start the job
    let response = client
        .post(format!("{}/api/cfd/run", openfoam_url))
        .json(&serde_json::json!({
            "r_throat": payload.params.r_throat,
            "r_chamber": payload.params.r_chamber,
            "r_exit": payload.params.r_exit,
            "l_chamber": payload.params.l_chamber,
            "l_nozzle": payload.params.l_nozzle,
            "p_chamber": payload.params.p_chamber,
            "t_chamber": payload.params.t_chamber,
            "gamma": payload.params.gamma,
            "molar_mass": payload.params.molar_mass,
            "nx": payload.params.nx,
            "ny": payload.params.ny,
            "max_iter": payload.params.max_iter,
            "tolerance": payload.params.tolerance,
            "solver": payload.solver.unwrap_or_else(|| "auto".to_string())
        }))
        .send()
        .await
        .map_err(|e| {
            (
                StatusCode::BAD_GATEWAY,
                format!("Failed to connect to CFD API: {}", e),
            )
        })?;

    if !response.status().is_success() {
        return Err((
            StatusCode::BAD_GATEWAY,
            format!("CFD API error: {}", response.status()),
        ));
    }

    let job: ExternalJobResponse = response.json().await.map_err(|e| {
        (
            StatusCode::INTERNAL_SERVER_ERROR,
            format!("Failed to parse response: {}", e),
        )
    })?;

    // Poll for completion (with timeout)
    let job_id = job.job_id;
    let max_wait = 600; // 10 minutes max
    let mut elapsed = 0;

    loop {
        tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;
        elapsed += 2;

        if elapsed > max_wait {
            return Err((
                StatusCode::GATEWAY_TIMEOUT,
                "CFD simulation timed out".to_string(),
            ));
        }

        let status_response = client
            .get(format!("{}/api/cfd/status/{}", openfoam_url, job_id))
            .send()
            .await
            .map_err(|e| {
                (
                    StatusCode::BAD_GATEWAY,
                    format!("Failed to get status: {}", e),
                )
            })?;

        let status: ExternalJobResponse = status_response.json().await.map_err(|e| {
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                format!("Failed to parse status: {}", e),
            )
        })?;

        match status.status.as_str() {
            "completed" => {
                // Get the result
                let result_response = client
                    .get(format!("{}/api/cfd/result/{}", openfoam_url, job_id))
                    .send()
                    .await
                    .map_err(|e| {
                        (
                            StatusCode::BAD_GATEWAY,
                            format!("Failed to get result: {}", e),
                        )
                    })?;

                let result: serde_json::Value = result_response.json().await.map_err(|e| {
                    (
                        StatusCode::INTERNAL_SERVER_ERROR,
                        format!("Failed to parse result: {}", e),
                    )
                })?;

                return Ok(Json(result));
            }
            "failed" => {
                return Err((
                    StatusCode::INTERNAL_SERVER_ERROR,
                    format!("CFD simulation failed: {}", status.message),
                ));
            }
            _ => {
                // Still running, continue polling
                continue;
            }
        }
    }
}

/// Check if OpenFOAM CFD solver is available
async fn check_openfoam_status() -> Json<serde_json::Value> {
    let openfoam_url =
        std::env::var("OPENFOAM_URL").unwrap_or_else(|_| "http://openfoam-cfd:8001".to_string());

    let client = reqwest::Client::new();

    match client
        .get(format!("{}/health", openfoam_url))
        .timeout(std::time::Duration::from_secs(5))
        .send()
        .await
    {
        Ok(response) if response.status().is_success() => Json(serde_json::json!({
            "available": true,
            "url": openfoam_url,
            "message": "External CFD solver is available"
        })),
        _ => Json(serde_json::json!({
            "available": false,
            "url": openfoam_url,
            "message": "OpenFOAM solver is not available"
        })),
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
        .route("/api/cfd/solve", post(run_cfd))
        .route("/api/cfd/stream", post(run_cfd_stream))
        .route("/api/cfd/external", post(run_cfd_external))
        .route("/api/cfd/openfoam/status", get(check_openfoam_status))
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
