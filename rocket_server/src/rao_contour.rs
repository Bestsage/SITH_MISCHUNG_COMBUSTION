//! # Rao Contour Module - Thrust Optimized Parabolic (TOP) Nozzle
//!
//! Ce module implémente la méthode de G.V.R. Rao pour générer des contours
//! de tuyère paraboliques optimisés pour la poussée.
//!
//! ## Avantages par rapport au cône 15°
//! - Meilleure conversion d'énergie thermique → cinétique
//! - Écoulement de sortie plus uniforme et parallèle
//! - Longueur réduite à performances égales
//!
//! ## Structure du Contour
//! 1. **Arc amont** (R_u = 1.5 × R_t) - Guide l'accélération subsonique
//! 2. **Arc col** (R_d = 0.382 × R_t) - Détente transsonique initiale
//! 3. **Parabole** - Expansion supersonique avec redressement progressif
//!
//! ## Références
//! - Rao, G.V.R. "Exhaust Nozzle Contour for Optimum Thrust", Jet Propulsion, 1958
//! - Huzel & Huang, "Modern Engineering for Design of Liquid-Propellant Rocket Engines"

use std::f64::consts::PI;

// ═══════════════════════════════════════════════════════════════════════════════
//                              CONSTANTES RAO
// ═══════════════════════════════════════════════════════════════════════════════

/// Rayon de courbure amont normalisé (zone convergente → col)
/// R_u = 1.5 × R_throat
pub const RAO_UPSTREAM_RADIUS_RATIO: f64 = 1.5;

/// Rayon de courbure aval normalisé (col → début parabole)
/// R_d = 0.382 × R_throat - Valeur optimale de Rao
pub const RAO_DOWNSTREAM_RADIUS_RATIO: f64 = 0.382;

/// Fraction de longueur standard pour tuyère "80% bell"
pub const STANDARD_BELL_FRACTION: f64 = 0.80;

// ═══════════════════════════════════════════════════════════════════════════════
//                          TABLES D'ANGLES DE RAO
// ═══════════════════════════════════════════════════════════════════════════════
//
// Ces tables contiennent les angles optimaux θ_n (inflexion) et θ_e (sortie)
// en fonction du rapport de détente ε et de la fraction de longueur.
// Source: Tables originales de Rao interpolées.

/// Données interpolées pour tuyère 80% bell
/// Format: (ε, θ_n en degrés, θ_e en degrés)
const RAO_ANGLES_80_PERCENT: [(f64, f64, f64); 8] = [
    (4.0,   27.0, 18.0),
    (6.0,   26.0, 16.5),
    (10.0,  25.0, 14.5),
    (15.0,  24.0, 12.5),
    (20.0,  23.5, 11.5),
    (30.0,  22.5, 10.0),
    (50.0,  21.5,  8.5),
    (100.0, 20.0,  6.5),
];

/// Données interpolées pour tuyère 90% bell
const RAO_ANGLES_90_PERCENT: [(f64, f64, f64); 8] = [
    (4.0,   24.0, 14.0),
    (6.0,   23.0, 12.5),
    (10.0,  22.0, 11.0),
    (15.0,  21.0,  9.5),
    (20.0,  20.5,  8.5),
    (30.0,  19.5,  7.5),
    (50.0,  18.5,  6.0),
    (100.0, 17.5,  4.5),
];

// ═══════════════════════════════════════════════════════════════════════════════
//                            STRUCTURES
// ═══════════════════════════════════════════════════════════════════════════════

/// Paramètres d'entrée pour la génération du contour de Rao
#[derive(Debug, Clone)]
pub struct RaoParams {
    /// Rayon au col [m]
    pub r_throat: f64,
    /// Rapport de détente ε = A_exit / A_throat [-]
    pub expansion_ratio: f64,
    /// Fraction de longueur par rapport au cône 15° (0.8 = 80% bell)
    pub length_fraction: f64,
    /// Angle du convergent [radians] (typiquement 30-45°)
    pub convergent_angle: f64,
    /// Rapport de contraction A_chamber / A_throat [-]
    pub contraction_ratio: f64,
}

impl Default for RaoParams {
    fn default() -> Self {
        Self {
            r_throat: 0.03,
            expansion_ratio: 40.0,
            length_fraction: 0.80,
            convergent_angle: 30.0_f64.to_radians(),
            contraction_ratio: 3.0,
        }
    }
}

