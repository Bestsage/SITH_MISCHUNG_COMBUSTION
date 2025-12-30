use serde::{Deserialize, Serialize};

pub mod cea_client;
pub mod cfd_solver;
pub mod geometry;
pub mod materials;
pub mod motor_definition;

// === CEA TYPES ===
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CEARequest {
    pub fuel: String,
    pub oxidizer: String,
    pub of_ratio: f64,
    pub pc: f64, // bar
    pub expansion_ratio: f64,
    #[serde(default = "default_pe")]
    pub pe: f64, // bar - exit pressure for eps calculation
    #[serde(default)]
    pub fac_cr: f64, // Finite Area Combustor contraction ratio
}

fn default_pe() -> f64 {
    1.013
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CEAResponse {
    pub isp_vac: f64,
    pub isp_sl: f64,
    pub c_star: f64,
    pub t_chamber: f64,
    pub gamma: f64,
    pub mw: f64,
    #[serde(default)]
    pub eps_from_pe: f64, // Expansion ratio from exit pressure
}
