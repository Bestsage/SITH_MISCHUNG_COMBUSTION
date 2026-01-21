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

// === MODULES AVANCÉS ===
mod cooling_advanced;
mod rao_contour;
mod structural;

use cfd_solver::{CFDRequest, CFDResult, ProgressUpdate};
use geometry::{GeometryParams, GeometryProfile};
use motor_definition::{CalculationResults, MotorDefinition};
use rocket_server::{CEARequest, CEAResponse};

// Imports modules avancés
use rao_contour::{generate_rao_contour, RaoParams};
use structural::analyze_wall_section;

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

// ═══════════════════════════════════════════════════════════════════════════════
//                     OPTIMISATION AVANCÉE - REQUEST/RESPONSE
// ═══════════════════════════════════════════════════════════════════════════════

/// Requête pour l'endpoint `/api/optimize/full`
/// 
/// # Description
/// Effectue une analyse complète incluant:
/// - Génération du contour Rao (TOP nozzle)
/// - Analyse thermique avancée (Naraghi, Taylor-Gortler)
/// - Analyse structurelle (Lamé, Von Mises, LCF)
#[derive(Debug, Serialize, Deserialize)]
pub struct OptimizeRequest {
    // === GÉOMÉTRIE DE BASE ===
    /// Rayon au col [m] - typiquement 0.02-0.05 pour petits moteurs
    pub r_throat: f64,
    /// Rapport de détente ε [-] - typiquement 20-80 pour moteurs vacuum
    pub expansion_ratio: f64,
    /// Rapport de contraction A_chamber/A_throat [-] - typiquement 2-5
    #[serde(default = "default_contraction_ratio")]
    pub contraction_ratio: f64,
    /// Fraction de longueur de bell (0.8 = 80% bell) [-]
    #[serde(default = "default_bell_fraction")]
    pub bell_fraction: f64,
    /// Longueur de chambre [m] - déterminée par L*
    #[serde(default)]
    pub l_chamber: f64,
    
    // === CONDITIONS DE FONCTIONNEMENT ===
    /// Pression chambre [Pa]
    pub pc: f64,
    /// Température chambre [K] - obtenue via CEA
    pub t_chamber: f64,
    /// Gamma des gaz [-] - obtenu via CEA
    #[serde(default = "default_gamma")]
    pub gamma: f64,
    /// C* caractéristique [m/s] - obtenu via CEA
    #[serde(default = "default_cstar")]
    pub c_star: f64,
    
    // === REFROIDISSEMENT ===
    /// Nombre de canaux de refroidissement
    pub n_channels: usize,
    /// Largeur des canaux [m]
    pub w_channel: f64,
    /// Profondeur des canaux [m]
    pub h_channel: f64,
    /// Épaisseur de la paroi interne (hot wall) [m]
    pub wall_thickness: f64,
    /// Débit massique total coolant [kg/s]
    pub m_dot_coolant: f64,
    /// Température d'entrée coolant [K]
    pub t_coolant_inlet: f64,
    /// Pression d'entrée coolant [Pa]
    pub p_coolant_inlet: f64,
    
    // === MATÉRIAU ===
    /// Matériau de la paroi chaude: "narloy-z", "grcop-42", "inconel-718"
    #[serde(default = "default_material")]
    pub material: String,
}

fn default_contraction_ratio() -> f64 { 3.0 }
fn default_bell_fraction() -> f64 { 0.8 }
fn default_gamma() -> f64 { 1.2 }
fn default_cstar() -> f64 { 1700.0 }
fn default_material() -> String { "narloy-z".to_string() }

/// Résultat de l'analyse d'optimisation complète
#[derive(Debug, Serialize, Deserialize)]
pub struct OptimizeResponse {
    // === GÉOMÉTRIE RAO ===
    pub geometry: RaoGeometryResult,
    
    // === ANALYSE THERMIQUE ===
    pub thermal: ThermalAnalysisResult,
    
    // === ANALYSE STRUCTURELLE ===
    pub structural: StructuralAnalysisResult,
    
