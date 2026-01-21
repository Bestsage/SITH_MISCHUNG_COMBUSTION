//! # Structural Analysis Module
//!
//! Analyse mécanique et structurelle des parois de moteur-fusée.
//!
//! ## Contenu
//! - **Équations de Lamé** - Contrainte circonférentielle (hoop stress) pour paroi épaisse
//! - **Contraintes thermiques** - Dilatation différentielle chaud/froid
//! - **Fatigue LCF** - Coffin-Manson pour durée de vie cyclique
//! - **Validation structurelle** - Comparaison σ vs σ_yield avec facteur de sécurité
//!
//! ## Références
//! - Huzel & Huang, "Modern Engineering for Design of Liquid-Propellant Rocket Engines"
//! - Coffin, L.F. "A Study of the Effects of Cyclic Thermal Stresses"
//! - Manson, S.S. "Behavior of Materials Under Conditions of Thermal Stress"

// ═══════════════════════════════════════════════════════════════════════════════
//                         ÉQUATIONS DE LAMÉ
// ═══════════════════════════════════════════════════════════════════════════════
//
// Pour une paroi cylindrique épaisse sous pression, les équations de Lamé
// donnent la distribution exacte des contraintes radiales et tangentielles.
//
// Plus précis que Barlow (σ = P×R/t) pour les rapports D/t < 20.

/// Calcule la contrainte circonférentielle (hoop stress) maximale selon Lamé.
///
/// # Équation de Lamé pour σ_θ (à la surface intérieure)
/// ```text
/// σ_hoop = (P_int × r_int² - P_ext × r_ext²) / (r_ext² - r_int²)
///        + (r_int² × r_ext² × (P_int - P_ext)) / (r² × (r_ext² - r_int²))
/// ```
///
/// Au rayon intérieur (r = r_int), σ_hoop est maximale.
///
/// # Arguments
/// * `p_internal` - Pression interne [Pa]
/// * `p_external` - Pression externe [Pa]  
/// * `r_internal` - Rayon intérieur [m]
/// * `r_external` - Rayon extérieur [m]
///
/// # Retourne
/// Contrainte hoop maximale (à la surface intérieure) [Pa]
///
/// # Notes
/// - Si P_int > P_ext: paroi en tension (positif)
/// - Si P_int < P_ext: paroi en compression (négatif) - risque de flambage
pub fn lame_hoop_stress(
    p_internal: f64,
    p_external: f64,
    r_internal: f64,
    r_external: f64,
) -> f64 {
    let ri2 = r_internal * r_internal;
    let ro2 = r_external * r_external;
    let delta_r2 = ro2 - ri2;
    
    if delta_r2.abs() < 1e-12 {
        return 0.0; // Paroi infiniment mince
    }
    
    // Contrainte à r = r_internal (maximum)
    let term1 = (p_internal * ri2 - p_external * ro2) / delta_r2;
    let term2 = (ri2 * ro2 * (p_internal - p_external)) / (ri2 * delta_r2);
    
    term1 + term2
}

/// Formule simplifiée de Barlow pour paroi mince.
///
/// # Équation
/// ```text
/// σ_hoop = ΔP × r_internal / t_wall
/// ```
///
/// Valide quand D/t > 20 (paroi mince).
///
/// # Arguments
/// * `delta_p` - Différence de pression [Pa]
/// * `r_internal` - Rayon intérieur [m]
/// * `wall_thickness` - Épaisseur de paroi [m]
///
/// # Retourne
/// Contrainte hoop [Pa]
pub fn barlow_hoop_stress(delta_p: f64, r_internal: f64, wall_thickness: f64) -> f64 {
    if wall_thickness < 1e-12 {
        return f64::INFINITY;
    }
    delta_p * r_internal / wall_thickness
}

