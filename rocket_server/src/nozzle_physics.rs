//! # Nozzle Physics Module
//!
//! Ce module centralise toutes les équations fondamentales de la physique des tuyères
//! pour moteurs-fusées à propergols liquides.
//!
//! ## Contenu
//! - **Relations isentropiques** : T, P, ρ en fonction de Mach
//! - **Relation aire-Mach** : calcul du nombre de Mach à partir du rapport de section
//! - **Corrélation de Bartz** : coefficient de transfert côté gaz chaud (h_g)
//! - **Corrélations de refroidissement** : Gnielinski, Dittus-Boelter (h_c)
//! - **Pertes de charge** : Darcy-Weisbach, Haaland
//! - **Contour de tuyère** : méthode de Rao avec courbes de Bézier
//!
//! ## Références
//! - Bartz, D.R. (1957). "A Simple Equation for Rapid Estimation of Rocket Nozzle Convective Heat Transfer Coefficients"
//! - Huzel & Huang, "Modern Engineering for Design of Liquid-Propellant Rocket Engines"
//! - Sutton & Biblarz, "Rocket Propulsion Elements"

use std::f64::consts::PI;

// ═══════════════════════════════════════════════════════════════════════════════
//                              CONSTANTES PHYSIQUES
// ═══════════════════════════════════════════════════════════════════════════════

/// Constante universelle des gaz parfaits [J/(mol·K)]
pub const R_UNIVERSAL: f64 = 8.314;

/// Accélération gravitationnelle standard [m/s²]
pub const G0: f64 = 9.80665;

// ═══════════════════════════════════════════════════════════════════════════════
//                           RELATIONS ISENTROPIQUES
// ═══════════════════════════════════════════════════════════════════════════════
//
// Ces relations décrivent l'évolution d'un gaz parfait dans une détente
// adiabatique réversible (isentropique). Elles sont fondamentales pour
// le calcul des tuyères de Laval.
//
// Hypothèses:
// - Gaz parfait (PV = nRT)
// - Pas de frottement (réversible)
// - Pas d'échange de chaleur (adiabatique)
// - Propriétés uniformes sur chaque section

/// Calcule le rapport de température T/T₀ pour un écoulement isentropique.
///
/// # Formule
/// ```text
/// T/T₀ = 1 / (1 + (γ-1)/2 × M²)
/// ```
///
/// # Arguments
/// * `mach` - Nombre de Mach local [-]
/// * `gamma` - Ratio des chaleurs spécifiques Cp/Cv [-]
///
/// # Retourne
/// Rapport T/T₀ (toujours ≤ 1)
///
/// # Exemple
/// Au col (M=1) avec γ=1.4: T/T₀ = 0.833 (soit T = 83.3% de T_chambre)
pub fn isentropic_temperature_ratio(mach: f64, gamma: f64) -> f64 {
    // T/T₀ = [1 + (γ-1)/2 × M²]^(-1)
    1.0 / (1.0 + 0.5 * (gamma - 1.0) * mach * mach)
}

/// Calcule le rapport de pression P/P₀ pour un écoulement isentropique.
///
/// # Formule
/// ```text
/// P/P₀ = [1 + (γ-1)/2 × M²]^(-γ/(γ-1))
/// ```
///
/// # Arguments
/// * `mach` - Nombre de Mach local [-]
/// * `gamma` - Ratio des chaleurs spécifiques [-]
///
/// # Retourne
/// Rapport P/P₀ (toujours ≤ 1)
///
/// # Exemple
/// À la sortie (M=3) avec γ=1.2: P/P₀ ≈ 0.027 (forte détente)
pub fn isentropic_pressure_ratio(mach: f64, gamma: f64) -> f64 {
    // P/P₀ = [T/T₀]^(γ/(γ-1))
    let temp_ratio = isentropic_temperature_ratio(mach, gamma);
    temp_ratio.powf(gamma / (gamma - 1.0))
}

/// Calcule le rapport de masse volumique ρ/ρ₀ pour un écoulement isentropique.
///
/// # Formule
/// ```text
/// ρ/ρ₀ = [1 + (γ-1)/2 × M²]^(-1/(γ-1))
/// ```
///
/// # Arguments
/// * `mach` - Nombre de Mach local [-]
/// * `gamma` - Ratio des chaleurs spécifiques [-]
///
/// # Retourne
/// Rapport ρ/ρ₀ (toujours ≤ 1)
pub fn isentropic_density_ratio(mach: f64, gamma: f64) -> f64 {
    // ρ/ρ₀ = [T/T₀]^(1/(γ-1))
    let temp_ratio = isentropic_temperature_ratio(mach, gamma);
    temp_ratio.powf(1.0 / (gamma - 1.0))
}