    // === STATUT GLOBAL ===
    pub status: String,
    pub warnings: Vec<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct RaoGeometryResult {
    /// Points x du contour [m]
    pub x: Vec<f64>,
    /// Points r (rayon) du contour [m]
    pub r: Vec<f64>,
    /// Longueur totale du divergent [m]
    pub l_divergent: f64,
    /// Angle initial θ_n [deg]
    pub theta_n_deg: f64,
    /// Angle de sortie θ_e [deg]
    pub theta_e_deg: f64,
    /// Rayon de sortie [m]
    pub r_exit: f64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ThermalAnalysisResult {
    /// Position axiale [m]
    pub x: Vec<f64>,
    /// Température paroi côté gaz [K]
    pub t_wall_hot: Vec<f64>,
    /// Température paroi côté coolant [K]
    pub t_wall_cold: Vec<f64>,
    /// Température coolant [K]
    pub t_coolant: Vec<f64>,
    /// Flux thermique [MW/m²]
    pub q_flux: Vec<f64>,
    /// Pression coolant [Pa]
    pub p_coolant: Vec<f64>,
    /// Température max paroi chaude [K]
    pub max_t_wall_hot: f64,
    /// Flux max [MW/m²]
    pub max_q_flux: f64,
    /// Perte de charge totale [bar]
    pub delta_p_bar: f64,
    /// Efficacité d'ailette moyenne
    pub avg_fin_efficiency: f64,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct StructuralAnalysisResult {
    /// Statut global: "OK", "WARNING", "CRITICAL"
    pub status: String,
    /// Facteur de sécurité minimum
    pub min_safety_factor: f64,
    /// Position du facteur de sécurité minimum [m]
    pub critical_x: f64,
    /// Contrainte Von Mises max [MPa]
    pub max_von_mises_mpa: f64,
    /// Nombre de cycles LCF estimé
    pub lcf_cycles: f64,
    /// Contrainte hoop max [MPa]
    pub max_hoop_mpa: f64,
    /// Contrainte thermique max [MPa]
    pub max_thermal_mpa: f64,
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

// ═══════════════════════════════════════════════════════════════════════════════
//                    SOLVEUR THERMIQUE 1D
// ═══════════════════════════════════════════════════════════════════════════════
//
// Calcule le profil thermique 1D le long de la paroi du moteur.
// 
// Résout le réseau de résistances thermiques:
//   T_gaz → [R_gaz = 1/h_g] → T_wh → [R_paroi = e/k] → T_wc → [R_cool = 1/h_c] → T_cool
//
// Formules utilisées:
//   - Bartz: h_g = 0.026/D_t^0.2 × (μ^0.2 × Cp / Pr^0.6) × (Pc/c*)^0.8 × (At/A)^0.9
//   - Gnielinski: Nu = (f/8)(Re-1000)Pr / [1 + 12.7√(f/8)(Pr^(2/3)-1)]
//   - Darcy-Weisbach: ΔP = f × (L/D_h) × (ρv²/2)
//
// ───────────────────────────────────────────────────────────────────────────────

async fn run_solver(
    Json(payload): Json<SolverRequest>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    // =========================================================================
    //                    EXTRACTION DES PARAMÈTRES
    // =========================================================================
    
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

    // =========================================================================
    //                    PROPRIÉTÉS DU COOLANT (RP-1/Kérosène)
    // =========================================================================
    //
    // Propriétés thermophysiques approximatives pour le kérosène (RP-1).
    // En réalité, ces propriétés varient avec la température.
    //
    // Nombre de Prandtl: Pr = μ × Cp / k
    //   Représente le rapport entre diffusion de quantité de mouvement
    //   et diffusion thermique.
    
    let rho_cool = 800.0;   // Masse volumique [kg/m³]
    let cp_cool = 2100.0;   // Capacité thermique [J/(kg·K)]
    let mu_cool = 0.001;    // Viscosité dynamique [Pa·s]
    let k_cool = 0.12;      // Conductivité thermique [W/(m·K)]
    let pr_cool = cp_cool * mu_cool / k_cool;  // Pr ≈ 17.5 pour RP-1

    // Channel hydraulic diameter
    let a_channel = w_channel * h_channel;
    let p_wet = 2.0 * (w_channel + h_channel);
    let d_h = 4.0 * a_channel / p_wet;

    // Velocity per channel
    let m_dot_channel = m_dot_total / n_channels as f64;
    let v_cool = m_dot_channel / (rho_cool * a_channel);

    // Reynolds number
    let re = rho_cool * v_cool * d_h / mu_cool;

    // =========================================================================
    //                    FACTEUR DE FRICTION (HAALAND)
    // =========================================================================
    //
    // Le facteur de friction f détermine les pertes de charge.
    //
    // Régime laminaire (Re < 2300): f = 64/Re
    // Régime turbulent (Re > 2300): Équation de Haaland
    //   1/√f = -1.8 × log₁₀[(ε/D)/3.7 + 6.9/Re]
    //
    // Note: Pour les canaux de refroidissement, on vise Re > 10000
    // pour un transfert thermique efficace (turbulent pleinement développé).
    
    let roughness = 1e-6; // Rugosité de surface [m] (poli)
    let f = if re > 2300.0 {
        // Équation de Haaland (approximation de Colebrook-White)
        let term = (6.9 / re) + (roughness / d_h / 3.7).powf(1.11);
        let inv_sqrt_f = -1.8 * term.ln() / 10.0_f64.ln();
        (1.0 / inv_sqrt_f).powi(2)
    } else {
        // Régime laminaire: solution analytique
        64.0 / re
    };

    // =========================================================================
    //                    NOMBRE DE NUSSELT (GNIELINSKI)
    // =========================================================================
    //
    // Le nombre de Nusselt détermine l'efficacité du transfert convectif:
    //   Nu = h × D_h / k
    //
    // Corrélation de Gnielinski (valide pour 2300 < Re < 5×10⁶):
    //   Nu = (f/8)(Re - 1000)Pr / [1 + 12.7√(f/8)(Pr^(2/3) - 1)]
    //
    // h_coolant = Nu × k_fluid / D_h
    
    let nu = if re > 2300.0 {
        let f_over_8 = f / 8.0;
        let numerator = f_over_8 * (re - 1000.0) * pr_cool;
        let denominator = 1.0 + 12.7 * f_over_8.sqrt() * (pr_cool.powf(2.0 / 3.0) - 1.0);
        numerator / denominator
    } else {
        3.66  // Laminaire: paroi isotherme (4.36 pour flux constant)
    };

    // Coefficient de transfert côté refroidissement [W/(m²·K)]
    let h_cool = nu * k_cool / d_h;

    // =========================================================================
    //                    CORRÉLATION DE BARTZ (COTE GAZ)
    // =========================================================================
    //
    // La corrélation de Bartz (1957) estime h_g côté gaz chaud:
    //
    //   h_g = [0.026/D_t^0.2] × [μ^0.2 × Cp / Pr^0.6] × [Pc/c*]^0.8 × [At/A]^0.9 × σ
    //
    // Points clés:
    //   - h_g est MAXIMUM au col (At/A = 1)
    //   - h_g augmente avec Pc (∝ Pc^0.8)
    //   - h_g augmente pour les PETITS moteurs (∝ D_t^-0.2)
    //
    // Paramètres typiques produits de combustion:
    //   μ ≈ 8×10⁻⁵ Pa·s, Cp ≈ 2000 J/(kg·K), Pr ≈ 0.72, γ ≈ 1.2
    
    let d_throat = 2.0 * r_throat;        // Diamètre au col [m]
    let gamma = 1.2;                       // Ratio chaleurs spécifiques [-]
    let t_chamber = 3500.0;                // Température chambre [K]
    let c_star = 1700.0;                   // Vitesse caractéristique [m/s]

    // Propriétés des gaz de combustion
    let mu_gas: f64 = 8e-5;               // Viscosité dynamique [Pa·s]
    let cp_gas: f64 = 2000.0;             // Capacité thermique [J/(kg·K)]
    let pr_gas: f64 = 0.72;               // Nombre de Prandtl [-]

    // Coefficient de Bartz de base (sans le facteur At/A)
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

        // ─────────────────────────────────────────────────────────────────────
        // Mise à jour de la température du coolant
        // ─────────────────────────────────────────────────────────────────────
        // Bilan énergétique: Q_absorbé = ṁ × Cp × ΔT
        // Donc: ΔT = Q / (ṁ × Cp)
        
        let r_local = r_throat * area_ratio.sqrt();
        let perimeter = 2.0 * std::f64::consts::PI * r_local;
        let q_absorbed = q_flux * perimeter * dx;
        t_cool += q_absorbed / (m_dot_total * cp_cool);

        // ─────────────────────────────────────────────────────────────────────
        // Perte de charge (Darcy-Weisbach)
        // ─────────────────────────────────────────────────────────────────────
        // ΔP = f × (L/D_h) × (ρv²/2)
        
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

// ═══════════════════════════════════════════════════════════════════════════════
//                    CALCUL COMPLET DU MOTEUR
// ═══════════════════════════════════════════════════════════════════════════════
//
// Endpoint principal pour le calcul d'un moteur complet.
// Enchaîne les étapes suivantes:
//   1. Calcul CEA pour les performances thermodynamiques
//   2. Dimensionnement géométrique (col, chambre, tuyère)
//   3. Calcul des performances (poussée, Isp)
//   4. Génération du profil de contour
//   5. Analyse thermique préliminaire
//
// ───────────────────────────────────────────────────────────────────────────────

async fn calculate_full(
    Json(motor): Json<MotorDefinition>,
) -> Result<Json<CalculationResults>, StatusCode> {
    
    // =========================================================================
    //  ÉTAPE 1: CALCUL CEA (Chemical Equilibrium with Applications)
    // =========================================================================
    //
    // CEA calcule l'équilibre thermodynamique de la combustion:
    //   - Température chambre T_c
    //   - Composition des produits
    //   - Propriétés: γ, masse molaire M, c*
    //   - Performance: Isp, Cf
    
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

    // =========================================================================
    //  ÉTAPE 2: DIMENSIONNEMENT GÉOMÉTRIQUE
    // =========================================================================
    //
    // Calcul des dimensions à partir des résultats CEA et des paramètres.
    //
    // AIRE AU COL (formule fondamentale):
    //   A* = ṁ × c* / (Pc × 1e5)
    //
    // Dérivation: c* = Pc × A* / ṁ (définition de c*)
    // Donc: A* = ṁ × c* / Pc
    //
    // RAYON AU COL:
    //   R_t = √(A* / π)
    
    let area_throat = (motor.mdot * cea_result.c_star) / (motor.pc * 1e5);  // [m²]
    let r_throat = (area_throat / std::f64::consts::PI).sqrt();              // [m]
    let r_chamber = r_throat * motor.contraction_ratio.sqrt();               // [m]

    // RAPPORT D'EXPANSION:
    // Utilise la valeur CEA (calculée depuis P_exit) si disponible.
    // Sinon, approximation: ε ≈ 1 + 0.5 × ln(Pc/Pe)
    let expansion_ratio = if cea_result.eps_from_pe > 1.0 {
        cea_result.eps_from_pe
    } else {
        1.0 + 0.5 * (motor.pc / motor.pe).ln()
    };
    let r_exit = r_throat * expansion_ratio.sqrt();

    // LONGUEUR DE LA CHAMBRE (depuis L*):
    //   L* = V_chambre / A* (définition)
    //   V = L* × A*
    //   L_chambre = V / A_chambre = L* × A* / (π × R_c²)
    
    let v_chamber = motor.lstar * area_throat;
    let l_chamber = v_chamber / (std::f64::consts::PI * r_chamber * r_chamber);

    // LONGUEUR DE LA TUYÈRE (formule de Rao 80% bell):
    //   L_n = 0.8 × (√ε - 1) × R_t / tan(15°)
    //
    // Où 15° est le demi-angle moyen d'un cône équivalent.
    // Le facteur 0.8 donne une tuyère plus courte qu'un cône conique
    // tout en conservant ~99% du Cf.
    
    let avg_half_angle = 15.0_f64.to_radians();
    let l_nozzle = 0.8 * (expansion_ratio.sqrt() - 1.0) * r_throat / avg_half_angle.tan();

    // =========================================================================
    //  ÉTAPE 3: CALCUL DES PERFORMANCES
    // =========================================================================
    //
    // POUSSÉE:
    //   F = ṁ × Isp × g₀
    //
    // Où g₀ = 9.80665 m/s² (accélération gravitationnelle standard)
    
    let thrust_vac = motor.mdot * cea_result.isp_vac * 9.81;   // [N]
    let thrust_sl = motor.mdot * cea_result.isp_sl * 9.81;      // [N]

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

// ═══════════════════════════════════════════════════════════════════════════════
//                    ENDPOINT D'OPTIMISATION AVANCÉE
// ═══════════════════════════════════════════════════════════════════════════════
//
// Cet endpoint intègre tous les modules avancés pour une analyse complète:
// 1. Génération du contour Rao (Thrust Optimized Parabolic)
// 2. Analyse thermique avec modèle Naraghi et correction Taylor-Gortler
// 3. Analyse structurelle avec Lamé, Von Mises, et LCF Coffin-Manson

/// Handler pour `/api/optimize/full`
/// 
/// # Description
/// Effectue une analyse complète de la tuyère incluant:
/// - Génération du contour Rao optimisé
/// - Analyse thermique 1D avec effets avancés (ailettes, courbure)
/// - Analyse structurelle avec fatigue LCF
async fn optimize_full(
    Json(req): Json<OptimizeRequest>,
) -> Result<Json<OptimizeResponse>, (StatusCode, String)> {
    let mut warnings: Vec<String> = Vec::new();
    
    // ═════════════════════════════════════════════════════════════════════════
    //                    PHASE 1: GÉNÉRATION DU CONTOUR RAO
    // ═════════════════════════════════════════════════════════════════════════
    //
    // Utilise la méthode de Rao pour générer un contour parabolique optimisé
    // pour la poussée (TOP = Thrust Optimized Parabolic).
    //
    // Avantages par rapport au cône 15°:
    // - ~2-5% de gain d'Isp
    // - Réduction des pertes divergentes
    
    let rao_params = RaoParams {
        r_throat: req.r_throat,
        expansion_ratio: req.expansion_ratio,
        contraction_ratio: req.contraction_ratio,
        length_fraction: req.bell_fraction,
        convergent_angle: 30.0_f64.to_radians(), // 30° standard
    };
    
    let rao_contour = generate_rao_contour(&rao_params, 100);
    
    // Extraire le rayon de sortie depuis les données
    let r_exit = *rao_contour.r.last().unwrap_or(&(req.r_throat * req.expansion_ratio.sqrt()));
    
    let geometry_result = RaoGeometryResult {
        x: rao_contour.x.clone(),
        r: rao_contour.r.clone(),
        l_divergent: rao_contour.nozzle_length,
        theta_n_deg: rao_contour.theta_n_deg,
        theta_e_deg: rao_contour.theta_e_deg,
        r_exit,
    };
    
    // ═════════════════════════════════════════════════════════════════════════
    //                    PHASE 2: ANALYSE THERMIQUE AVANCÉE
    // ═════════════════════════════════════════════════════════════════════════
    //
    // Analyse 1D le long de la tuyère avec:
    // - Corrélation de Bartz pour h_g (côté gaz)
    // - Modèle Naraghi pour l'efficacité d'ailette
    // - Correction Taylor-Gortler pour la courbure au col
    // - Réseau de résistances thermiques complet
    
    let n_points = rao_contour.x.len();
    let mut x_arr: Vec<f64> = Vec::with_capacity(n_points);
    let mut t_wall_hot_arr: Vec<f64> = Vec::with_capacity(n_points);
    let mut t_wall_cold_arr: Vec<f64> = Vec::with_capacity(n_points);
    let mut t_coolant_arr: Vec<f64> = Vec::with_capacity(n_points);
    let mut q_flux_arr: Vec<f64> = Vec::with_capacity(n_points);
    let mut p_coolant_arr: Vec<f64> = Vec::with_capacity(n_points);
    let mut fin_efficiencies: Vec<f64> = Vec::new();
    
    // Propriétés du coolant (RP-1/kérosène)
    let rho_cool = 800.0;  // kg/m³
    let cp_cool = 2100.0;  // J/kgK
    let mu_cool = 0.001;   // Pa.s
    let k_cool = 0.12;     // W/mK
    
    // Propriétés du matériau
    let material = match req.material.to_lowercase().as_str() {
        "grcop-42" | "grcop42" => structural::MaterialProperties::grcop_42(),
        "inconel-718" | "inconel718" | "inconel" => structural::MaterialProperties::inconel_718(),
        _ => structural::MaterialProperties::narloy_z(),
    };
    
    // Conductivité thermique de la paroi
    let k_wall = match req.material.to_lowercase().as_str() {
        "grcop-42" | "grcop42" => 315.0,     // W/mK
        "inconel-718" | "inconel718" => 11.4, // W/mK
        _ => 340.0,                            // Narloy-Z: 340 W/mK
    };
    
    // Hydraulique des canaux
    let a_channel = req.w_channel * req.h_channel;
    let p_wet = 2.0 * (req.w_channel + req.h_channel);
    let d_h = 4.0 * a_channel / p_wet;
    let m_dot_channel = req.m_dot_coolant / req.n_channels as f64;
    let v_cool = m_dot_channel / (rho_cool * a_channel);
    
    // Reynolds et friction
    let re = rho_cool * v_cool * d_h / mu_cool;
    let pr_cool = cp_cool * mu_cool / k_cool;
    
    // Nusselt de base (Gnielinski)
    let roughness = 1e-6;
    let f = if re > 2300.0 {
        let a = -1.8 * ((6.9 / re) + (roughness / d_h / 3.7).powf(1.11)).ln() / 10.0_f64.ln();
        (1.0 / a).powi(2)
    } else {
        64.0 / re
    };
    
    let nu_base = if re > 2300.0 {
        ((f / 8.0) * (re - 1000.0) * pr_cool)
            / (1.0 + 12.7 * (f / 8.0).sqrt() * (pr_cool.powf(2.0 / 3.0) - 1.0))
    } else {
        3.66
    };
    
    let h_cool_base = nu_base * k_cool / d_h;
    
    // Bartz base coefficient
    let d_throat: f64 = 2.0 * req.r_throat;
    let pr_gas: f64 = 0.72;
    let mu_gas: f64 = 8e-5;
    let cp_gas: f64 = 2000.0;
    
    let bartz_base = 0.026 / d_throat.powf(0.2)
        * (mu_gas.powf(0.2) * cp_gas / pr_gas.powf(0.6))
        * (req.pc / req.c_star).powf(0.8);
    
    // État initial
    let mut t_cool = req.t_coolant_inlet;
    let mut p_cool = req.p_coolant_inlet;
    
    // Itérer sur les points du contour
    for i in 0..n_points {
        let x = rao_contour.x[i];
        let r_local = rao_contour.r[i];
        
        x_arr.push(x);
        
        // Rapport d'aire locale
        let area_ratio = (r_local / req.r_throat).powi(2);
        
        // Coefficient h_g (Bartz)
        // ─────────────────────────────────────────────────────────────────────
        // Formule de Bartz:
        // h_g = (0.026/D_t^0.2) × (μ^0.2 × C_p / Pr^0.6) × (P_c/c*)^0.8 × (A_t/A)^0.9 × σ
        // ─────────────────────────────────────────────────────────────────────
        let h_gas = bartz_base * (1.0 / area_ratio).powf(0.9);
        
        // Efficacité d'ailette (Naraghi)
        // ─────────────────────────────────────────────────────────────────────
        // η_f = tanh(m × H) / (m × H)
        // où m = √(2 × h_c / (k_wall × W_rib))
        // ─────────────────────────────────────────────────────────────────────
        let w_rib = (2.0 * std::f64::consts::PI * r_local - req.n_channels as f64 * req.w_channel) 
            / req.n_channels as f64;
        let eta_fin = cooling_advanced::naraghi_fin_efficiency(
            h_cool_base, k_wall, w_rib.max(0.001), req.h_channel
        );
        fin_efficiencies.push(eta_fin);
        
        // Correction Taylor-Gortler au voisinage du col
        // ─────────────────────────────────────────────────────────────────────
        // Nu_curved / Nu_straight ≈ 1 + 0.04 × (H/R)^0.5 × Re^0.2
        // Améliore le transfert dans les zones courbes (col)
        // ─────────────────────────────────────────────────────────────────────
        let r_curvature = if area_ratio < 2.0 {
            req.r_throat * 0.4  // Rayon de courbure au col (0.4 × R_t typ.)
        } else {
            1e6  // Pas de courbure significative
        };
        let tg_factor = cooling_advanced::taylor_gortler_correction(req.h_channel, r_curvature, re);
        
        // h_coolant effectif avec ailette et courbure
        let h_cool_eff = h_cool_base * eta_fin * tg_factor;
        
        // Température adiabatique de paroi
        // ─────────────────────────────────────────────────────────────────────
        // T_aw = T_0 × [1 + r × (γ-1)/2 × M²] / [1 + (γ-1)/2 × M²]
        // où r ≈ Pr^(1/3) pour turbulent
        // ─────────────────────────────────────────────────────────────────────
        let t_aw = cooling_advanced::adiabatic_wall_temperature(
            req.t_chamber, req.gamma, area_ratio, pr_gas
        );
        
        // Réseau de résistances thermiques
        // ─────────────────────────────────────────────────────────────────────
        // R_total = R_gas + R_wall + R_cool
        //         = 1/h_g + t_wall/k_wall + 1/(h_c × A_eff)
        // q = (T_aw - T_cool) / R_total
        // ─────────────────────────────────────────────────────────────────────
        let r_gas = 1.0 / h_gas;
        let r_wall = req.wall_thickness / k_wall;
        let r_cool = 1.0 / h_cool_eff;
        let r_total = r_gas + r_wall + r_cool;
        
        let q_flux = (t_aw - t_cool) / r_total;
        let t_wall_hot = t_aw - q_flux * r_gas;
        let t_wall_cold = t_wall_hot - q_flux * r_wall;
        
        q_flux_arr.push(q_flux / 1e6); // MW/m²
        t_wall_hot_arr.push(t_wall_hot);
        t_wall_cold_arr.push(t_wall_cold);
        t_coolant_arr.push(t_cool);
        p_coolant_arr.push(p_cool);
        
        // Mise à jour de la température coolant
        let perimeter = 2.0 * std::f64::consts::PI * r_local;
        let dx = if i > 0 { x - rao_contour.x[i - 1] } else { 0.0 };
        let q_absorbed = q_flux * perimeter * dx.abs();
        t_cool += q_absorbed / (req.m_dot_coolant * cp_cool);
        
        // Perte de charge (Darcy-Weisbach)
        let dp = f * (dx.abs() / d_h) * (rho_cool * v_cool.powi(2) / 2.0);
        p_cool -= dp;
    }
    
    let max_t_wall_hot = t_wall_hot_arr.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    let max_q_flux = q_flux_arr.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
    let delta_p = req.p_coolant_inlet - p_cool;
    let avg_fin_efficiency = fin_efficiencies.iter().sum::<f64>() / fin_efficiencies.len() as f64;
    
    let thermal_result = ThermalAnalysisResult {
        x: x_arr.clone(),
        t_wall_hot: t_wall_hot_arr.clone(),
        t_wall_cold: t_wall_cold_arr.clone(),
        t_coolant: t_coolant_arr.clone(),
        q_flux: q_flux_arr.clone(),
        p_coolant: p_coolant_arr.clone(),
        max_t_wall_hot,
        max_q_flux,
        delta_p_bar: delta_p / 1e5,
        avg_fin_efficiency,
    };
    
    // Vérifications thermiques
    if max_t_wall_hot > 900.0 {
        warnings.push(format!(
            "Température paroi élevée: {:.0}K (recommandé < 900K pour cuivre)",
            max_t_wall_hot
        ));
    }
    
    // ═════════════════════════════════════════════════════════════════════════
    //                    PHASE 3: ANALYSE STRUCTURELLE
    // ═════════════════════════════════════════════════════════════════════════
    //
    // Pour chaque point, calcule:
    // - Contrainte hoop (Lamé)
    // - Contrainte thermique
    // - Contrainte Von Mises combinée
    // - Facteur de sécurité
    // - Durée de vie LCF (Coffin-Manson)
    
    let mut min_safety_factor: f64 = f64::INFINITY;
    let mut critical_x: f64 = 0.0;
    let mut max_von_mises: f64 = 0.0;
    let mut max_hoop: f64 = 0.0;
    let mut max_thermal_stress: f64 = 0.0;
    let mut worst_lcf: f64 = f64::INFINITY;
    let mut structural_status = "OK".to_string();
    
    for i in 0..n_points {
        let r_local = rao_contour.r[i];
        let t_hot = t_wall_hot_arr[i];
        let t_cold = t_wall_cold_arr[i];
        
        // Pression locale (approx: plus haute au col)
        let area_ratio = (r_local / req.r_throat).powi(2);
        let p_gas_local = req.pc * area_ratio.powf(-0.7); // Approximation isentropique simplifiée
        let p_cool_local = p_coolant_arr[i];
        
        // Analyse structurelle via le module
        let result = analyze_wall_section(
            p_gas_local.min(req.pc),  // Ne pas dépasser Pc
            p_cool_local,
            r_local,
            req.wall_thickness,
            t_hot,
            t_cold,
            &material,
        );
        
        // Tracking des valeurs critiques
        if result.safety_factor < min_safety_factor {
            min_safety_factor = result.safety_factor;
            critical_x = x_arr[i];
        }
        
        max_von_mises = max_von_mises.max(result.von_mises_stress);
        max_hoop = max_hoop.max(result.hoop_stress.abs());
        max_thermal_stress = max_thermal_stress.max(result.thermal_stress);
        
        if result.lcf_cycles < worst_lcf && result.lcf_cycles > 0.0 && result.lcf_cycles.is_finite() {
            worst_lcf = result.lcf_cycles;
        }
        
        if result.status == "CRITICAL" {
            structural_status = "CRITICAL".to_string();
        } else if result.status == "WARNING" && structural_status != "CRITICAL" {
            structural_status = "WARNING".to_string();
        }
    }
    
    let structural_result = StructuralAnalysisResult {
        status: structural_status.clone(),
        min_safety_factor,
        critical_x,
        max_von_mises_mpa: max_von_mises / 1e6,
        lcf_cycles: if worst_lcf.is_finite() { worst_lcf } else { 100000.0 },
        max_hoop_mpa: max_hoop / 1e6,
        max_thermal_mpa: max_thermal_stress / 1e6,
    };
    
    // Warnings structurels
    if min_safety_factor < 1.5 {
        warnings.push(format!(
            "Facteur de sécurité faible: {:.2} à x={:.3}m",
            min_safety_factor, critical_x
        ));
    }
    
    if worst_lcf < 100.0 && worst_lcf > 0.0 {
        warnings.push(format!(
            "Fatigue critique: seulement {:.0} cycles avant rupture",
            worst_lcf
        ));
    }
    
    // ═════════════════════════════════════════════════════════════════════════
    //                    STATUT GLOBAL
    // ═════════════════════════════════════════════════════════════════════════
    
    let global_status = if structural_status == "CRITICAL" || min_safety_factor < 1.0 {
        "CRITICAL"
    } else if structural_status == "WARNING" || min_safety_factor < 1.5 || !warnings.is_empty() {
        "WARNING"
    } else {
        "OK"
    };
    
    Ok(Json(OptimizeResponse {
        geometry: geometry_result,
        thermal: thermal_result,
        structural: structural_result,
        status: global_status.to_string(),
        warnings,
    }))
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
        .route("/api/optimize/full", post(optimize_full))  // NEW: Advanced optimization
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
