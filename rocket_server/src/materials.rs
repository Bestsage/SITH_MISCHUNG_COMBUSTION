use serde_json::{json, Value};
use std::collections::HashMap;

pub fn get_all_materials() -> HashMap<String, Value> {
    let mut materials = HashMap::new();

    materials.insert("Cuivre (Cu-OFHC)".to_string(), json!({"k": 390, "T_melt": 1356, "T_max": 800, "rho": 8940, "E": 115, "nu": 0.34, "alpha": 17.0, "sigma_y": 60, "sigma_uts": 220, "color": "#b87333"}));
    materials.insert("GlidCop AL-15".to_string(), json!({"k": 365, "T_melt": 1356, "T_max": 1200, "rho": 8900, "E": 130, "nu": 0.33, "alpha": 16.6, "sigma_y": 380, "sigma_uts": 450, "color": "#cc5500"}));
    materials.insert("CuCrNb (GRCop-42)".to_string(), json!({"k": 320, "T_melt": 1330, "T_max": 1100, "rho": 8790, "E": 115, "nu": 0.33, "alpha": 17.5, "sigma_y": 260, "sigma_uts": 430, "color": "#ff7f50"}));
    materials.insert("Inconel 718".to_string(), json!({"k": 11.4, "T_melt": 1533, "T_max": 1200, "rho": 8190, "E": 200, "nu": 0.29, "alpha": 13.0, "sigma_y": 1030, "sigma_uts": 1240, "color": "#8b4513"}));
    materials.insert("Aluminium 7075-T6".to_string(), json!({"k": 130, "T_melt": 750, "T_max": 400, "rho": 2810, "E": 71, "nu": 0.33, "alpha": 23.6, "sigma_y": 503, "sigma_uts": 572, "color": "#c0c0c0"}));

    materials
}