/// Calcule la vitesse du son dans un gaz parfait.
///
/// # Formule
/// ```text
/// a = √(γ × R × T) = √(γ × P / ρ)
/// ```
///
/// # Arguments
/// * `gamma` - Ratio des chaleurs spécifiques [-]
/// * `r_specific` - Constante spécifique du gaz [J/(kg·K)] = R_universal / M_molaire
/// * `temperature` - Température statique [K]
///
/// # Retourne
/// Vitesse du son [m/s]
///
/// # Exemple
/// Gaz de combustion (γ=1.2, M=25 g/mol, T=3500K): a ≈ 1180 m/s
pub fn speed_of_sound(gamma: f64, r_specific: f64, temperature: f64) -> f64 {
    (gamma * r_specific * temperature).sqrt()
}

// ═══════════════════════════════════════════════════════════════════════════════
//                           RELATION AIRE-MACH
// ═══════════════════════════════════════════════════════════════════════════════
//
// C'est LA relation fondamentale des tuyères de Laval.
// Elle relie le rapport de section A/A* au nombre de Mach.
//
// A* = aire au col (où M = 1, écoulement sonique "choked")
// A  = aire locale
//
// Cette équation a DEUX solutions pour chaque A/A* > 1:
// - Une solution subsonique (M < 1) dans le convergent
// - Une solution supersonique (M > 1) dans le divergent

/// Calcule le rapport de section A/A* pour un nombre de Mach donné.
///
/// # Formule (équation aire-Mach)
/// ```text
/// A/A* = (1/M) × [(2/(γ+1)) × (1 + (γ-1)/2 × M²)]^((γ+1)/(2(γ-1)))
/// ```
///
/// # Arguments
/// * `mach` - Nombre de Mach local (doit être > 0)
/// * `gamma` - Ratio des chaleurs spécifiques
///
/// # Retourne
/// Rapport de section A/A* (toujours ≥ 1, = 1 quand M = 1)
pub fn area_ratio_from_mach(mach: f64, gamma: f64) -> f64 {
    if mach <= 0.0 {
        return f64::INFINITY;
    }
    
    let gp1 = gamma + 1.0;  // γ + 1
    let gm1 = gamma - 1.0;  // γ - 1
    
    // Terme entre crochets: (2/(γ+1)) × (1 + (γ-1)/2 × M²)
    let bracket_term = (2.0 / gp1) * (1.0 + 0.5 * gm1 * mach * mach);
    
    // Exposant: (γ+1) / (2×(γ-1))
    let exponent = gp1 / (2.0 * gm1);
    
    // A/A* = bracket_term^exponent / M
    bracket_term.powf(exponent) / mach
}

/// Résout l'équation aire-Mach pour trouver le nombre de Mach à partir du rapport de section.
///
/// Utilise la méthode de Newton-Raphson pour résoudre:
/// ```text
/// f(M) = A/A* calculé - A/A* cible = 0
/// ```
///
/// # Arguments
/// * `area_ratio` - Rapport de section A/A* cible (doit être ≥ 1)
/// * `gamma` - Ratio des chaleurs spécifiques
/// * `supersonic` - `true` pour la solution supersonique (divergent), `false` pour subsonique
///
/// # Retourne
/// Nombre de Mach correspondant
///
/// # Algorithme
/// Newton-Raphson avec estimation initiale:
/// - Subsonique: M₀ = 0.5
/// - Supersonique: M₀ = 2.0
///
/// # Limites
/// Retourne M entre 0.01 et 10.0 pour éviter les divergences numériques
pub fn mach_from_area_ratio(area_ratio: f64, gamma: f64, supersonic: bool) -> f64 {
    // Cas trivial: au col, A/A* = 1 → M = 1
    if area_ratio < 1.0001 {
        return 1.0;
    }
    
    // Estimation initiale selon la branche recherchée
    let mut mach = if supersonic { 2.0 } else { 0.5 };
    
    let gp1 = gamma + 1.0;
    let gm1 = gamma - 1.0;
    let exponent = gp1 / (2.0 * gm1);
    
    // Newton-Raphson: M_new = M - f(M) / f'(M)
    for _ in 0..50 {
        // Calcul de A/A* pour le Mach actuel
        let term1 = 2.0 / gp1;
        let term2 = 1.0 + 0.5 * gm1 * mach * mach;
        
        let computed_ratio = (term1 * term2).powf(exponent) / mach;
        let error = computed_ratio - area_ratio;
        
        // Convergence atteinte
        if error.abs() < 1e-8 {
            return mach.clamp(0.01, 10.0);
        }
        
        // Dérivée de A/A* par rapport à M
        // d(A/A*)/dM = (A/A*) × (M² - 1) / (M × term2)
        let derivative = computed_ratio * (mach * mach - 1.0) / (mach * term2);
        
        // Protection contre dérivée nulle (près du col)
        if derivative.abs() < 1e-12 {
            break;
        }
        
        // Mise à jour Newton-Raphson
        mach -= error / derivative;
        mach = mach.clamp(0.01, 10.0);
    }
    
    mach.clamp(0.01, 10.0)
}