/// Calcule la contrainte axiale (longitudinale) pour un cylindre fermé.
///
/// # Équation
/// ```text
/// σ_axial = ΔP × r² / (r_ext² - r_int²) ≈ ΔP × r / (2 × t)  (paroi mince)
/// ```
///
/// La contrainte axiale est environ la moitié de la contrainte hoop.
pub fn axial_stress(delta_p: f64, r_internal: f64, r_external: f64) -> f64 {
    let ri2 = r_internal * r_internal;
    let ro2 = r_external * r_external;
    let delta_r2 = ro2 - ri2;
    
    if delta_r2.abs() < 1e-12 {
        return 0.0;
    }
    
    delta_p * ri2 / delta_r2
}

// ═══════════════════════════════════════════════════════════════════════════════
//                        CONTRAINTES THERMIQUES
// ═══════════════════════════════════════════════════════════════════════════════
//
// La différence de température entre la paroi chaude et froide crée des
// contraintes internes majeures dues à la dilatation différentielle.
//
// Face chaude: veut se dilater → contrainte de COMPRESSION (retenue par le froid)
// Face froide: retient le chaud → contrainte de TRACTION

/// Calcule la contrainte thermique maximale due au gradient de température.
///
/// # Équation
/// ```text
/// σ_thermal = ± E × α × ΔT / (2 × (1 - ν))
/// ```
///
/// Où:
/// - E = Module de Young [Pa]
/// - α = Coefficient de dilatation [1/K]
/// - ΔT = Différence de température (T_hot - T_cold) [K]
/// - ν = Coefficient de Poisson [-]
///
/// # Arguments
/// * `e_modulus` - Module de Young [Pa]
/// * `alpha` - Coefficient de dilatation thermique [1/K]
/// * `delta_t` - Différence de température [K]
/// * `poisson_ratio` - Coefficient de Poisson [-]
///
/// # Retourne
/// Contrainte thermique absolue [Pa]
///
/// # Distribution
/// - Face chaude: -σ_thermal (compression)
/// - Face froide: +σ_thermal (traction)
pub fn thermal_stress(
    e_modulus: f64,
    alpha: f64,
    delta_t: f64,
    poisson_ratio: f64,
) -> f64 {
    if (1.0 - poisson_ratio).abs() < 1e-12 {
        return f64::INFINITY; // Poisson = 1 non physique
    }
    
    (e_modulus * alpha * delta_t) / (2.0 * (1.0 - poisson_ratio))
}

/// Calcule la contrainte thermique avec un modèle de gradient linéaire.
///
/// Plus précis que la formule simplifiée pour les parois épaisses.
///
/// # Équation (approximation linéaire)
/// ```text
/// σ_thermal(r) = (E × α × ΔT) / (1 - ν) × [1/(2×ln(k)) - (k²-1)/(2×(k²+1)×ln(k))]
/// ```
/// où k = r_ext / r_int
pub fn thermal_stress_thick_wall(
    e_modulus: f64,
    alpha: f64,
    t_inner: f64,
    t_outer: f64,
    r_internal: f64,
    r_external: f64,
    poisson_ratio: f64,
) -> f64 {
    let delta_t = t_inner - t_outer;
    let k = r_external / r_internal;
    let ln_k = k.ln();
    
    if ln_k.abs() < 1e-12 {
        return 0.0;
    }
    
    let k2 = k * k;
    let factor = 1.0 / (2.0 * ln_k) - (k2 - 1.0) / (2.0 * (k2 + 1.0) * ln_k);
    
    (e_modulus * alpha * delta_t) / (1.0 - poisson_ratio) * factor
}

// ═══════════════════════════════════════════════════════════════════════════════
//                    CONTRAINTE ÉQUIVALENTE (VON MISES)
// ═══════════════════════════════════════════════════════════════════════════════

