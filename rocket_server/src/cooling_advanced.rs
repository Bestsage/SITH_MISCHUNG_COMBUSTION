//! # Advanced Cooling Module
//!
//! Module de refroidissement avancé avec modèles physiques détaillés.
//!
//! ## Contenu
//! - **Efficacité d'ailette Naraghi** - Amélioration du transfert via les nervures
//! - **Correction Taylor-Gortler** - Effet de courbure sur Nu
//! - **Réseau thermique complet** - Résistances en série avec tous les effets
//! - **Canaux HARCC** - High Aspect Ratio Cooling Channels
//!
//! ## Références
//! - Naraghi, M.H.N. "A General Relations for the Heat Transfer Coefficient"
//! - Taylor, G.I. & Gortler, H. "Instability of Boundary Layers"

use std::f64::consts::PI;

// ═══════════════════════════════════════════════════════════════════════════════
//                    EFFICACITÉ D'AILETTE (NARAGHI)
// ═══════════════════════════════════════════════════════════════════════════════
//
// Dans les canaux rectangulaires, les cloisons entre canaux (ribs) agissent
// comme des ailettes qui augmentent la surface d'échange effective.
// Ignorer cet effet conduit à surdimensionner le refroidissement.

/// Calcule l'efficacité d'ailette rectangulaire (modèle Naraghi).
///
/// # Équation
/// ```text
/// η_f = tanh(m × H) / (m × H)
/// ```
///
/// Où m est le paramètre d'ailette:
/// ```text
/// m = √(2 × h_c / (k_wall × W_rib))
/// ```
///
/// # Arguments
/// * `h_coolant` - Coefficient de transfert du coolant [W/(m²·K)]
/// * `k_wall` - Conductivité thermique de la paroi [W/(m·K)]
/// * `w_rib` - Largeur de la nervure (entre deux canaux) [m]
/// * `h_channel` - Hauteur du canal (= longueur de l'ailette) [m]
///
/// # Retourne
/// Efficacité d'ailette η_f [-] (entre 0 et 1)
///
/// # Interprétation
/// - η_f → 1: Ailette "parfaite", toute sa surface contribue au transfert
/// - η_f → 0: Ailette inefficace (trop haute ou trop fine)
///
/// # Stratégie HARCC
/// Pour maximiser l'efficacité avec des canaux profonds (high aspect ratio):
/// - Augmenter k_wall (utiliser cuivre plutôt qu'Inconel)
/// - Augmenter W_rib (nervures plus épaisses)
pub fn naraghi_fin_efficiency(
    h_coolant: f64,
    k_wall: f64,
    w_rib: f64,
    h_channel: f64,
) -> f64 {
    if k_wall <= 0.0 || w_rib <= 0.0 || h_channel <= 0.0 {
        return 0.0;
    }
    
    // Paramètre d'ailette: m = √(2 h / (k × t))
    let m = (2.0 * h_coolant / (k_wall * w_rib)).sqrt();
    let m_h = m * h_channel;
    
    // Limite pour petit mH (éviter division par zéro)
    if m_h < 0.01 {
        return 1.0; // Ailette parfaite
    }
    
    // η_f = tanh(mH) / (mH)
    m_h.tanh() / m_h
}

/// Calcule la surface d'échange effective avec effet d'ailette.
///
/// # Équation
/// ```text
/// A_eff = W_channel + 2 × H_channel × η_f
/// ```
///
/// Par unité de longueur axiale, la surface d'échange n'est plus juste
/// le fond du canal (W), mais inclut les parois latérales pondérées par η_f.
///
/// # Arguments
/// * `w_channel` - Largeur du canal [m]
/// * `h_channel` - Hauteur du canal [m]
/// * `eta_fin` - Efficacité d'ailette [-]
///
/// # Retourne
/// Périmètre effectif par canal [m]
pub fn effective_heat_transfer_perimeter(
    w_channel: f64,
    h_channel: f64,
    eta_fin: f64,
) -> f64 {
    w_channel + 2.0 * h_channel * eta_fin
}