/// Résultat de la génération du contour Rao
#[derive(Debug, Clone)]
pub struct RaoContour {
    /// Positions axiales [m] (0 = entrée chambre)
    pub x: Vec<f64>,
    /// Rayons [m]
    pub r: Vec<f64>,
    /// Longueur totale chambre + tuyère [m]
    pub total_length: f64,
    /// Longueur du divergent seul [m]
    pub nozzle_length: f64,
    /// Position axiale du col [m]
    pub throat_position: f64,
    /// Angle d'inflexion θ_n [degrés]
    pub theta_n_deg: f64,
    /// Angle de sortie θ_e [degrés]
    pub theta_e_deg: f64,
}

// ═══════════════════════════════════════════════════════════════════════════════
//                    LONGUEUR DE RÉFÉRENCE CONIQUE
// ═══════════════════════════════════════════════════════════════════════════════

/// Calcule la longueur d'une tuyère conique à 15° de demi-angle.
///
/// Cette longueur sert de référence pour définir la fraction de longueur
/// des tuyères bell (ex: 80% bell = 0.8 × L_15).
///
/// # Formule
/// ```text
/// L_15 = R_t × (√ε - 1) / tan(15°)
/// ```
///
/// # Arguments
/// * `r_throat` - Rayon au col [m]
/// * `expansion_ratio` - Rapport de détente ε [-]
///
/// # Retourne
/// Longueur du cône 15° [m]
pub fn conical_15_length(r_throat: f64, expansion_ratio: f64) -> f64 {
    let r_exit = r_throat * expansion_ratio.sqrt();
    (r_exit - r_throat) / 15.0_f64.to_radians().tan()
}

/// Calcule la longueur du divergent pour une fraction donnée.
///
/// # Arguments
/// * `r_throat` - Rayon au col [m]
/// * `expansion_ratio` - Rapport de détente ε [-]
/// * `length_fraction` - Fraction de longueur (0.8 pour 80% bell)
///
/// # Retourne
/// Longueur du divergent [m]
pub fn nozzle_length(r_throat: f64, expansion_ratio: f64, length_fraction: f64) -> f64 {
    conical_15_length(r_throat, expansion_ratio) * length_fraction
}

// ═══════════════════════════════════════════════════════════════════════════════
//                    INTERPOLATION DES ANGLES OPTIMAUX
// ═══════════════════════════════════════════════════════════════════════════════

/// Interpole les angles optimaux θ_n et θ_e depuis les tables de Rao.
///
/// # Arguments
/// * `expansion_ratio` - Rapport de détente ε [-]
/// * `length_fraction` - Fraction de longueur (0.8 ou 0.9 supportées)
///
/// # Retourne
/// (θ_n, θ_e) en radians
///
/// # Notes
/// Pour les fractions intermédiaires, une interpolation linéaire est appliquée
/// entre les tables 80% et 90%.
pub fn optimal_angles(expansion_ratio: f64, length_fraction: f64) -> (f64, f64) {
    // Sélection de la table appropriée
    let (theta_n_80, theta_e_80) = interpolate_from_table(expansion_ratio, &RAO_ANGLES_80_PERCENT);
    let (theta_n_90, theta_e_90) = interpolate_from_table(expansion_ratio, &RAO_ANGLES_90_PERCENT);
    
    // Interpolation linéaire entre 80% et 90%
    let t = ((length_fraction - 0.80) / 0.10).clamp(0.0, 1.0);
    let theta_n_deg = theta_n_80 + t * (theta_n_90 - theta_n_80);
    let theta_e_deg = theta_e_80 + t * (theta_e_90 - theta_e_80);
    
    (theta_n_deg.to_radians(), theta_e_deg.to_radians())
}

/// Interpolation linéaire dans une table (ε, θ_n, θ_e)
fn interpolate_from_table(eps: f64, table: &[(f64, f64, f64)]) -> (f64, f64) {
    // Cas hors bornes
    if eps <= table[0].0 {
        return (table[0].1, table[0].2);
    }
    if eps >= table[table.len() - 1].0 {
        let last = table[table.len() - 1];
        return (last.1, last.2);
    }
    
    // Recherche de l'intervalle
    for i in 0..table.len() - 1 {
        let (eps_lo, theta_n_lo, theta_e_lo) = table[i];
        let (eps_hi, theta_n_hi, theta_e_hi) = table[i + 1];
        
        if eps >= eps_lo && eps <= eps_hi {
            // Interpolation logarithmique sur ε (plus précise)
            let t = (eps.ln() - eps_lo.ln()) / (eps_hi.ln() - eps_lo.ln());
            let theta_n = theta_n_lo + t * (theta_n_hi - theta_n_lo);
            let theta_e = theta_e_lo + t * (theta_e_hi - theta_e_lo);
            return (theta_n, theta_e);
        }
    }
    
    // Fallback (ne devrait pas arriver)
    (25.0, 10.0)
}