// ═══════════════════════════════════════════════════════════════════════════════
//                        EXPANSION DE PRANDTL-MEYER
// ═══════════════════════════════════════════════════════════════════════════════
//
// Décrit l'expansion isentropique d'un écoulement supersonique autour d'un coin.
// Utilisé pour modéliser l'expansion dans le panache (plume) après la sortie.

/// Calcule l'angle de Prandtl-Meyer (fonction de détente).
///
/// # Formule
/// ```text
/// ν(M) = √((γ+1)/(γ-1)) × arctan(√((γ-1)/(γ+1) × (M²-1))) - arctan(√(M²-1))
/// ```
///
/// # Arguments
/// * `mach` - Nombre de Mach (doit être ≥ 1 pour écoulement supersonique)
/// * `gamma` - Ratio des chaleurs spécifiques
///
/// # Retourne
/// Angle de Prandtl-Meyer ν [radians]
/// Retourne 0 si M ≤ 1 (pas d'expansion possible en subsonique)
///
/// # Utilisation
/// Si un écoulement à M₁ tourne d'un angle θ, le nouveau Mach est:
/// ν(M₂) = ν(M₁) + θ
pub fn prandtl_meyer_angle(mach: f64, gamma: f64) -> f64 {
    if mach <= 1.0 {
        return 0.0;
    }
    
    let gp1 = gamma + 1.0;
    let gm1 = gamma - 1.0;
    let m2_minus_1 = mach * mach - 1.0;
    
    // √((γ+1)/(γ-1))
    let coefficient = (gp1 / gm1).sqrt();
    
    // arctan(√((γ-1)/(γ+1) × (M²-1)))
    let term1 = ((gm1 / gp1) * m2_minus_1).sqrt().atan();
    
    // arctan(√(M²-1))
    let term2 = m2_minus_1.sqrt().atan();
    
    coefficient * term1 - term2
}

/// Calcule l'angle de Mach (cône de Mach).
///
/// # Formule
/// ```text
/// μ = arcsin(1/M)
/// ```
///
/// L'angle de Mach est le demi-angle du cône dans lequel sont confinées
/// les perturbations d'un écoulement supersonique.
///
/// # Arguments
/// * `mach` - Nombre de Mach (doit être ≥ 1)
///
/// # Retourne
/// Angle de Mach μ [radians]
pub fn mach_angle(mach: f64) -> f64 {
    if mach < 1.0 {
        return PI / 2.0; // 90° pour subsonique (pas de sens physique)
    }
    (1.0 / mach).asin()
}

// ═══════════════════════════════════════════════════════════════════════════════
//                      CORRÉLATION DE BARTZ (h_g)
// ═══════════════════════════════════════════════════════════════════════════════
//
// La corrélation de Bartz (1957) est la méthode standard pour estimer
// le coefficient de transfert thermique convectif côté gaz chaud (h_g).
//
// C'est une corrélation semi-empirique dérivée des équations de couche limite
// turbulente modifiées pour les conditions extrêmes des moteurs-fusées.