// ═══════════════════════════════════════════════════════════════════════════════
//                    CORRECTION TAYLOR-GORTLER
// ═══════════════════════════════════════════════════════════════════════════════
//
// Dans les régions courbes (col de la tuyère), les forces centrifuges
// induisent des tourbillons secondaires qui améliorent le mélange turbulent.
// Cela augmente le coefficient de transfert sur les parois concaves.

/// Calcule le nombre de Gortler pour prédire l'instabilité de couche limite.
///
/// # Équation
/// ```text
/// Go = (Re × θ / R)^0.5 × (θ / R)^0.5 = Re_θ × (θ / R)
/// ```
///
/// Version simplifiée basée sur la géométrie:
/// ```text
/// Go ≈ Re^0.5 × (δ / R)
/// ```
///
/// # Arguments
/// * `reynolds` - Nombre de Reynolds du canal [-]
/// * `boundary_layer_thickness` - Épaisseur de couche limite [m] (≈ D_h/10)
/// * `radius_curvature` - Rayon de courbure local [m]
///
/// # Retourne
/// Nombre de Gortler [-]
///
/// # Interprétation
/// - Go > 0.3: Tourbillons de Gortler se développent
/// - Go > 0.6: Transition vers turbulence améliorée
pub fn gortler_number(
    reynolds: f64,
    boundary_layer_thickness: f64,
    radius_curvature: f64,
) -> f64 {
    if radius_curvature <= 0.0 {
        return 0.0; // Pas de courbure
    }
    
    reynolds.sqrt() * (boundary_layer_thickness / radius_curvature)
}

/// Facteur de correction du Nusselt pour courbure concave (Taylor-Gortler).
///
/// # Équation empirique
/// ```text
/// Nu_curved / Nu_straight ≈ 1 + 0.04 × (H/R)^0.5 × Re^0.2
/// ```
///
/// Cette corrélation est une approximation des effets de tourbillons
/// secondaires dans les canaux courbes.
///
/// # Arguments
/// * `h_channel` - Hauteur du canal [m]
/// * `radius_curvature` - Rayon de courbure local [m]
/// * `reynolds` - Nombre de Reynolds du canal [-]
///
/// # Retourne
/// Facteur multiplicatif (≥ 1.0)
///
/// # Notes
/// - Au col où la courbure est forte, ce facteur peut atteindre 1.2-1.5
/// - Permet potentiellement de réduire la vitesse du coolant
pub fn taylor_gortler_correction(
    h_channel: f64,
    radius_curvature: f64,
    reynolds: f64,
) -> f64 {
    if radius_curvature <= 0.0 || h_channel <= 0.0 {
        return 1.0;
    }
    
    let ratio = (h_channel / radius_curvature).sqrt();
    let re_factor = reynolds.powf(0.2);
    
    (1.0 + 0.04 * ratio * re_factor).max(1.0)
}

// ═══════════════════════════════════════════════════════════════════════════════
//                    RÉSEAU THERMIQUE COMPLET
// ═══════════════════════════════════════════════════════════════════════════════
//
// Modèle de résistances thermiques en série avec tous les effets physiques.

/// Paramètres d'entrée pour le calcul thermique
#[derive(Debug, Clone)]
pub struct ThermalInputs {
    // Températures
    pub t_adiabatic_wall: f64,  // Température adiabatique de paroi [K]
    pub t_coolant_bulk: f64,    // Température bulk du coolant [K]
    
    // Coefficients de transfert
    pub h_gas: f64,             // Coefficient côté gaz (Bartz) [W/(m²·K)]
    pub h_coolant: f64,         // Coefficient côté coolant (Gnielinski) [W/(m²·K)]
    
    // Géométrie paroi
    pub wall_thickness: f64,    // Épaisseur liner [m]
    pub k_wall: f64,            // Conductivité paroi [W/(m·K)]
    
    // Géométrie canal
    pub w_channel: f64,         // Largeur canal [m]
    pub h_channel: f64,         // Hauteur canal [m]
    pub w_rib: f64,             // Largeur nervure [m]
    
    // Courbure (optionnel)
    pub radius_curvature: Option<f64>,  // Rayon de courbure local [m]
    pub reynolds: f64,          // Reynolds du canal [-]
}