/// Calcule la contrainte équivalente de Von Mises pour un état de contrainte biaxial.
///
/// # Équation
/// ```text
/// σ_vm = √(σ₁² + σ₂² - σ₁×σ₂)
/// ```
///
/// # Arguments
/// * `sigma_1` - Contrainte principale 1 (ex: hoop) [Pa]
/// * `sigma_2` - Contrainte principale 2 (ex: axial ou thermal) [Pa]
///
/// # Retourne
/// Contrainte équivalente de Von Mises [Pa]
pub fn von_mises_biaxial(sigma_1: f64, sigma_2: f64) -> f64 {
    (sigma_1 * sigma_1 + sigma_2 * sigma_2 - sigma_1 * sigma_2).sqrt()
}

/// Calcule la contrainte de Von Mises pour état triaxial complet.
///
/// # Équation
/// ```text
/// σ_vm = √(0.5 × [(σ₁-σ₂)² + (σ₂-σ₃)² + (σ₃-σ₁)²])
/// ```
pub fn von_mises_triaxial(sigma_1: f64, sigma_2: f64, sigma_3: f64) -> f64 {
    let term1 = (sigma_1 - sigma_2).powi(2);
    let term2 = (sigma_2 - sigma_3).powi(2);
    let term3 = (sigma_3 - sigma_1).powi(2);
    
    (0.5 * (term1 + term2 + term3)).sqrt()
}

// ═══════════════════════════════════════════════════════════════════════════════
//                    FATIGUE OLIGOCYCLIQUE (LCF)
// ═══════════════════════════════════════════════════════════════════════════════
//
// Les moteurs-fusées subissent des cycles thermiques extrêmes (démarrage/arrêt).
// Si la contrainte dépasse la limite élastique, la paroi plastifie localement.
// Après un certain nombre de cycles, des fissures se forment (LCF).

/// Calcule le nombre de cycles avant rupture selon Coffin-Manson.
///
/// # Équation de Coffin-Manson
/// ```text
/// Δε_p / 2 = ε_f' × (2×N_f)^c
/// ```
///
/// Donc:
/// ```text
/// N_f = 0.5 × (Δε_p / (2 × ε_f'))^(1/c)
/// ```
///
/// # Arguments
/// * `delta_eps_plastic` - Amplitude de déformation plastique [-]
/// * `eps_f_prime` - Coefficient de ductilité en fatigue [-] (typiquement 0.1-0.5)
/// * `c` - Exposant de Coffin-Manson [-] (typiquement -0.5 à -0.7)
///
/// # Retourne
/// Nombre de cycles avant rupture (N_f)
///
/// # Valeurs typiques
/// - Narloy-Z à 800K: ε_f' ≈ 0.15, c ≈ -0.6
/// - GRCop-42 à 800K: ε_f' ≈ 0.20, c ≈ -0.55 (meilleure résistance)
///
/// # Notes
/// Pour réutilisabilité, viser N_f > 100-500 cycles selon le facteur de sécurité.
pub fn coffin_manson_cycles(
    delta_eps_plastic: f64,
    eps_f_prime: f64,
    c: f64,
) -> f64 {
    if eps_f_prime <= 0.0 || delta_eps_plastic <= 0.0 {
        return f64::INFINITY; // Pas de déformation plastique
    }
    
    // Δε_p/2 = ε_f' × (2×N_f)^c
    // (Δε_p/2) / ε_f' = (2×N_f)^c
    // [(Δε_p/2) / ε_f']^(1/c) = 2×N_f
    // N_f = 0.5 × [(Δε_p/2) / ε_f']^(1/c)
    
    let ratio = (delta_eps_plastic / 2.0) / eps_f_prime;
    let exponent = 1.0 / c;
    
    0.5 * ratio.powf(exponent)
}

/// Estime la déformation plastique à partir de la contrainte et du module.
///
/// # Équation (approximation élasto-plastique)
/// ```text
/// ε_plastic ≈ (σ - σ_yield) / E    si σ > σ_yield
///           = 0                     sinon
/// ```
///
/// Note: C'est une approximation grossière. Un modèle plus complet
/// utiliserait la courbe σ-ε du matériau.
pub fn plastic_strain_estimate(
    stress: f64,
    yield_strength: f64,
    e_modulus: f64,
) -> f64 {
    if stress <= yield_strength {
        return 0.0;
    }
    
    (stress - yield_strength) / e_modulus
}