/// Calcule le coefficient de transfert thermique côté gaz chaud h_g.
///
/// # Équation de Bartz
/// ```text
/// h_g = [0.026 / D_t^0.2] × [μ^0.2 × Cp / Pr^0.6] × [P_c / c*]^0.8 × [A_t/A]^0.9 × σ
/// ```
///
/// Où σ est le facteur de correction pour la couche limite:
/// ```text
/// σ = 1 / [(T_wg/T_c × 0.5 + 0.5)^0.68 × (1 + (γ-1)/2 × M²)^0.12]
/// ```
///
/// # Arguments
/// * `params` - Structure contenant tous les paramètres nécessaires
///
/// # Retourne
/// Coefficient h_g [W/(m²·K)]
///
/// # Points clés
/// - h_g est MAXIMUM au col (où A_t/A = 1)
/// - h_g augmente avec P_c (∝ P_c^0.8)
/// - h_g augmente quand le moteur est plus petit (∝ D_t^-0.2)
/// - C'est un défi pour les petits moteurs haute pression!
#[derive(Debug, Clone)]
pub struct BartzParams {
    /// Diamètre au col [m]
    pub d_throat: f64,
    /// Viscosité dynamique du gaz [Pa·s]
    pub mu_gas: f64,
    /// Capacité thermique massique du gaz [J/(kg·K)]
    pub cp_gas: f64,
    /// Nombre de Prandtl du gaz [-]
    pub pr_gas: f64,
    /// Pression chambre [Pa]
    pub p_chamber: f64,
    /// Vitesse caractéristique [m/s]
    pub c_star: f64,
    /// Ratio des chaleurs spécifiques [-]
    pub gamma: f64,
    /// Température chambre [K]
    pub t_chamber: f64,
    /// Température de paroi côté gaz [K] (estimation)
    pub t_wall_gas: f64,
}

pub fn bartz_heat_transfer_coefficient(params: &BartzParams, area_ratio: f64, mach: f64) -> f64 {
    // Terme 1: 0.026 / D_t^0.2 (effet d'échelle)
    let scale_term = 0.026 / params.d_throat.powf(0.2);
    
    // Terme 2: μ^0.2 × Cp / Pr^0.6 (propriétés du gaz)
    let gas_props_term = params.mu_gas.powf(0.2) * params.cp_gas / params.pr_gas.powf(0.6);
    
    // Terme 3: (P_c / c*)^0.8 (effet de pression/débit)
    let pressure_term = (params.p_chamber / params.c_star).powf(0.8);
    
    // Terme 4: (A_t/A)^0.9 (effet de position - max au col)
    let area_term = (1.0 / area_ratio).powf(0.9);
    
    // Terme 5: σ (correction de couche limite)
    let t_ratio = params.t_wall_gas / params.t_chamber;
    let sigma_term1 = (t_ratio * 0.5 + 0.5).powf(0.68);
    let sigma_term2 = (1.0 + 0.5 * (params.gamma - 1.0) * mach * mach).powf(0.12);
    let sigma = 1.0 / (sigma_term1 * sigma_term2);
    
    // h_g final
    scale_term * gas_props_term * pressure_term * area_term * sigma
}

/// Facteur de mise à l'échelle simplifié de Bartz.
///
/// Pour une estimation rapide, h_g varie principalement avec le rapport de section:
/// ```text
/// h_g(x) ≈ h_g_throat × (A_t/A)^0.9
/// ```
///
/// # Arguments
/// * `area_ratio` - Rapport de section locale A/A_t
///
/// # Retourne
/// Facteur multiplicatif (1.0 au col, décroît dans le divergent)
pub fn bartz_scaling_factor(area_ratio: f64) -> f64 {
    (1.0 / area_ratio).powf(0.9)
}

// ═══════════════════════════════════════════════════════════════════════════════
//                    CORRÉLATIONS DE TRANSFERT COOLANT (h_c)
// ═══════════════════════════════════════════════════════════════════════════════
//
// Ces corrélations estiment le coefficient de transfert thermique
// côté refroidissement (h_c) dans les canaux de cooling.

