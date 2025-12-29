use serde::{Deserialize, Serialize};

/// Complete motor definition with all parameters from legacy app
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct MotorDefinition {
    // === IDENTIFICATION ===
    pub name: String,

    // === PROPELLANTS (CEA) ===
    pub oxidizer: String,
    pub fuel: String,
    pub of_ratio: f64, // O/F mixture ratio

    // === CHAMBER CONDITIONS ===
    pub pc: f64,                // Chamber pressure (bar)
    pub mdot: f64,              // Total mass flow rate (kg/s)
    pub lstar: f64,             // L* characteristic length (m)
    pub contraction_ratio: f64, // Ac/At

    // === NOZZLE ===
    pub pe: f64,      // Exit pressure design (bar)
    pub pamb: f64,    // Ambient pressure (bar)
    pub theta_n: f64, // Nozzle entrance angle (deg)
    pub theta_e: f64, // Nozzle exit angle (deg)

    // === WALL/STRUCTURE ===
    pub material_name: String,
    pub wall_thickness: f64, // mm
    pub wall_k: f64,         // Thermal conductivity (W/m-K)
    pub twall_max: f64,      // Max wall temperature (K)

    // === COOLING ===
    pub coolant_name: String,  // "Auto" = use fuel
    pub coolant_mdot: String,  // "Auto" or specific value
    pub coolant_pressure: f64, // bar
    pub coolant_tin: f64,      // Inlet temperature (K)
    pub coolant_tout_max: f64, // Max outlet temperature (K)
    pub coolant_margin: f64,   // Safety margin (%)

    // === CUSTOM COOLANT PROPERTIES (if not Auto) ===
    pub custom_cp: f64,    // Specific heat (J/kg-K)
    pub custom_tboil: f64, // Boiling point @1bar (K)
    pub custom_tcrit: f64, // Critical temperature (K)
    pub custom_hvap: f64,  // Heat of vaporization (kJ/kg)
}

impl Default for MotorDefinition {
    fn default() -> Self {
        Self {
            name: "Moteur_Propane".to_string(),
            oxidizer: "O2".to_string(),
            fuel: "C3H8".to_string(),
            of_ratio: 2.8,
            pc: 12.0,
            mdot: 0.5,
            lstar: 1.0,
            contraction_ratio: 3.5,
            pe: 1.013,
            pamb: 1.013,
            theta_n: 25.0,
            theta_e: 8.0,
            material_name: "Cuivre-Zirconium (CuZr)".to_string(),
            wall_thickness: 2.0,
            wall_k: 340.0,
            twall_max: 1000.0,
            coolant_name: "Auto".to_string(),
            coolant_mdot: "Auto".to_string(),
            coolant_pressure: 15.0,
            coolant_tin: 293.0,
            coolant_tout_max: 350.0,
            coolant_margin: 20.0,
            custom_cp: 2500.0,
            custom_tboil: 350.0,
            custom_tcrit: 500.0,
            custom_hvap: 400.0,
        }
    }
}

/// Complete calculation results
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CalculationResults {
    // === CEA RESULTS ===
    pub isp_vac: f64,
    pub isp_sl: f64,
    pub c_star: f64,
    pub cf_vac: f64,
    pub cf_sl: f64,
    pub t_chamber: f64,
    pub gamma: f64,
    pub mw: f64,

    // === GEOMETRY ===
    pub r_throat: f64,
    pub r_chamber: f64,
    pub r_exit: f64,
    pub l_chamber: f64,
    pub l_nozzle: f64,
    pub area_throat: f64,
    pub area_exit: f64,
    pub expansion_ratio: f64,

    // === PERFORMANCE ===
    pub thrust_vac: f64,
    pub thrust_sl: f64,
    pub mass_flow: f64,

    // === THERMAL ===
    pub max_heat_flux: f64,
    pub max_wall_temp: f64,
    pub coolant_temp_out: f64,
    pub coolant_pressure_drop: f64,
    pub cooling_status: String, // "OK", "WARNING", "CRITICAL"

    // === PROFILES ===
    pub thermal_profile: Option<ThermalProfile>,
    pub geometry_profile: Option<GeometryProfile>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ThermalProfile {
    pub x: Vec<f64>,
    pub t_wall: Vec<f64>,
    pub t_coolant: Vec<f64>,
    pub p_coolant: Vec<f64>,
    pub heat_flux: Vec<f64>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct GeometryProfile {
    pub x: Vec<f64>,
    pub r: Vec<f64>,
    pub area: Vec<f64>,
    pub area_ratio: Vec<f64>,
}