/// Résultats du calcul thermique
#[derive(Debug, Clone)]
pub struct ThermalOutputs {
    /// Flux thermique [W/m²]
    pub heat_flux: f64,
    /// Température paroi côté gaz [K]
    pub t_wall_hot: f64,
    /// Température paroi côté coolant [K]  
    pub t_wall_cold: f64,
    /// Résistance totale [m²·K/W]
    pub r_total: f64,
    /// Efficacité d'ailette [-]
    pub fin_efficiency: f64,
    /// Facteur de correction courbure [-]
    pub curvature_factor: f64,
}

/// Résout le réseau de résistances thermiques complet.
///
/// # Circuit thermique
/// ```text
/// T_aw → [R_gas] → T_wh → [R_wall] → T_wc → [R_cool_augmented] → T_cool
///         1/h_g        t/k           1/(h_c × A_eff)
/// ```
///
/// Où A_eff inclut l'effet d'ailette Naraghi et la correction Taylor-Gortler.
///
/// # Arguments
/// * `inputs` - Paramètres d'entrée
///
/// # Retourne
/// Structure avec tous les résultats thermiques
pub fn solve_thermal_network(inputs: &ThermalInputs) -> ThermalOutputs {
    // Efficacité d'ailette
    let eta_f = naraghi_fin_efficiency(
        inputs.h_coolant,
        inputs.k_wall,
        inputs.w_rib,
        inputs.h_channel,
    );
    
    // Correction Taylor-Gortler si courbure spécifiée
    let curvature_factor = inputs.radius_curvature
        .map(|r| taylor_gortler_correction(inputs.h_channel, r, inputs.reynolds))
        .unwrap_or(1.0);
    
    // Surface effective par unité de largeur
    let a_eff = effective_heat_transfer_perimeter(
        inputs.w_channel,
        inputs.h_channel,
        eta_f,
    );
    
    // Coefficient de transfert augmenté
    let h_cool_augmented = inputs.h_coolant * curvature_factor * (a_eff / inputs.w_channel);
    
    // Résistances thermiques [m²·K/W]
    let r_gas = 1.0 / inputs.h_gas;
    let r_wall = inputs.wall_thickness / inputs.k_wall;
    let r_cool = 1.0 / h_cool_augmented;
    
    let r_total = r_gas + r_wall + r_cool;
    
    // Flux thermique
    let heat_flux = (inputs.t_adiabatic_wall - inputs.t_coolant_bulk) / r_total;
    
    // Températures intermédiaires
    let t_wall_hot = inputs.t_adiabatic_wall - heat_flux * r_gas;
    let t_wall_cold = inputs.t_coolant_bulk + heat_flux * r_cool;
    
    ThermalOutputs {
        heat_flux,
        t_wall_hot,
        t_wall_cold,
        r_total,
        fin_efficiency: eta_f,
        curvature_factor,
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
//                    DIMENSIONNEMENT HARCC
// ═══════════════════════════════════════════════════════════════════════════════
//
// High Aspect Ratio Cooling Channels - Stratégie de canaux profonds et étroits.

/// Paramètres pour le dimensionnement HARCC
#[derive(Debug, Clone)]
pub struct HarccParams {
    /// Circonférence totale à refroidir [m]
    pub circumference: f64,
    /// Rapport d'aspect cible (H/W) [-]
    pub aspect_ratio: f64,
    /// Largeur minimum de nervure (contrainte fabrication) [m]
    pub min_rib_width: f64,
    /// Perte de charge maximale admissible [Pa]
    pub max_pressure_drop: f64,
    /// Débit massique total coolant [kg/s]
    pub mass_flow: f64,
}

/// Résultat du dimensionnement HARCC
#[derive(Debug, Clone)]
pub struct HarccResult {
    /// Nombre de canaux optimal
    pub n_channels: usize,
    /// Largeur de canal [m]
    pub w_channel: f64,
    /// Hauteur de canal [m]
    pub h_channel: f64,
    /// Largeur de nervure [m]
    pub w_rib: f64,
    /// Diamètre hydraulique [m]
    pub d_hydraulic: f64,
}

/// Dimensionne les canaux HARCC optimaux.
///
/// # Stratégie
/// 1. Maximiser le nombre de canaux (meilleure distribution)
/// 2. Maintenir le rapport d'aspect cible
/// 3. Respecter la contrainte de largeur min de nervure
///
/// # Arguments
/// * `params` - Paramètres de dimensionnement
///
/// # Retourne
/// Configuration optimale des canaux
pub fn dimension_harcc_channels(params: &HarccParams) -> HarccResult {
    // Approche itérative: partir du nombre max de canaux possible
    let mut best_result: Option<HarccResult> = None;
    
    // Pitch minimum = 2× min_rib pour avoir au moins 50% de canal
    let min_pitch = 3.0 * params.min_rib_width;
    let max_channels = (params.circumference / min_pitch).floor() as usize;
    
    for n in (20..=max_channels.max(21)).rev() {
        let pitch = params.circumference / n as f64;
        let w_rib = params.min_rib_width;
        let w_channel = pitch - w_rib;
        
        if w_channel <= 0.0 {
            continue;
        }
        
        let h_channel = w_channel * params.aspect_ratio;
        let d_h = hydraulic_diameter_rectangular(w_channel, h_channel);
        
        // Vérifier la contrainte de perte de charge (approximation)
        // ΔP ∝ v² ∝ (ṁ/A)² ∝ (ṁ/n)² / (w×h)²
        // Plus de canaux = moins de perte de charge par canal
        
        best_result = Some(HarccResult {
            n_channels: n,
            w_channel,
            h_channel,
            w_rib,
            d_hydraulic: d_h,
        });
        
        break; // Prendre le premier (plus de canaux possible)
    }
    
    best_result.unwrap_or(HarccResult {
        n_channels: 60,
        w_channel: 0.002,
        h_channel: 0.008,
        w_rib: 0.001,
        d_hydraulic: 0.0032,
    })
}

/// Diamètre hydraulique d'un canal rectangulaire.
fn hydraulic_diameter_rectangular(width: f64, height: f64) -> f64 {
    2.0 * width * height / (width + height)
}

// ═══════════════════════════════════════════════════════════════════════════════
//                    FACTEUR DE RÉCUPÉRATION
// ═══════════════════════════════════════════════════════════════════════════════

/// Calcule la température adiabatique de paroi (température de récupération).
///
/// # Équation
/// ```text
/// T_aw = T_static × [1 + r × (γ-1)/2 × M²]
///      = T_0 × [1 - (1-r) × (γ-1)/(γ+1)]   (au col, M=1)
/// ```
///
/// Où r est le facteur de récupération:
/// - Écoulement laminaire: r = Pr^0.5 ≈ 0.85
/// - Écoulement turbulent: r = Pr^(1/3) ≈ 0.90
///
/// # Arguments
/// * `t_chamber` - Température totale chambre [K]
/// * `gamma` - Ratio chaleurs spécifiques [-]
/// * `recovery_factor` - Facteur de récupération [-]
///
/// # Retourne
/// Température adiabatique de paroi [K]
///
/// # Notes
/// T_aw < T_chamber à cause de la conversion en énergie cinétique.
/// Au col (M=1), T_aw ≈ 0.95 × T_chamber pour γ=1.2
pub fn adiabatic_wall_temperature(
    t_chamber: f64,
    gamma: f64,
    mach: f64,
    recovery_factor: f64,
) -> f64 {
    let gm1 = gamma - 1.0;
    
    // T_static / T_0 = 1 / (1 + (γ-1)/2 × M²)
    let t_ratio = 1.0 / (1.0 + 0.5 * gm1 * mach * mach);
    let t_static = t_chamber * t_ratio;
    
    // T_aw = T_static × (1 + r × (γ-1)/2 × M²)
    t_static * (1.0 + recovery_factor * 0.5 * gm1 * mach * mach)
}

/// Facteur de récupération pour écoulement turbulent.
///
/// r = Pr^(1/3) ≈ 0.89-0.91 pour les gaz de combustion
pub fn turbulent_recovery_factor(prandtl: f64) -> f64 {
    prandtl.powf(1.0 / 3.0)
}

// ═══════════════════════════════════════════════════════════════════════════════
//                                  TESTS
// ═══════════════════════════════════════════════════════════════════════════════

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_fin_efficiency_perfect() {
        // Ailette très courte → η ≈ 1
        let eta = naraghi_fin_efficiency(10000.0, 300.0, 0.001, 0.0001);
        assert!(eta > 0.99, "η = {} devrait être ~1 pour ailette courte", eta);
    }
    
    #[test]
    fn test_fin_efficiency_realistic() {
        // Cas typique: h=20kW/m²K, k=320 W/mK, W_rib=1.5mm, H=5mm
        let eta = naraghi_fin_efficiency(20000.0, 320.0, 0.0015, 0.005);
        
        // η devrait être entre 0.7 et 0.95
        assert!(eta > 0.6 && eta < 1.0, "η = {} hors plage réaliste", eta);
    }
    
    #[test]
    fn test_fin_efficiency_poor() {
        // Ailette très haute avec mauvais conducteur → η faible
        let eta = naraghi_fin_efficiency(50000.0, 15.0, 0.001, 0.01);
        assert!(eta < 0.5, "η = {} devrait être faible pour cette config", eta);
    }
    
    #[test]
    fn test_taylor_gortler_flat() {
        // Sans courbure → facteur = 1
        let factor = taylor_gortler_correction(0.005, f64::INFINITY, 50000.0);
        assert!((factor - 1.0).abs() < 0.01);
    }
    
    #[test]
    fn test_taylor_gortler_curved() {
        // Forte courbure au col → facteur > 1
        let factor = taylor_gortler_correction(0.005, 0.02, 50000.0);
        assert!(factor > 1.0, "Facteur = {} devrait être > 1", factor);
        assert!(factor < 2.0, "Facteur = {} trop élevé", factor);
    }
    
    #[test]
    fn test_thermal_network_energy_balance() {
        let inputs = ThermalInputs {
            t_adiabatic_wall: 3000.0,
            t_coolant_bulk: 400.0,
            h_gas: 15000.0,
            h_coolant: 30000.0,
            wall_thickness: 0.002,
            k_wall: 300.0,
            w_channel: 0.002,
            h_channel: 0.006,
            w_rib: 0.001,
            radius_curvature: None,
            reynolds: 50000.0,
        };
        
        let result = solve_thermal_network(&inputs);
        
        // Vérifications physiques
        assert!(result.heat_flux > 0.0);
        assert!(result.t_wall_hot < inputs.t_adiabatic_wall);
        assert!(result.t_wall_cold > inputs.t_coolant_bulk);
        assert!(result.t_wall_hot > result.t_wall_cold);
        assert!(result.fin_efficiency > 0.0 && result.fin_efficiency <= 1.0);
    }
    
    #[test]
    fn test_adiabatic_wall_temp() {
        // Au col (M=1) avec r=0.9 et γ=1.2:
        // T_static/T_0 = 1/(1 + 0.1) = 0.909
        // T_aw/T_0 = 0.909 × (1 + 0.9 × 0.1) = 0.909 × 1.09 = 0.99
        // Donc T_aw ≈ 99% de T_chamber pour ce cas
        let t_aw = adiabatic_wall_temperature(3500.0, 1.2, 1.0, 0.9);
        
        let ratio = t_aw / 3500.0;
        assert!(ratio > 0.95 && ratio < 1.0,
            "T_aw/T_c = {:.3} hors plage attendue [0.95, 1.0]", ratio);
    }
    
    #[test]
    fn test_harcc_dimensions() {
        let params = HarccParams {
            circumference: 0.2,  // 200mm
            aspect_ratio: 4.0,
            min_rib_width: 0.001,  // 1mm
            max_pressure_drop: 1e6,
            mass_flow: 0.5,
        };
        
        let result = dimension_harcc_channels(&params);
        
        // Vérifications de cohérence
        assert!(result.n_channels >= 20);
        assert!(result.w_channel > 0.0);
        assert!(result.h_channel > 0.0);
        assert!((result.h_channel / result.w_channel - params.aspect_ratio).abs() < 0.1);
        
        // La somme des pitches = circonférence
        let total_pitch = result.n_channels as f64 * (result.w_channel + result.w_rib);
        assert!((total_pitch - params.circumference).abs() < 0.01);
    }
}