/// Calcule le facteur de friction de Darcy pour un écoulement en conduite.
///
/// Utilise l'équation de Haaland (approximation directe de Colebrook-White).
///
/// # Régimes d'écoulement
/// - Re < 2300: Laminaire → f = 64/Re
/// - Re > 2300: Turbulent → Formule de Haaland
///
/// # Équation de Haaland
/// ```text
/// 1/√f = -1.8 × log₁₀[(ε/D)/3.7 + 6.9/Re]
/// ```
///
/// # Arguments
/// * `reynolds` - Nombre de Reynolds [-]
/// * `roughness` - Rugosité absolue de surface [m]
/// * `hydraulic_diameter` - Diamètre hydraulique [m]
///
/// # Retourne
/// Facteur de friction de Darcy f [-]
pub fn friction_factor_haaland(reynolds: f64, roughness: f64, hydraulic_diameter: f64) -> f64 {
    // Régime laminaire: f = 64/Re (solution analytique)
    if reynolds < 2300.0 {
        return 64.0 / reynolds;
    }
    
    // Régime turbulent: équation de Haaland
    let relative_roughness = roughness / hydraulic_diameter;
    let inner_term = (relative_roughness / 3.7) + (6.9 / reynolds);
    let inv_sqrt_f = -1.8 * inner_term.log10();
    
    1.0 / (inv_sqrt_f * inv_sqrt_f)
}

/// Calcule le nombre de Nusselt avec la corrélation de Gnielinski.
///
/// # Domaine de validité
/// - 2300 < Re < 5×10⁶
/// - 0.5 < Pr < 2000
///
/// # Équation
/// ```text
/// Nu = [(f/8)(Re - 1000)Pr] / [1 + 12.7√(f/8)(Pr^(2/3) - 1)]
/// ```
///
/// # Arguments
/// * `reynolds` - Nombre de Reynolds
/// * `prandtl` - Nombre de Prandtl
/// * `friction_f` - Facteur de friction de Darcy
///
/// # Retourne
/// Nombre de Nusselt Nu [-]
///
/// # Notes
/// - Pour Re < 2300 (laminaire), retourne Nu = 3.66 (paroi isotherme)
/// - Plus précis que Dittus-Boelter, surtout pour Re modéré
pub fn nusselt_gnielinski(reynolds: f64, prandtl: f64, friction_f: f64) -> f64 {
    // Régime laminaire: Nu constant
    if reynolds < 2300.0 {
        return 3.66; // Paroi à température constante
        // Alternative: 4.36 pour flux de chaleur constant
    }
    
    // Corrélation de Gnielinski
    let f_over_8 = friction_f / 8.0;
    let numerator = f_over_8 * (reynolds - 1000.0) * prandtl;
    let denominator = 1.0 + 12.7 * f_over_8.sqrt() * (prandtl.powf(2.0 / 3.0) - 1.0);
    
    numerator / denominator
}

/// Calcule le nombre de Nusselt avec la corrélation de Dittus-Boelter.
///
/// # Domaine de validité
/// - Re > 10,000 (turbulent pleinement développé)
/// - 0.6 < Pr < 160
/// - L/D > 10
///
/// # Équation
/// ```text
/// Nu = 0.023 × Re^0.8 × Pr^0.4   (chauffage du fluide)
/// Nu = 0.023 × Re^0.8 × Pr^0.3   (refroidissement du fluide)
/// ```
///
/// # Arguments
/// * `reynolds` - Nombre de Reynolds
/// * `prandtl` - Nombre de Prandtl
/// * `heating` - `true` si le fluide est chauffé (exposant 0.4)
///
/// # Retourne
/// Nombre de Nusselt Nu [-]
pub fn nusselt_dittus_boelter(reynolds: f64, prandtl: f64, heating: bool) -> f64 {
    let pr_exponent = if heating { 0.4 } else { 0.3 };
    0.023 * reynolds.powf(0.8) * prandtl.powf(pr_exponent)
}

/// Calcule le coefficient de transfert h à partir du nombre de Nusselt.
///
/// # Formule
/// ```text
/// h = Nu × k_fluid / D_h
/// ```
///
/// # Arguments
/// * `nusselt` - Nombre de Nusselt [-]
/// * `k_fluid` - Conductivité thermique du fluide [W/(m·K)]
/// * `hydraulic_diameter` - Diamètre hydraulique [m]
///
/// # Retourne
/// Coefficient de transfert h [W/(m²·K)]
pub fn heat_transfer_coefficient_from_nusselt(
    nusselt: f64,
    k_fluid: f64,
    hydraulic_diameter: f64,
) -> f64 {
    nusselt * k_fluid / hydraulic_diameter
}

// ═══════════════════════════════════════════════════════════════════════════════
//                          PERTES DE CHARGE
// ═══════════════════════════════════════════════════════════════════════════════

