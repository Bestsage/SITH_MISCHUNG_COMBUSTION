//! # Rocket Server Library
//!
//! Backend pour le design et l'analyse de moteurs-fusées à propergols liquides.
//!
//! ## Modules Principaux
//! - [`nozzle_physics`] - Équations fondamentales de tuyère (isentropique, Bartz)
//! - [`rao_contour`] - Contour parabolique optimisé Thrust Optimized Parabolic (TOP)
//! - [`geometry`] - Génération de contours de tuyère (Bézier)
//! - [`cfd_solver`] - Solveur CFD 2D axisymétrique
//!
//! ## Modules Avancés
//! - [`cooling_advanced`] - Refroidissement: Naraghi, Taylor-Gortler, HARCC
//! - [`structural`] - Analyse structurelle: Lamé, Von Mises, LCF Coffin-Manson
//! - [`materials`] - Base de données matériaux avec k(T) et σ_y(T)
//!
//! ## Modules Support
//! - [`motor_definition`] - Structures de données moteur
//! - [`cea_client`] - Client pour le service NASA CEA

use serde::{Deserialize, Serialize};

// === MODULES PHYSIQUE DE BASE ===
pub mod cea_client;
pub mod cfd_solver;
pub mod geometry;
pub mod materials;
pub mod motor_definition;
pub mod nozzle_physics;

// === MODULES AVANCÉS ===
pub mod cooling_advanced;
pub mod rao_contour;
pub mod structural;

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