// ═══════════════════════════════════════════════════════════════════════════════
//                    FACTEUR DE SÉCURITÉ
// ═══════════════════════════════════════════════════════════════════════════════

/// Structure pour les résultats d'analyse structurelle
#[derive(Debug, Clone)]
pub struct StructuralResult {
    /// Contrainte hoop [Pa]
    pub hoop_stress: f64,
    /// Contrainte thermique [Pa]
    pub thermal_stress: f64,
    /// Contrainte Von Mises combinée [Pa]
    pub von_mises_stress: f64,
    /// Limite élastique à la température de paroi [Pa]
    pub yield_strength: f64,
    /// Facteur de sécurité (yield / von_mises)
    pub safety_factor: f64,
    /// Nombre de cycles LCF estimé
    pub lcf_cycles: f64,
    /// Statut: "OK", "WARNING", "CRITICAL"
    pub status: String,
}

/// Effectue l'analyse structurelle complète d'une section de paroi.
///
/// # Arguments
/// * `p_gas` - Pression des gaz [Pa]
/// * `p_coolant` - Pression du coolant [Pa]
/// * `r_inner` - Rayon intérieur [m]
/// * `wall_thickness` - Épaisseur de paroi [m]
/// * `t_wall_hot` - Température paroi chaude [K]
/// * `t_wall_cold` - Température paroi froide [K]
/// * `material` - Propriétés du matériau
///
/// # Retourne
/// Résultat d'analyse avec statut
pub fn analyze_wall_section(
    p_gas: f64,
    p_coolant: f64,
    r_inner: f64,
    wall_thickness: f64,
    t_wall_hot: f64,
    t_wall_cold: f64,
    material: &MaterialProperties,
) -> StructuralResult {
    let r_outer = r_inner + wall_thickness;
    
    // Contrainte de pression (Lamé)
    let sigma_hoop = lame_hoop_stress(p_coolant, p_gas, r_inner, r_outer);
    
    // Contrainte thermique
    let sigma_thermal = thermal_stress(
        material.e_modulus,
        material.alpha,
        t_wall_hot - t_wall_cold,
        material.poisson_ratio,
    );
    
    // Von Mises (combinaison)
    let sigma_vm = von_mises_biaxial(sigma_hoop.abs(), sigma_thermal);
    
    // Limite élastique à la température chaude (là où c'est le pire)
    let sigma_y = material.yield_strength_at_temp(t_wall_hot);
    
    // Facteur de sécurité
    let safety_factor = if sigma_vm > 0.0 { sigma_y / sigma_vm } else { f64::INFINITY };
    
    // LCF si plastification
    let eps_plastic = plastic_strain_estimate(sigma_vm, sigma_y, material.e_modulus);
    let lcf_cycles = if eps_plastic > 0.0 {
        coffin_manson_cycles(2.0 * eps_plastic, material.eps_f_prime, material.coffin_c)
    } else {
        f64::INFINITY
    };
    
    // Statut
    let status = if safety_factor >= 1.5 {
        "OK".to_string()
    } else if safety_factor >= 1.0 {
        "WARNING".to_string()
    } else {
        "CRITICAL".to_string()
    };
    
    StructuralResult {
        hoop_stress: sigma_hoop,
        thermal_stress: sigma_thermal,
        von_mises_stress: sigma_vm,
        yield_strength: sigma_y,
        safety_factor,
        lcf_cycles,
        status,
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
//                    PROPRIÉTÉS MATÉRIAU
// ═══════════════════════════════════════════════════════════════════════════════

/// Propriétés mécaniques d'un matériau pour analyse structurelle
#[derive(Debug, Clone)]
pub struct MaterialProperties {
    /// Nom du matériau
    pub name: String,
    /// Module de Young [Pa]
    pub e_modulus: f64,
    /// Coefficient de Poisson [-]
    pub poisson_ratio: f64,
    /// Coefficient de dilatation thermique [1/K]
    pub alpha: f64,
    /// Limite élastique à 300K [Pa]
    pub yield_300k: f64,
    /// Limite élastique à 800K [Pa]
    pub yield_800k: f64,
    /// Coefficient de ductilité Coffin-Manson [-]
    pub eps_f_prime: f64,
    /// Exposant Coffin-Manson [-]
    pub coffin_c: f64,
}

impl MaterialProperties {
    /// Interpole la limite élastique à une température donnée.
    ///
    /// Modèle linéaire entre 300K et 800K, puis chute accélérée au-delà.
    pub fn yield_strength_at_temp(&self, temp_k: f64) -> f64 {
        if temp_k <= 300.0 {
            return self.yield_300k;
        }
        
        if temp_k >= 800.0 {
            // Chute accélérée au-delà de 800K
            let excess = (temp_k - 800.0) / 200.0; // Normalisé sur 200K
            let factor = (1.0 - excess * 0.8).max(0.1); // Min 10% de yield_800k
            return self.yield_800k * factor;
        }
        
        // Interpolation linéaire entre 300K et 800K
        let t = (temp_k - 300.0) / 500.0;
        self.yield_300k + t * (self.yield_800k - self.yield_300k)
    }
    
    /// Narloy-Z (Cu-3Ag-0.5Zr) - Alliage standard NASA
    pub fn narloy_z() -> Self {
        Self {
            name: "Narloy-Z".to_string(),
            e_modulus: 115e9,        // 115 GPa
            poisson_ratio: 0.34,
            alpha: 17.5e-6,          // 17.5 µm/m/K
            yield_300k: 240e6,       // 240 MPa
            yield_800k: 140e6,       // 140 MPa (chute significative)
            eps_f_prime: 0.15,
            coffin_c: -0.6,
        }
    }
    
    /// GRCop-42 (Cu-Cr-Nb) - Alliage avancé NASA Glenn
    pub fn grcop_42() -> Self {
        Self {
            name: "GRCop-42".to_string(),
            e_modulus: 115e9,
            poisson_ratio: 0.33,
            alpha: 17.8e-6,
            yield_300k: 260e6,       // 260 MPa
            yield_800k: 180e6,       // Meilleure tenue à chaud
            eps_f_prime: 0.20,       // Meilleure ductilité
            coffin_c: -0.55,
        }
    }
    
    /// Inconel 718 - Pour la jaquette structurelle
    pub fn inconel_718() -> Self {
        Self {
            name: "Inconel 718".to_string(),
            e_modulus: 200e9,        // 200 GPa
            poisson_ratio: 0.29,
            alpha: 13.0e-6,
            yield_300k: 1185e6,      // 1185 MPa
            yield_800k: 1050e6,      // Reste très résistant
            eps_f_prime: 0.10,
            coffin_c: -0.65,
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
//                                  TESTS
// ═══════════════════════════════════════════════════════════════════════════════

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_lame_vs_barlow() {
        // Pour paroi mince, Lamé ≈ Barlow
        let p_int = 3e6;  // 30 bar
        let p_ext = 0.0;
        let r_int = 0.05;
        let t = 0.001;  // 1 mm (D/t = 100, paroi mince)
        let r_ext = r_int + t;
        
        let sigma_lame = lame_hoop_stress(p_int, p_ext, r_int, r_ext);
        let sigma_barlow = barlow_hoop_stress(p_int, r_int, t);
        
        // Différence < 5%
        let diff = (sigma_lame - sigma_barlow).abs() / sigma_barlow;
        assert!(diff < 0.05, "Lamé vs Barlow: diff = {:.1}%", diff * 100.0);
    }
    
    #[test]
    fn test_lame_thick_wall() {
        // Pour paroi épaisse, Lamé > Barlow
        let p_int = 10e6;  // 100 bar
        let p_ext = 0.0;
        let r_int = 0.02;
        let t = 0.005;  // 5 mm (D/t = 8, paroi épaisse)
        let r_ext = r_int + t;
        
        let sigma_lame = lame_hoop_stress(p_int, p_ext, r_int, r_ext);
        let sigma_barlow = barlow_hoop_stress(p_int, r_int, t);
        
        // Lamé devrait être plus grand (concentration au bord interne)
        assert!(sigma_lame > sigma_barlow, "Lamé devrait être > Barlow pour paroi épaisse");
    }
    
    #[test]
    fn test_thermal_stress_order_of_magnitude() {
        // Cuivre avec ΔT = 400K devrait donner ~100-200 MPa
        let e = 115e9;       // Cuivre
        let alpha = 17e-6;   // 17 µm/m/K
        let delta_t = 400.0; // K
        let nu = 0.34;
        
        let sigma = thermal_stress(e, alpha, delta_t, nu);
        
        // σ ≈ 115e9 × 17e-6 × 400 / (2 × 0.66) ≈ 590 MPa (simplifié)
        // Formule exacte donne moins car facteur 2
        assert!(sigma > 100e6 && sigma < 1000e6,
            "Contrainte thermique = {:.0} MPa hors plage", sigma / 1e6);
    }
    
    #[test]
    fn test_von_mises_uniaxial() {
        // En uniaxial, Von Mises = contrainte appliquée
        let sigma = 100e6;
        let vm = von_mises_biaxial(sigma, 0.0);
        assert!((vm - sigma).abs() < 1.0, "Von Mises uniaxial incorrect");
    }
    
    #[test]
    fn test_coffin_manson_low_strain() {
        // Faible déformation plastique → beaucoup de cycles
        let eps = 0.001;  // 0.1%
        let nf = coffin_manson_cycles(eps, 0.15, -0.6);
        
        assert!(nf > 1000.0, "N_f = {} trop faible pour ε = 0.1%", nf);
    }
    
    #[test]
    fn test_coffin_manson_high_strain() {
        // Forte déformation plastique → peu de cycles
        let eps = 0.05;  // 5%
        let nf = coffin_manson_cycles(eps, 0.15, -0.6);
        
        assert!(nf < 100.0, "N_f = {} trop élevé pour ε = 5%", nf);
    }
    
    #[test]
    fn test_material_yield_interpolation() {
        let mat = MaterialProperties::narloy_z();
        
        // À 300K
        assert!((mat.yield_strength_at_temp(300.0) - mat.yield_300k).abs() < 1e6);
        
        // À 800K
        assert!((mat.yield_strength_at_temp(800.0) - mat.yield_800k).abs() < 1e6);
        
        // À 550K (milieu)
        let mid = mat.yield_strength_at_temp(550.0);
        let expected_mid = (mat.yield_300k + mat.yield_800k) / 2.0;
        assert!((mid - expected_mid).abs() < 10e6);
        
        // Au-delà de 800K, ça chute
        let hot = mat.yield_strength_at_temp(1000.0);
        assert!(hot < mat.yield_800k, "Yield doit chuter au-delà de 800K");
    }
    
    #[test]
    fn test_analyze_wall_section() {
        let mat = MaterialProperties::narloy_z();
        
        let result = analyze_wall_section(
            3e6,     // P_gas = 30 bar
            5e6,     // P_coolant = 50 bar
            0.03,    // R = 30 mm
            0.002,   // t = 2 mm
            900.0,   // T_hot = 900K
            600.0,   // T_cold = 600K
            &mat,
        );
        
        // Vérifications de cohérence
        assert!(result.hoop_stress.abs() > 0.0);
        assert!(result.thermal_stress > 0.0);
        assert!(result.von_mises_stress > 0.0);
        assert!(result.safety_factor > 0.0);
        
        // À 900K avec contraintes élevées, le status ne devrait pas être OK
        println!("Safety factor = {:.2}, Status = {}", result.safety_factor, result.status);
    }
}