/// Calcule la perte de charge linéaire selon Darcy-Weisbach.
///
/// # Équation
/// ```text
/// ΔP = f × (L/D_h) × (ρ × v²/2)
/// ```
///
/// # Arguments
/// * `friction_f` - Facteur de friction de Darcy [-]
/// * `length` - Longueur du canal [m]
/// * `hydraulic_diameter` - Diamètre hydraulique [m]
/// * `density` - Masse volumique du fluide [kg/m³]
/// * `velocity` - Vitesse moyenne du fluide [m/s]
///
/// # Retourne
/// Perte de charge ΔP [Pa]
///
/// # Remarque
/// Cette formule ne compte que les pertes linéaires (friction).
/// Les pertes singulières (coudes, contractions) doivent être ajoutées séparément.
pub fn pressure_drop_darcy_weisbach(
    friction_f: f64,
    length: f64,
    hydraulic_diameter: f64,
    density: f64,
    velocity: f64,
) -> f64 {
    friction_f * (length / hydraulic_diameter) * (density * velocity * velocity / 2.0)
}

/// Calcule le diamètre hydraulique d'un canal rectangulaire.
///
/// # Formule
/// ```text
/// D_h = 4A/P = 4×(w×h) / (2×(w+h)) = 2×w×h / (w+h)
/// ```
///
/// # Arguments
/// * `width` - Largeur du canal [m]
/// * `height` - Hauteur (profondeur) du canal [m]
///
/// # Retourne
/// Diamètre hydraulique [m]
pub fn hydraulic_diameter_rectangular(width: f64, height: f64) -> f64 {
    2.0 * width * height / (width + height)
}

// ═══════════════════════════════════════════════════════════════════════════════
//                         RÉSEAU THERMIQUE
// ═══════════════════════════════════════════════════════════════════════════════
//
// Le transfert thermique à travers la paroi est modélisé comme un circuit
// de résistances thermiques en série.

/// Résistances thermiques et calcul du flux.
///
/// # Circuit thermique
/// ```text
/// T_gaz → [R_gaz = 1/h_g] → T_wh → [R_paroi = e/k] → T_wc → [R_cool = 1/h_c] → T_cool
/// ```
///
/// # Arguments
/// * `t_gas` - Température adiabatique de paroi (≈ T_chambre × facteur de récupération) [K]
/// * `t_coolant` - Température bulk du coolant [K]
/// * `h_gas` - Coefficient de transfert côté gaz [W/(m²·K)]
/// * `h_coolant` - Coefficient de transfert côté coolant [W/(m²·K)]
/// * `wall_thickness` - Épaisseur de paroi [m]
/// * `wall_conductivity` - Conductivité thermique de la paroi [W/(m·K)]
///
/// # Retourne
/// Tuple (flux_thermique [W/m²], température_paroi_chaude [K], température_paroi_froide [K])
pub fn thermal_resistance_network(
    t_gas: f64,
    t_coolant: f64,
    h_gas: f64,
    h_coolant: f64,
    wall_thickness: f64,
    wall_conductivity: f64,
) -> (f64, f64, f64) {
    // Résistances thermiques [m²·K/W]
    let r_gas = 1.0 / h_gas;          // Convection côté gaz
    let r_wall = wall_thickness / wall_conductivity;  // Conduction paroi
    let r_cool = 1.0 / h_coolant;     // Convection côté coolant
    
    let r_total = r_gas + r_wall + r_cool;
    
    // Flux thermique [W/m²]
    let heat_flux = (t_gas - t_coolant) / r_total;
    
    // Températures aux interfaces
    let t_wall_hot = t_gas - heat_flux * r_gas;
    let t_wall_cold = t_coolant + heat_flux * r_cool;
    
    (heat_flux, t_wall_hot, t_wall_cold)
}

// ═══════════════════════════════════════════════════════════════════════════════
//                        GÉOMÉTRIE DE TUYÈRE (RAO)
// ═══════════════════════════════════════════════════════════════════════════════
//
// La méthode de Rao permet de générer des contours de tuyère optimisés
// pour minimiser les pertes par divergence.