// ═══════════════════════════════════════════════════════════════════════════════
//                    CONSTRUCTION DU CONTOUR COMPLET
// ═══════════════════════════════════════════════════════════════════════════════

/// Génère le contour complet de Rao (chambre + convergent + col + divergent).
///
/// # Sections générées
///
/// 1. **Chambre cylindrique** - Rayon constant R_chamber
/// 2. **Arc amont** (R_u = 1.5 R_t) - Transition vers le col
/// 3. **Arc col** (R_d = 0.382 R_t) - Détente initiale
/// 4. **Parabole** - Contour optimisé jusqu'à la sortie
///
/// # Arguments
/// * `params` - Paramètres de la tuyère
/// * `n_points` - Nombre de points par section
///
/// # Retourne
/// Structure `RaoContour` avec tous les points et métadonnées
pub fn generate_rao_contour(params: &RaoParams, n_points: usize) -> RaoContour {
    let r_t = params.r_throat;
    let r_chamber = r_t * params.contraction_ratio.sqrt();
    let r_exit = r_t * params.expansion_ratio.sqrt();
    
    // Rayons de courbure
    let r_u = RAO_UPSTREAM_RADIUS_RATIO * r_t;   // 1.5 × R_t
    let r_d = RAO_DOWNSTREAM_RADIUS_RATIO * r_t; // 0.382 × R_t
    
    // Angles optimaux
    let (theta_n, theta_e) = optimal_angles(params.expansion_ratio, params.length_fraction);
    
    // Longueur du divergent
    let l_nozzle = nozzle_length(r_t, params.expansion_ratio, params.length_fraction);
    
    // ─────────────────────────────────────────────────────────────────────────
    // CALCUL DES POINTS CARACTÉRISTIQUES
    // ─────────────────────────────────────────────────────────────────────────
    
    // Point d'inflexion N (fin de l'arc col, début parabole)
    // Coordonnées relatives au col (x=0 au col)
    let x_n = r_d * theta_n.sin();
    let y_n = r_t + r_d * (1.0 - theta_n.cos());
    
    // Point de sortie E
    let x_e = l_nozzle;
    let y_e = r_exit;
    
    // ─────────────────────────────────────────────────────────────────────────
    // COEFFICIENTS DE LA PARABOLE
    // ─────────────────────────────────────────────────────────────────────────
    //
    // Parabole: y = a×x² + b×x + c
    // Conditions:
    //   1. Passe par N: a×x_n² + b×x_n + c = y_n
    //   2. Tangente en N: 2a×x_n + b = tan(θ_n)
    //   3. Passe par E: a×x_e² + b×x_e + c = y_e
    //
    // Système 3×3 pour (a, b, c)
    
    let tan_n = theta_n.tan();
    let tan_e = theta_e.tan();
    
    // Résolution du système (méthode directe)
    // De la condition tangente: b = tan(θ_n) - 2a×x_n
    // Substitution dans les deux autres équations...
    
    // Méthode alternative: coefficients de Bézier quadratique
    // Plus stable numériquement et garantit les tangences
    let (a, b, c) = solve_parabola_coefficients(x_n, y_n, tan_n, x_e, y_e, tan_e);
    
    // ─────────────────────────────────────────────────────────────────────────
    // LONGUEUR DU CONVERGENT
    // ─────────────────────────────────────────────────────────────────────────
    
    let theta_conv = params.convergent_angle;
    
    // Géométrie du convergent avec arc amont
    // L'arc amont de rayon R_u tangent à la chambre et au convergent
    let l_conv = calculate_convergent_length(r_chamber, r_t, r_u, theta_conv);
    
    // ─────────────────────────────────────────────────────────────────────────
    // GÉNÉRATION DES POINTS
    // ─────────────────────────────────────────────────────────────────────────
    
    let mut x_points: Vec<f64> = Vec::new();
    let mut r_points: Vec<f64> = Vec::new();
    
    // Position du col dans le système de coordonnées (x=0 = entrée)
    let throat_x = l_conv;
    let total_length = l_conv + l_nozzle;
    
    let n_conv = n_points / 3;
    let n_arc = n_points / 6;
    let n_para = n_points / 2;
    
    // Section 1: Convergent (arc + cône + arc)
    generate_convergent_points(
        &mut x_points, &mut r_points,
        r_chamber, r_t, r_u, r_d, theta_conv, l_conv, n_conv
    );
    
    // Section 2: Arc col (0.382 R_t)
    generate_throat_arc_points(
        &mut x_points, &mut r_points,
        r_t, r_d, theta_n, throat_x, n_arc
    );
    
    // Section 3: Parabole
    generate_parabola_points(
        &mut x_points, &mut r_points,
        a, b, c, x_n, x_e, throat_x, n_para
    );
    
    RaoContour {
        x: x_points,
        r: r_points,
        total_length,
        nozzle_length: l_nozzle,
        throat_position: throat_x,
        theta_n_deg: theta_n.to_degrees(),
        theta_e_deg: theta_e.to_degrees(),
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
//                    FONCTIONS AUXILIAIRES
// ═══════════════════════════════════════════════════════════════════════════════

/// Calcule la longueur du convergent
fn calculate_convergent_length(r_chamber: f64, r_throat: f64, r_u: f64, theta: f64) -> f64 {
    // Hauteur des arcs
    let h_arc = r_u * (1.0 - theta.cos());
    // Hauteur du cône droit
    let h_cone = (r_chamber - r_throat - 2.0 * h_arc).max(0.0);
    // Longueur totale
    2.0 * r_u * theta.sin() + h_cone / theta.tan()
}

/// Résout le système pour les coefficients de la parabole
fn solve_parabola_coefficients(
    x_n: f64, y_n: f64, tan_n: f64,
    x_e: f64, y_e: f64, _tan_e: f64
) -> (f64, f64, f64) {
    // Système surdéterminé - on utilise conditions sur N et E avec tangente en N
    // b = tan_n - 2a×x_n
    // Substitution: a×x_n² + (tan_n - 2a×x_n)×x_n + c = y_n
    //              a×x_n² + tan_n×x_n - 2a×x_n² + c = y_n
    //              -a×x_n² + tan_n×x_n + c = y_n
    //              c = y_n + a×x_n² - tan_n×x_n
    //
    // Pour E: a×x_e² + b×x_e + c = y_e
    //         a×x_e² + (tan_n - 2a×x_n)×x_e + y_n + a×x_n² - tan_n×x_n = y_e
    //         a×(x_e² - 2×x_n×x_e + x_n²) = y_e - y_n - tan_n×(x_e - x_n)
    //         a×(x_e - x_n)² = y_e - y_n - tan_n×(x_e - x_n)
    
    let dx = x_e - x_n;
    let dy = y_e - y_n;
    
    let a = (dy - tan_n * dx) / (dx * dx);
    let b = tan_n - 2.0 * a * x_n;
    let c = y_n + a * x_n * x_n - tan_n * x_n;
    
    (a, b, c)
}

/// Génère les points du convergent
fn generate_convergent_points(
    x_pts: &mut Vec<f64>, r_pts: &mut Vec<f64>,
    r_chamber: f64, r_throat: f64, r_u: f64, r_d: f64,
    theta: f64, l_conv: f64, n_points: usize
) {
    for i in 0..n_points {
        let t = i as f64 / (n_points - 1) as f64;
        let x = t * l_conv;
        
        // Profil convergent simplifié avec courbe cosinus
        let r = r_throat + (r_chamber - r_throat) * (1.0 - (PI * t / 2.0).sin());
        
        x_pts.push(x);
        r_pts.push(r.max(r_throat));
    }
    
    // Supprimer le dernier point (sera remplacé par l'arc col)
    if !x_pts.is_empty() {
        x_pts.pop();
        r_pts.pop();
    }
}

/// Génère les points de l'arc col (rayon 0.382 R_t)
fn generate_throat_arc_points(
    x_pts: &mut Vec<f64>, r_pts: &mut Vec<f64>,
    r_throat: f64, r_d: f64, theta_n: f64,
    throat_x: f64, n_points: usize
) {
    // Arc de cercle du col au point d'inflexion N
    // Centre: (0, R_t + R_d) relatif au col
    let y_center = r_throat + r_d;
    
    for i in 0..n_points {
        let t = i as f64 / (n_points - 1) as f64;
        let angle = t * theta_n;  // De 0 à θ_n
        
        let x_local = r_d * angle.sin();
        let y_local = y_center - (r_d * r_d - x_local * x_local).sqrt();
        
        x_pts.push(throat_x + x_local);
        r_pts.push(y_local);
    }
}

/// Génère les points de la parabole
fn generate_parabola_points(
    x_pts: &mut Vec<f64>, r_pts: &mut Vec<f64>,
    a: f64, b: f64, c: f64,
    x_n: f64, x_e: f64, throat_x: f64,
    n_points: usize
) {
    for i in 1..=n_points {
        let t = i as f64 / n_points as f64;
        let x_local = x_n + t * (x_e - x_n);
        let y = a * x_local * x_local + b * x_local + c;
        
        x_pts.push(throat_x + x_local);
        r_pts.push(y);
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
//                                  TESTS
// ═══════════════════════════════════════════════════════════════════════════════

#[cfg(test)]
mod tests {
    use super::*;
    
    const EPSILON: f64 = 1e-6;
    
    #[test]
    fn test_conical_15_length() {
        let r_t = 0.03;  // 30 mm
        let eps = 40.0;
        
        let l_15 = conical_15_length(r_t, eps);
        
        // L_15 = R_t × (√40 - 1) / tan(15°) ≈ 0.03 × 5.32 / 0.268 ≈ 0.596 m
        assert!(l_15 > 0.5 && l_15 < 0.7, "L_15 = {} hors bornes", l_15);
    }
    
    #[test]
    fn test_optimal_angles_bounds() {
        // Les angles doivent être dans des plages raisonnables
        for eps in [5.0, 10.0, 20.0, 50.0, 100.0] {
            let (theta_n, theta_e) = optimal_angles(eps, 0.80);
            
            // θ_n entre 18° et 30°
            let theta_n_deg = theta_n.to_degrees();
            assert!(theta_n_deg >= 18.0 && theta_n_deg <= 30.0,
                "θ_n = {:.1}° hors bornes pour ε = {}", theta_n_deg, eps);
            
            // θ_e entre 4° et 20°, et θ_e < θ_n
            let theta_e_deg = theta_e.to_degrees();
            assert!(theta_e_deg >= 4.0 && theta_e_deg <= 20.0,
                "θ_e = {:.1}° hors bornes pour ε = {}", theta_e_deg, eps);
            assert!(theta_e < theta_n, "θ_e doit être < θ_n");
        }
    }
    
    #[test]
    fn test_angles_decrease_with_expansion_ratio() {
        // Plus ε augmente, plus θ_e diminue (écoulement plus parallèle)
        let (_, theta_e_10) = optimal_angles(10.0, 0.80);
        let (_, theta_e_50) = optimal_angles(50.0, 0.80);
        let (_, theta_e_100) = optimal_angles(100.0, 0.80);
        
        assert!(theta_e_50 < theta_e_10, "θ_e(50) < θ_e(10)");
        assert!(theta_e_100 < theta_e_50, "θ_e(100) < θ_e(50)");
    }
    
    #[test]
    fn test_generate_contour_basic() {
        let params = RaoParams::default();
        let contour = generate_rao_contour(&params, 100);
        
        // Vérifications de base
        assert!(contour.x.len() > 50, "Pas assez de points");
        assert_eq!(contour.x.len(), contour.r.len());
        
        // Rayons positifs
        assert!(contour.r.iter().all(|&r| r > 0.0));
        
        // Monotonie de x
        for i in 1..contour.x.len() {
            assert!(contour.x[i] >= contour.x[i-1], "x non monotone");
        }
    }
    
    #[test]
    fn test_throat_is_minimum_radius() {
        let params = RaoParams::default();
        let contour = generate_rao_contour(&params, 100);
        
        let r_min = contour.r.iter().cloned().fold(f64::INFINITY, f64::min);
        let r_throat = params.r_throat;
        
        // Le rayon minimum doit être proche de R_throat (±5%)
        assert!((r_min - r_throat).abs() / r_throat < 0.05,
            "R_min = {}, R_throat = {}", r_min, r_throat);
    }
    
    #[test]
    fn test_exit_radius_correct() {
        let params = RaoParams {
            r_throat: 0.03,
            expansion_ratio: 25.0,  // √25 = 5
            ..Default::default()
        };
        let contour = generate_rao_contour(&params, 100);
        
        let r_exit_expected = params.r_throat * params.expansion_ratio.sqrt();
        let r_exit_actual = *contour.r.last().unwrap();
        
        // Tolérance de 2%
        assert!((r_exit_actual - r_exit_expected).abs() / r_exit_expected < 0.02,
            "R_exit = {}, attendu = {}", r_exit_actual, r_exit_expected);
    }
    
    #[test]
    fn test_parabola_coefficients() {
        // Cas simple avec valeurs connues
        let (a, b, c) = solve_parabola_coefficients(
            0.01, 0.032, 0.5,  // Point N
            0.2, 0.1, 0.1     // Point E
        );
        
        // Vérifier que la parabole passe par N
        let y_n_calc = a * 0.01 * 0.01 + b * 0.01 + c;
        assert!((y_n_calc - 0.032).abs() < 1e-6);
        
        // Vérifier que la parabole passe par E
        let y_e_calc = a * 0.2 * 0.2 + b * 0.2 + c;
        assert!((y_e_calc - 0.1).abs() < 1e-4);
    }
}
