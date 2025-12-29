use serde::{Deserialize, Serialize};
use std::collections::HashMap;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Material {
    pub k: f64, // Conductivité thermique (W/mK)
    #[serde(rename = "T_melt")]
    pub t_melt: f64, // Température de fusion (K)
    #[serde(rename = "T_max")]
    pub t_max: f64, // Température max de service (K)
    pub rho: f64, // Densité (kg/m³)
    #[serde(rename = "E")]
    pub e: f64, // Module de Young (GPa)
    pub nu: f64, // Coefficient de Poisson
    pub alpha: f64, // Coefficient de dilatation (×10⁻⁶/K)
    pub sigma_y: f64, // Limite élastique (MPa)
    pub sigma_uts: f64, // Résistance à la traction (MPa)
    pub color: String, // Couleur pour affichage
}

pub fn get_materials() -> HashMap<String, Material> {
    let mut materials = HashMap::new();

    // === CUIVRES ET ALLIAGES ===
    materials.insert(
        "Cuivre (Cu-OFHC)".to_string(),
        Material {
            k: 390.0,
            t_melt: 1356.0,
            t_max: 800.0,
            rho: 8940.0,
            e: 115.0,
            nu: 0.34,
            alpha: 17.0,
            sigma_y: 60.0,
            sigma_uts: 220.0,
            color: "#b87333".to_string(),
        },
    );

    materials.insert(
        "Cuivre-Chrome (CuCr)".to_string(),
        Material {
            k: 320.0,
            t_melt: 1350.0,
            t_max: 1050.0,
            rho: 8900.0,
            e: 118.0,
            nu: 0.33,
            alpha: 17.0,
            sigma_y: 350.0,
            sigma_uts: 420.0,
            color: "#cd7f32".to_string(),
        },
    );

    materials.insert(
        "Cuivre-Zirconium (CuZr)".to_string(),
        Material {
            k: 340.0,
            t_melt: 1356.0,
            t_max: 900.0,
            rho: 8920.0,
            e: 120.0,
            nu: 0.33,
            alpha: 17.0,
            sigma_y: 280.0,
            sigma_uts: 380.0,
            color: "#d2691e".to_string(),
        },
    );

    materials.insert(
        "GlidCop AL-15".to_string(),
        Material {
            k: 365.0,
            t_melt: 1356.0,
            t_max: 1200.0,
            rho: 8900.0,
            e: 130.0,
            nu: 0.33,
            alpha: 16.6,
            sigma_y: 380.0,
            sigma_uts: 450.0,
            color: "#cc5500".to_string(),
        },
    );

    materials.insert(
        "CuCrNb (GRCop-42)".to_string(),
        Material {
            k: 320.0,
            t_melt: 1330.0,
            t_max: 1100.0,
            rho: 8790.0,
            e: 115.0,
            nu: 0.33,
            alpha: 17.5,
            sigma_y: 260.0,
            sigma_uts: 430.0,
            color: "#ff7f50".to_string(),
        },
    );

    // === ALUMINIUM ===
    materials.insert(
        "AlSi10Mg (SLM)".to_string(),
        Material {
            k: 110.0,
            t_melt: 843.0,
            t_max: 570.0,
            rho: 2670.0,
            e: 70.0,
            nu: 0.33,
            alpha: 21.0,
            sigma_y: 240.0,
            sigma_uts: 350.0,
            color: "#a9a9a9".to_string(),
        },
    );

    materials.insert(
        "Aluminium 7075-T6".to_string(),
        Material {
            k: 130.0,
            t_melt: 750.0,
            t_max: 400.0,
            rho: 2810.0,
            e: 71.0,
            nu: 0.33,
            alpha: 23.6,
            sigma_y: 503.0,
            sigma_uts: 572.0,
            color: "#c0c0c0".to_string(),
        },
    );

    materials.insert(
        "Aluminium 6061-T6".to_string(),
        Material {
            k: 167.0,
            t_melt: 855.0,
            t_max: 450.0,
            rho: 2700.0,
            e: 69.0,
            nu: 0.33,
            alpha: 23.6,
            sigma_y: 276.0,
            sigma_uts: 310.0,
            color: "#d3d3d3".to_string(),
        },
    );

    // === SUPERALLIAGES ===
    materials.insert(
        "Inconel 718".to_string(),
        Material {
            k: 11.4,
            t_melt: 1533.0,
            t_max: 1200.0,
            rho: 8190.0,
            e: 200.0,
            nu: 0.29,
            alpha: 13.0,
            sigma_y: 1030.0,
            sigma_uts: 1240.0,
            color: "#8b4513".to_string(),
        },
    );

    materials.insert(
        "Inconel 625".to_string(),
        Material {
            k: 9.8,
            t_melt: 1563.0,
            t_max: 1250.0,
            rho: 8440.0,
            e: 207.0,
            nu: 0.28,
            alpha: 12.8,
            sigma_y: 460.0,
            sigma_uts: 880.0,
            color: "#a0522d".to_string(),
        },
    );

    materials.insert(
        "Monel 400".to_string(),
        Material {
            k: 21.8,
            t_melt: 1570.0,
            t_max: 1000.0,
            rho: 8800.0,
            e: 179.0,
            nu: 0.32,
            alpha: 13.9,
            sigma_y: 240.0,
            sigma_uts: 550.0,
            color: "#808000".to_string(),
        },
    );

    materials.insert(
        "Hastelloy X".to_string(),
        Material {
            k: 9.1,
            t_melt: 1530.0,
            t_max: 1300.0,
            rho: 8220.0,
            e: 205.0,
            nu: 0.30,
            alpha: 14.0,
            sigma_y: 360.0,
            sigma_uts: 750.0,
            color: "#556b2f".to_string(),
        },
    );

    // === ACIERS INOX ===
    materials.insert(
        "Acier Inox 316L".to_string(),
        Material {
            k: 16.3,
            t_melt: 1673.0,
            t_max: 1100.0,
            rho: 8000.0,
            e: 193.0,
            nu: 0.30,
            alpha: 16.0,
            sigma_y: 290.0,
            sigma_uts: 580.0,
            color: "#708090".to_string(),
        },
    );

    materials.insert(
        "Acier Inox 304L".to_string(),
        Material {
            k: 16.2,
            t_melt: 1673.0,
            t_max: 1050.0,
            rho: 7900.0,
            e: 193.0,
            nu: 0.29,
            alpha: 17.2,
            sigma_y: 215.0,
            sigma_uts: 505.0,
            color: "#778899".to_string(),
        },
    );

    materials.insert(
        "Acier Inox 17-4PH".to_string(),
        Material {
            k: 17.9,
            t_melt: 1677.0,
            t_max: 600.0,
            rho: 7750.0,
            e: 196.0,
            nu: 0.27,
            alpha: 10.8,
            sigma_y: 1100.0,
            sigma_uts: 1250.0,
            color: "#696969".to_string(),
        },
    );

    // === RÉFRACTAIRES ===
    materials.insert(
        "Titane Ti-6Al-4V".to_string(),
        Material {
            k: 6.7,
            t_melt: 1933.0,
            t_max: 750.0,
            rho: 4430.0,
            e: 114.0,
            nu: 0.34,
            alpha: 8.6,
            sigma_y: 880.0,
            sigma_uts: 950.0,
            color: "#4682b4".to_string(),
        },
    );

    materials.insert(
        "Niobium C-103".to_string(),
        Material {
            k: 42.0,
            t_melt: 2623.0,
            t_max: 2200.0,
            rho: 8860.0,
            e: 90.0,
            nu: 0.40,
            alpha: 7.3,
            sigma_y: 250.0,
            sigma_uts: 380.0,
            color: "#9370db".to_string(),
        },
    );

    materials.insert(
        "Molybdene (TZM)".to_string(),
        Material {
            k: 126.0,
            t_melt: 2896.0,
            t_max: 2400.0,
            rho: 10220.0,
            e: 320.0,
            nu: 0.31,
            alpha: 5.3,
            sigma_y: 560.0,
            sigma_uts: 700.0,
            color: "#4b0082".to_string(),
        },
    );

    materials.insert(
        "Tungstene".to_string(),
        Material {
            k: 173.0,
            t_melt: 3695.0,
            t_max: 3200.0,
            rho: 19250.0,
            e: 411.0,
            nu: 0.28,
            alpha: 4.5,
            sigma_y: 550.0,
            sigma_uts: 980.0,
            color: "#000080".to_string(),
        },
    );

    materials.insert(
        "Tantalum".to_string(),
        Material {
            k: 57.0,
            t_melt: 3290.0,
            t_max: 2800.0,
            rho: 16690.0,
            e: 186.0,
            nu: 0.34,
            alpha: 6.3,
            sigma_y: 170.0,
            sigma_uts: 250.0,
            color: "#483d8b".to_string(),
        },
    );

    materials.insert(
        "Rhenium".to_string(),
        Material {
            k: 48.0,
            t_melt: 3459.0,
            t_max: 3000.0,
            rho: 21020.0,
            e: 463.0,
            nu: 0.26,
            alpha: 6.2,
            sigma_y: 290.0,
            sigma_uts: 490.0,
            color: "#800000".to_string(),
        },
    );

    // === COMPOSITES ===
    materials.insert(
        "Graphite".to_string(),
        Material {
            k: 120.0,
            t_melt: 3900.0,
            t_max: 3500.0,
            rho: 1800.0,
            e: 11.0,
            nu: 0.20,
            alpha: 4.0,
            sigma_y: 30.0,
            sigma_uts: 45.0,
            color: "#000000".to_string(),
        },
    );

    materials.insert(
        "Carbon-Phenolic".to_string(),
        Material {
            k: 1.5,
            t_melt: 2500.0,
            t_max: 3000.0,
            rho: 1450.0,
            e: 15.0,
            nu: 0.30,
            alpha: 5.0,
            sigma_y: 50.0,
            sigma_uts: 80.0,
            color: "#2f4f4f".to_string(),
        },
    );

    materials
}