/// Calcule la longueur d'une tuyère optimisée à 80% (méthode de Rao).
///
/// Une tuyère "80% bell" est un compromis standard entre
/// performances (longueur) et masse/encombrement.
///
/// # Formule approximative
/// ```text
/// L_n = 0.8 × (√ε - 1) × R_t / tan(15°)
/// ```
///
/// Où:
/// - ε = rapport de section de sortie (A_e/A_t)
/// - R_t = rayon au col
/// - 15° = demi-angle moyen équivalent conique
///
/// # Arguments
/// * `r_throat` - Rayon au col [m]
/// * `expansion_ratio` - Rapport de section ε = A_e/A_t [-]
/// * `bell_fraction` - Fraction de cloche (typiquement 0.8 pour 80% bell) [-]
///
/// # Retourne
/// Longueur du divergent [m]
pub fn rao_nozzle_length(r_throat: f64, expansion_ratio: f64, bell_fraction: f64) -> f64 {
    let avg_half_angle = 15.0_f64.to_radians(); // 15° = angle moyen conique équivalent
    bell_fraction * (expansion_ratio.sqrt() - 1.0) * r_throat / avg_half_angle.tan()
}

/// Génère un point sur une courbe de Bézier quadratique.
///
/// # Formule
/// ```text
/// B(t) = (1-t)² × P₀ + 2(1-t)t × P₁ + t² × P₂
/// ```
///
/// # Arguments
/// * `t` - Paramètre de courbe [0, 1]
/// * `p0` - Point de départ (x, y)
/// * `p1` - Point de contrôle (x, y)
/// * `p2` - Point d'arrivée (x, y)
///
/// # Retourne
/// Point sur la courbe (x, y)
pub fn bezier_quadratic(t: f64, p0: (f64, f64), p1: (f64, f64), p2: (f64, f64)) -> (f64, f64) {
    let one_minus_t = 1.0 - t;
    
    let x = one_minus_t * one_minus_t * p0.0
          + 2.0 * one_minus_t * t * p1.0
          + t * t * p2.0;
          
    let y = one_minus_t * one_minus_t * p0.1
          + 2.0 * one_minus_t * t * p1.1
          + t * t * p2.1;
    
    (x, y)
}

/// Calcule le point de contrôle P₁ pour un contour de tuyère Bézier.
///
/// Le point de contrôle est l'intersection des tangentes:
/// - Tangente au col avec angle θ_n (angle initial)
/// - Tangente à la sortie avec angle θ_e (angle de sortie)
///
/// # Arguments
/// * `r_throat` - Rayon au col [m]
/// * `r_exit` - Rayon à la sortie [m]
/// * `l_nozzle` - Longueur du divergent [m]
/// * `theta_n` - Angle initial au col [radians]
/// * `theta_e` - Angle de sortie [radians]
///
/// # Retourne
/// Coordonnées du point de contrôle (x, y) [m]
pub fn bezier_control_point_rao(
    r_throat: f64,
    r_exit: f64,
    l_nozzle: f64,
    theta_n: f64,
    theta_e: f64,
) -> (f64, f64) {
    let tan_n = theta_n.tan();
    let tan_e = theta_e.tan();
    
    // Intersection des deux tangentes
    // Tangente 1: y = tan(θ_n) × x + R_t (passe par col avec angle θ_n)
    // Tangente 2: y = tan(θ_e) × (x - L_n) + R_e (passe par sortie avec angle θ_e)
    
    let denom = tan_n - tan_e;
    let denom = if denom.abs() < 1e-9 { 1e-9 } else { denom };
    
    let x = (r_exit - r_throat - tan_e * l_nozzle) / denom;
    let y = tan_n * x + r_throat;
    
    (x, y)
}

// ═══════════════════════════════════════════════════════════════════════════════
//                                  TESTS
// ═══════════════════════════════════════════════════════════════════════════════

#[cfg(test)]
mod tests {
    use super::*;
    
    const EPSILON: f64 = 1e-6;
    
    #[test]
    fn test_isentropic_at_stagnation() {
        // Au repos (M=0), toutes les propriétés = conditions de stagnation
        let gamma = 1.4;
        
        assert!((isentropic_temperature_ratio(0.0, gamma) - 1.0).abs() < EPSILON);
        assert!((isentropic_pressure_ratio(0.0, gamma) - 1.0).abs() < EPSILON);
        assert!((isentropic_density_ratio(0.0, gamma) - 1.0).abs() < EPSILON);
    }
    
