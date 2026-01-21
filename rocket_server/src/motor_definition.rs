//! # Motor Definition Module
//!
//! Structures de données pour définir un moteur-fusée complet et ses résultats de calcul.
//!
//! ## Contenu
//! - [`MotorDefinition`] - Paramètres d'entrée du moteur
//! - [`CalculationResults`] - Résultats de performance et thermiques
//! - [`ThermalProfile`] - Profil thermique 1D le long du moteur
//! - [`GeometryProfile`] - Profil géométrique (coordonnées)

use serde::{Deserialize, Serialize};

// ═══════════════════════════════════════════════════════════════════════════════
//                         DÉFINITION DU MOTEUR
// ═══════════════════════════════════════════════════════════════════════════════

/// Définition complète d'un moteur-fusée avec tous les paramètres de conception.
///
/// Cette structure contient l'ensemble des entrées nécessaires pour calculer
/// les performances, la géométrie, et l'analyse thermique d'un moteur.
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct MotorDefinition {
    // ─────────────────────────────────────────────────────────────────────────
    //                          IDENTIFICATION
    // ─────────────────────────────────────────────────────────────────────────
    
    /// Nom du moteur (pour référence)
    pub name: String,

    // ─────────────────────────────────────────────────────────────────────────
    //                        PROPERGOLS (CEA)
    // ─────────────────────────────────────────────────────────────────────────
    
    /// Oxydant utilisé (notation CEA)
    /// 
    /// Exemples: "O2" (oxygène liquide), "N2O4" (peroxyde d'azote), "H2O2" (peroxyde)
    pub oxidizer: String,
    
    /// Carburant utilisé (notation CEA)
    /// 
    /// Exemples: "C3H8" (propane), "CH4" (méthane), "RP1" (kérosène), "H2" (hydrogène)
    pub fuel: String,
    
    /// Ratio de mélange O/F [-]
    /// 
    /// ```text
    /// O/F = ṁ_oxydant / ṁ_carburant
    /// ```
    /// 
    /// Le ratio optimal dépend du couple de propergols:
    /// - LOX/RP-1: 2.2-2.7
    /// - LOX/CH4: 3.4-3.8
    /// - LOX/H2: 5.5-6.5
    /// - LOX/C3H8: 2.5-3.0
    pub of_ratio: f64,

    // ─────────────────────────────────────────────────────────────────────────
    //                      CONDITIONS CHAMBRE
    // ─────────────────────────────────────────────────────────────────────────
    
    /// Pression chambre [bar]
    /// 
    /// Typiquement 10-300 bar selon le cycle:
    /// - 10-30 bar: Moteurs amateurs, pression-fed
    /// - 50-100 bar: Moteurs professionnels simples
    /// - 100-300 bar: Moteurs haute performance (staged combustion)
    pub pc: f64,
    
    /// Débit massique total [kg/s]
    /// 
    /// ```text
    /// ṁ_total = ṁ_oxydant + ṁ_carburant
    /// ```
    pub mdot: f64,
    
    /// Longueur caractéristique L* [m]
    /// 
    /// Volume de la chambre divisé par l'aire au col:
    /// ```text
    /// L* = V_chambre / A_col
    /// ```
    /// 
    /// Valeurs typiques:
    /// - LOX/RP-1: 1.0-1.5 m
    /// - LOX/H2: 0.6-1.0 m
    /// - LOX/CH4: 0.8-1.2 m
    pub lstar: f64,
    
    /// Rapport de contraction [-] = A_chambre / A_col
    /// 
    /// Typiquement 2.5-4.0. Un rapport plus élevé réduit les pertes
    /// mais augmente la taille de la chambre.
    pub contraction_ratio: f64,

    // ─────────────────────────────────────────────────────────────────────────
    //                            TUYÈRE
    // ─────────────────────────────────────────────────────────────────────────
    
    /// Pression de sortie de conception [bar]
    /// 
    /// Détermine le rapport d'expansion optimal:
    /// - Au niveau de la mer: P_e ≈ 1.0 bar
    /// - En altitude: P_e < 1.0 bar
    /// - Dans le vide: P_e → 0 (limité par la taille)
    pub pe: f64,
    
    /// Pression ambiante [bar]
    /// 
    /// Pour le calcul de la poussée effective:
    /// ```text
    /// F = ṁ × V_e + (P_e - P_amb) × A_e
    /// ```
    pub pamb: f64,
    
    /// Angle initial de tuyère θ_n [degrés]
    /// 
    /// Angle au col côté divergent. Typiquement 25-35°.
    pub theta_n: f64,
    
    /// Angle de sortie θ_e [degrés]
    /// 
    /// Angle du contour à la sortie. Typiquement 5-12°.
    pub theta_e: f64,

    // ─────────────────────────────────────────────────────────────────────────
    //                        PAROI / STRUCTURE
    // ─────────────────────────────────────────────────────────────────────────
    
    /// Nom du matériau de paroi
    /// 
    /// Exemples: "Cuivre-Zirconium (CuZr)", "Inconel 718", "GlidCop AL-15"
    pub material_name: String,
    
    /// Épaisseur de paroi [mm]
    /// 
    /// Épaisseur de la paroi côté gaz (liner).
    /// Typiquement 1-5 mm selon la pression et le matériau.
    pub wall_thickness: f64,
    
    /// Conductivité thermique de la paroi [W/(m·K)]
    /// 
    /// Typiquement:
    /// - Cuivre: 300-400 W/(m·K)
    /// - Inconel: 10-20 W/(m·K)
    /// - Aluminium: 100-200 W/(m·K)
    pub wall_k: f64,
    
    /// Température maximale de paroi admissible [K]
    /// 
    /// Doit être inférieure à la limite du matériau:
    /// - Cuivre: 800-1000 K
    /// - Inconel: 1100-1200 K
    /// - Niobium: 1800-2200 K
    pub twall_max: f64,

    // ─────────────────────────────────────────────────────────────────────────
    //                         REFROIDISSEMENT
    // ─────────────────────────────────────────────────────────────────────────
    
    /// Nom du fluide de refroidissement
    /// 
    /// "Auto" = utilise le carburant comme coolant (régénératif classique)
    pub coolant_name: String,
    
    /// Débit massique du coolant [kg/s ou "Auto"]
    /// 
    /// "Auto" = ṁ_carburant = ṁ_total / (1 + O/F)
    pub coolant_mdot: String,
    
    /// Pression d'entrée du coolant [bar]
    /// 
    /// Doit être supérieure à P_chambre pour éviter le retour de flamme.
    pub coolant_pressure: f64,
    
    /// Température d'entrée du coolant [K]
    /// 
    /// Typiquement température de stockage:
    /// - RP-1: 290-300 K
    /// - LCH4: 111 K (cryogénique)
    /// - LH2: 20 K (cryogénique)
    pub coolant_tin: f64,
    
    /// Température de sortie maximale du coolant [K]
    /// 
    /// Doit rester en dessous de la température d'ébullition
    /// pour éviter la vaporisation dans les canaux.
    pub coolant_tout_max: f64,
    
    /// Marge de sécurité thermique [%]
    /// 
    /// Réduction appliquée aux limites calculées.
    pub coolant_margin: f64,

    // ─────────────────────────────────────────────────────────────────────────
    //                    PROPRIÉTÉS COOLANT CUSTOM
    // ─────────────────────────────────────────────────────────────────────────
    
    /// Capacité thermique massique custom [J/(kg·K)]
    pub custom_cp: f64,
    
    /// Point d'ébullition à 1 bar [K]
    pub custom_tboil: f64,
    
    /// Température critique [K]
    pub custom_tcrit: f64,
    
    /// Enthalpie de vaporisation [kJ/kg]
    pub custom_hvap: f64,
}