    #[test]
    fn test_isentropic_at_sonic() {
        // Au col (M=1), valeurs critiques connues
        let gamma = 1.4;
        
        // T*/T₀ = 2/(γ+1) = 0.833 pour γ=1.4
        let expected_t_ratio = 2.0 / (gamma + 1.0);
        assert!((isentropic_temperature_ratio(1.0, gamma) - expected_t_ratio).abs() < EPSILON);
        
        // P*/P₀ = [2/(γ+1)]^(γ/(γ-1)) ≈ 0.528 pour γ=1.4
        let expected_p_ratio = expected_t_ratio.powf(gamma / (gamma - 1.0));
        assert!((isentropic_pressure_ratio(1.0, gamma) - expected_p_ratio).abs() < EPSILON);
    }
    
    #[test]
    fn test_area_ratio_at_sonic() {
        // Au col (M=1), A/A* = 1
        let gamma = 1.4;
        assert!((area_ratio_from_mach(1.0, gamma) - 1.0).abs() < EPSILON);
    }
    
    #[test]
    fn test_mach_from_area_ratio_subsonic() {
        let gamma = 1.4;
        let area_ratio = 2.0;
        
        let mach_sub = mach_from_area_ratio(area_ratio, gamma, false);
        
        // Vérifier que c'est bien subsonique
        assert!(mach_sub < 1.0);
        
        // Vérifier cohérence inverse
        let computed_ar = area_ratio_from_mach(mach_sub, gamma);
        assert!((computed_ar - area_ratio).abs() < 0.01);
    }
    
    #[test]
    fn test_mach_from_area_ratio_supersonic() {
        let gamma = 1.4;
        let area_ratio = 2.0;
        
        let mach_super = mach_from_area_ratio(area_ratio, gamma, true);
        
        // Vérifier que c'est bien supersonique
        assert!(mach_super > 1.0);
        
        // Vérifier cohérence inverse
        let computed_ar = area_ratio_from_mach(mach_super, gamma);
        assert!((computed_ar - area_ratio).abs() < 0.01);
    }
    
    #[test]
    fn test_friction_factor_laminar() {
        // Régime laminaire: f = 64/Re
        let re = 1000.0;
        let f = friction_factor_haaland(re, 0.0, 0.01);
        assert!((f - 64.0 / re).abs() < EPSILON);
    }
    
    #[test]
    fn test_hydraulic_diameter_square() {
        // Pour un carré a×a: D_h = a
        let a = 0.005; // 5mm
        let d_h = hydraulic_diameter_rectangular(a, a);
        assert!((d_h - a).abs() < EPSILON);
    }
    
    #[test]
    fn test_bezier_endpoints() {
        let p0 = (0.0, 1.0);
        let p1 = (0.5, 2.0);
        let p2 = (1.0, 1.5);
        
        // À t=0, on est en P0
        let (x0, y0) = bezier_quadratic(0.0, p0, p1, p2);
        assert!((x0 - p0.0).abs() < EPSILON);
        assert!((y0 - p0.1).abs() < EPSILON);
        
        // À t=1, on est en P2
        let (x1, y1) = bezier_quadratic(1.0, p0, p1, p2);
        assert!((x1 - p2.0).abs() < EPSILON);
        assert!((y1 - p2.1).abs() < EPSILON);
    }
    
    #[test]
    fn test_prandtl_meyer_subsonic() {
        // Pas d'expansion possible en subsonique
        assert!((prandtl_meyer_angle(0.5, 1.4) - 0.0).abs() < EPSILON);
        assert!((prandtl_meyer_angle(1.0, 1.4) - 0.0).abs() < EPSILON);
    }
    
    #[test]
    fn test_thermal_network_energy_conservation() {
        // Vérifier que le flux est le même partout dans le réseau
        let t_gas = 3000.0;
        let t_cool = 300.0;
        let h_g = 10000.0;
        let h_c = 20000.0;
        let e = 0.002;
        let k = 300.0;
        
        let (q, t_wh, t_wc) = thermal_resistance_network(t_gas, t_cool, h_g, h_c, e, k);
        
        // Flux côté gaz = h_g × (T_gas - T_wh)
        let q_gas = h_g * (t_gas - t_wh);
        assert!((q_gas - q).abs() / q < 0.001);
        
        // Flux côté coolant = h_c × (T_wc - T_cool)
        let q_cool = h_c * (t_wc - t_cool);
        assert!((q_cool - q).abs() / q < 0.001);
        
        // Flux paroi = k/e × (T_wh - T_wc)
        let q_wall = k / e * (t_wh - t_wc);
        assert!((q_wall - q).abs() / q < 0.001);
    }
}