impl Default for MotorDefinition {
    /// Configuration par défaut: moteur LOX/Propane amateur ~5 kN
    fn default() -> Self {
        Self {
            name: "Moteur_Propane".to_string(),
            
            // Propergols
            oxidizer: "O2".to_string(),
            fuel: "C3H8".to_string(),
            of_ratio: 2.8,  // Proche de l'optimal pour LOX/C3H8
            
            // Chambre
            pc: 12.0,       // 12 bar (pression-fed typique)
            mdot: 0.5,      // 0.5 kg/s → ~5 kN de poussée
            lstar: 1.0,     // 1.0 m (standard)
            contraction_ratio: 3.5,
            
            // Tuyère
            pe: 1.013,      // Optimisé niveau de la mer
            pamb: 1.013,    // Atmosphère standard
            theta_n: 25.0,  // 25° angle initial
            theta_e: 8.0,   // 8° angle de sortie
            
            // Paroi
            material_name: "Cuivre-Zirconium (CuZr)".to_string(),
            wall_thickness: 2.0,  // 2 mm
            wall_k: 340.0,        // 340 W/(m·K)
            twall_max: 1000.0,    // 1000 K max
            
            // Refroidissement
            coolant_name: "Auto".to_string(),
            coolant_mdot: "Auto".to_string(),
            coolant_pressure: 15.0,    // 15 bar (> Pc)
            coolant_tin: 293.0,        // 20°C
            coolant_tout_max: 350.0,   // 77°C max
            coolant_margin: 20.0,      // 20% marge
            
            // Custom (non utilisé si "Auto")
            custom_cp: 2500.0,
            custom_tboil: 350.0,
            custom_tcrit: 500.0,
            custom_hvap: 400.0,
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
//                          RÉSULTATS DE CALCUL
// ═══════════════════════════════════════════════════════════════════════════════

/// Résultats complets de l'analyse d'un moteur.
///
/// Contient les performances (CEA), la géométrie calculée, et l'analyse thermique.
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct CalculationResults {
    // ─────────────────────────────────────────────────────────────────────────
    //                        RÉSULTATS CEA
    // ─────────────────────────────────────────────────────────────────────────
    
    /// Impulsion spécifique dans le vide [s]
    /// 
    /// ```text
    /// Isp_vac = c* × Cf_vac / g₀
    /// ```
    pub isp_vac: f64,
    
    /// Impulsion spécifique au niveau de la mer [s]
    pub isp_sl: f64,
    
    /// Vitesse caractéristique [m/s]
    /// 
    /// Mesure l'efficacité de la chambre de combustion:
    /// ```text
    /// c* = Pc × A* / ṁ = √(γ × R × Tc) / Γ
    /// ```
    pub c_star: f64,
    
    /// Coefficient de poussée dans le vide [-]
    /// 
    /// ```text
    /// Cf = F / (Pc × A*)
    /// ```
    pub cf_vac: f64,
    
    /// Coefficient de poussée au niveau de la mer [-]
    pub cf_sl: f64,
    
    /// Température de combustion [K]
    pub t_chamber: f64,
    
    /// Ratio des chaleurs spécifiques γ = Cp/Cv [-]
    pub gamma: f64,
    
    /// Masse molaire des gaz de combustion [g/mol]
    pub mw: f64,

    // ─────────────────────────────────────────────────────────────────────────
    //                           GÉOMÉTRIE
    // ─────────────────────────────────────────────────────────────────────────
    
    /// Rayon au col [m]
    pub r_throat: f64,
    
    /// Rayon de la chambre [m]
    pub r_chamber: f64,
    
    /// Rayon de sortie [m]
    pub r_exit: f64,
    
    /// Longueur de la chambre [m]
    pub l_chamber: f64,
    
    /// Longueur du divergent [m]
    pub l_nozzle: f64,
    
    /// Aire au col [m²]
    pub area_throat: f64,
    
    /// Aire de sortie [m²]
    pub area_exit: f64,
    
    /// Rapport d'expansion ε = A_e/A* [-]
    pub expansion_ratio: f64,

    // ─────────────────────────────────────────────────────────────────────────
    //                         PERFORMANCE
    // ─────────────────────────────────────────────────────────────────────────
    
    /// Poussée dans le vide [N]
    /// 
    /// ```text
    /// F_vac = ṁ × Isp_vac × g₀
    /// ```
    pub thrust_vac: f64,
    
    /// Poussée au niveau de la mer [N]
    pub thrust_sl: f64,
    
    /// Débit massique total [kg/s]
    pub mass_flow: f64,

    // ─────────────────────────────────────────────────────────────────────────
    //                          THERMIQUE
    // ─────────────────────────────────────────────────────────────────────────
    
    /// Flux thermique maximum [MW/m²]
    /// 
    /// Généralement au col de la tuyère.
    pub max_heat_flux: f64,
    
    /// Température de paroi maximale [K]
    pub max_wall_temp: f64,
    
    /// Température de sortie du coolant [K]
    pub coolant_temp_out: f64,
    
    /// Perte de charge dans les canaux [bar]
    pub coolant_pressure_drop: f64,
    
    /// Statut du système de refroidissement
    /// 
    /// - "OK": Températures dans les limites
    /// - "WARNING": Proche des limites
    /// - "CRITICAL": Dépassement des limites
    pub cooling_status: String,

    // ─────────────────────────────────────────────────────────────────────────
    //                           PROFILS
    // ─────────────────────────────────────────────────────────────────────────
    
    /// Profil thermique 1D (optionnel)
    pub thermal_profile: Option<ThermalProfile>,
    
    /// Profil géométrique (optionnel)
    pub geometry_profile: Option<GeometryProfile>,
}

// ═══════════════════════════════════════════════════════════════════════════════
//                              PROFILS
// ═══════════════════════════════════════════════════════════════════════════════

/// Profil thermique le long du moteur.
///
/// Contient les distributions de température et pression du système de refroidissement.
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct ThermalProfile {
    /// Positions axiales [m]
    pub x: Vec<f64>,
    
    /// Température de paroi (côté gaz) [K]
    pub t_wall: Vec<f64>,
    
    /// Température du coolant [K]
    pub t_coolant: Vec<f64>,
    
    /// Pression du coolant [Pa]
    pub p_coolant: Vec<f64>,
    
    /// Flux thermique local [W/m²]
    pub heat_flux: Vec<f64>,
}

/// Profil géométrique du contour de tuyère.
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct GeometryProfile {
    /// Positions axiales [m]
    pub x: Vec<f64>,
    
    /// Rayons [m]
    pub r: Vec<f64>,
    
    /// Aires de section [m²]
    pub area: Vec<f64>,
    
    /// Rapports de section A/A* [-]
    pub area_ratio: Vec<f64>,
}
