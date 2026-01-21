//! # Geometry Module - Génération de Contours de Tuyère
//!
//! Ce module génère les profils géométriques de tuyères de Laval utilisant
//! la méthode de Rao avec des courbes de Bézier pour un contour optimisé.
//!
//! ## Méthode de Génération
//!
//! Le profil est composé de trois sections:
//!
//! 1. **Chambre cylindrique** - Rayon constant `R_chamber`
//! 2. **Convergent** - Courbe cosinus lisse de `R_chamber` à `R_throat`
//! 3. **Divergent (Bell)** - Courbe de Bézier quadratique de `R_throat` à `R_exit`
//!
//! ## Références
//! - Rao, G.V.R. "Exhaust Nozzle Contour for Optimum Thrust", Jet Propulsion, 1958
//! - Huzel & Huang, "Modern Engineering for Design of Liquid-Propellant Rocket Engines"

use serde::{Deserialize, Serialize};
use std::f64::consts::PI;

// ═══════════════════════════════════════════════════════════════════════════════
//                            STRUCTURES DE DONNÉES
// ═══════════════════════════════════════════════════════════════════════════════

/// Profil géométrique complet d'une tuyère.
///
/// Contient les coordonnées axiales et radiales pour tracer le contour,
/// ainsi que les aires et rapports de section pour les calculs aérodynamiques.
#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct GeometryProfile {
    /// Positions axiales [m] (0 = entrée chambre, positif vers sortie)
    pub x: Vec<f64>,
    
    /// Rayons locaux [m]
    pub r: Vec<f64>,
    
    /// Aires de section [m²] = π × r²
    pub area: Vec<f64>,
    
    /// Rapports de section [-] = A / A_throat
    pub area_ratio: Vec<f64>,
}

/// Paramètres d'entrée pour la génération de géométrie.
///
/// Ces paramètres définissent complètement la forme de la tuyère.
#[derive(Debug, Serialize, Deserialize)]
pub struct GeometryParams {
    // ─────────────────────────────────────────────────────────────────────────
    //                          DIMENSIONS PRINCIPALES
    // ─────────────────────────────────────────────────────────────────────────
    
    /// Rayon au col [m] - Point le plus étroit de la tuyère
    ///
    /// C'est le paramètre dimensionnel fondamental. L'aire au col A* détermine
    /// le débit massique maximum (choked flow):
    /// ```text
    /// ṁ = A* × P_c / c* = A* × Γ × P_c × √(γ / (R × T_c))
    /// ```
    pub r_throat: f64,
    
    /// Longueur de la chambre de combustion [m]
    ///
    /// Liée au L* (longueur caractéristique) par:
    /// ```text
    /// L* = V_chambre / A_throat
    /// L_chambre ≈ L* × (A_throat / A_chambre)
    /// ```
    pub l_chamber: f64,
    
    /// Longueur du divergent [m]
    ///
    /// Pour une tuyère 80% bell:
    /// ```text
    /// L_nozzle ≈ 0.8 × (√ε - 1) × R_t / tan(15°)
    /// ```
    pub l_nozzle: f64,
    
    // ─────────────────────────────────────────────────────────────────────────
    //                          RAPPORTS DE SECTION
    // ─────────────────────────────────────────────────────────────────────────
    
    /// Rapport de contraction [-] = A_chambre / A_col
    ///
    /// Typiquement 2.5 à 4.0 pour les moteurs liquides.
    /// Affecte les pertes de pression dans la chambre.
    pub contraction_ratio: f64,
    
    /// Rapport d'expansion [-] = A_sortie / A_col
    ///
    /// Détermine la pression de sortie et l'efficacité de détente:
    /// - ε petit (~5-10): Optimal au niveau de la mer
    /// - ε grand (~50-100): Optimal dans le vide
    pub expansion_ratio: f64,
    
    // ─────────────────────────────────────────────────────────────────────────
    //                              ANGLES
    // ─────────────────────────────────────────────────────────────────────────
    
    /// Angle du convergent [degrés] - Non utilisé dans l'algorithme Bézier actuel
    #[allow(dead_code)]
    pub theta_conv: f64,
    
    /// Angle de sortie [degrés] (θ_e)
    ///
    /// Angle final du contour à la sortie. Typiquement 5-10° pour minimiser
    /// les pertes par divergence.
    pub theta_div: f64,
    
    /// Angle initial de tuyère [degrés] (θ_n)
    ///
    /// Angle au col côté divergent. Typiquement 25-35° pour une expansion rapide.
    /// Plus grand = tuyère plus courte mais plus de pertes.
    pub theta_n: f64,
    
    /// Type de tuyère: "bell" (Rao) ou "conical"
    pub nozzle_type: String,
}

impl Default for GeometryParams {
    /// Valeurs par défaut pour un moteur amateur typique (~10 kN)
    fn default() -> Self {
        Self {
            r_throat: 0.03,           // 30 mm
            l_chamber: 0.15,          // 150 mm
            l_nozzle: 0.20,           // 200 mm
            contraction_ratio: 3.0,   // A_c/A_t = 3
            expansion_ratio: 40.0,    // A_e/A_t = 40 (optimisé vide)
            theta_conv: 30.0,         // 30° (non utilisé)
            theta_div: 8.0,           // θ_e = 8° (angle de sortie)
            theta_n: 30.0,            // θ_n = 30° (angle initial)
            nozzle_type: "bell".to_string(),
        }
    }
}

impl GeometryParams {
    // ═══════════════════════════════════════════════════════════════════════
    //                    GÉNÉRATION DU PROFIL COMPLET
    // ═══════════════════════════════════════════════════════════════════════
    
    /// Génère le profil de contour complet en utilisant l'algorithme Bézier-Rao.
    ///
    /// # Algorithme
    ///
    /// 1. **Chambre** (20 points): Section cylindrique à rayon constant
    /// 2. **Convergent** (30 points): Courbe cosinus pour transition lisse
    /// 3. **Divergent** (50 points): Courbe de Bézier quadratique (méthode Rao)
    ///
    /// # Arguments
    /// * `_n_points` - Paramètre ignoré (le nombre de points est fixé à ~97)
    ///
    /// # Retourne
    /// `GeometryProfile` contenant les coordonnées et aires
    ///
    /// # Exemple
    /// ```ignore
    /// let params = GeometryParams::default();
    /// let profile = params.generate_profile(100);
    /// // profile.x contient les positions axiales
    /// // profile.r contient les rayons
    /// ```
    pub fn generate_profile(&self, _n_points: usize) -> GeometryProfile {
        // ─────────────────────────────────────────────────────────────────────
        // ÉTAPE 1: Calcul des rayons caractéristiques
        // ─────────────────────────────────────────────────────────────────────
        //
        // R_chamber = R_throat × √(contraction_ratio)
        // R_exit = R_throat × √(expansion_ratio)
        //
        // Note: Le rapport de section est proportionnel au carré du rayon
        // car A = π × R², donc A₁/A₂ = (R₁/R₂)²
        
        let r_chamber = self.r_throat * self.contraction_ratio.sqrt();
        let r_exit = self.r_throat * self.expansion_ratio.sqrt();
        
        // ─────────────────────────────────────────────────────────────────────
        // ÉTAPE 2: Conversion en mm pour cohérence avec l'algorithme Python
        // ─────────────────────────────────────────────────────────────────────
        
        let rt = self.r_throat * 1000.0;      // Rayon col [mm]
        let rc = r_chamber * 1000.0;           // Rayon chambre [mm]
        let re = r_exit * 1000.0;              // Rayon sortie [mm]
        let lc = self.l_chamber * 1000.0;      // Longueur chambre [mm]
        let lb = self.l_nozzle * 1000.0;       // Longueur divergent [mm]
        
        // Angles en radians
        let theta_n = self.theta_n.to_radians();  // Angle initial (30° typ.)
        let theta_e = self.theta_div.to_radians(); // Angle de sortie (8° typ.)
        
        // ─────────────────────────────────────────────────────────────────────
        // ÉTAPE 3: Longueur du convergent
        // ─────────────────────────────────────────────────────────────────────
        //
        // Formule empirique: L_conv = 1.5 × (R_chamber - R_throat)
        // Cette longueur assure une contraction progressive sans pertes
        // excessives.
        
        let l_conv = (rc - rt) * 1.5;
        
        // ─────────────────────────────────────────────────────────────────────
        // SECTION A: CHAMBRE CYLINDRIQUE
        // ─────────────────────────────────────────────────────────────────────
        //
        // Section à rayon constant. Les coordonnées X vont de -(L_c + L_conv)
        // jusqu'à -L_conv (le col étant à X = 0).
        
        let n_chamber = 20;
        let mut x_ch: Vec<f64> = Vec::with_capacity(n_chamber);
        let mut y_ch: Vec<f64> = Vec::with_capacity(n_chamber);
        
        for i in 0..n_chamber {
            let fraction = i as f64 / (n_chamber - 1) as f64;
            // X va de -(l_c + l_conv) à -l_conv
            let x = -(lc + l_conv) + l_conv * fraction;
            x_ch.push(x);
            y_ch.push(rc);  // Rayon constant = R_chamber
        }
        
        // ─────────────────────────────────────────────────────────────────────
        // SECTION B: CONVERGENT (COURBE COSINUS)
        // ─────────────────────────────────────────────────────────────────────
        //
        // Profil en cosinus pour une transition C1-continue (tangente continue):
        //
        //   R(x) = R_t + (R_c - R_t) × [1 - sin(π × t / 2)]
        //
        // où t = (x + L_conv) / L_conv ∈ [0, 1]
        //
        // À t=0 (début): R = R_chamber
        // À t=1 (col):   R = R_throat
        // dR/dx = 0 aux deux extrémités → transition lisse
        
        let n_conv = 30;
        let mut x_conv: Vec<f64> = Vec::with_capacity(n_conv);
        let mut y_conv: Vec<f64> = Vec::with_capacity(n_conv);
        
        for i in 0..n_conv {
            // X va de -L_conv à 0 (col)
            let x = -l_conv + l_conv * (i as f64 / (n_conv - 1) as f64);
            
            // Paramètre normalisé t ∈ [0, 1]
            let t = (x + l_conv) / l_conv;
            
            // Profil cosinus: commence à R_chamber, finit à R_throat
            let y = rt + (rc - rt) * (1.0 - (PI * t / 2.0).sin());
            
            x_conv.push(x);
            y_conv.push(y);
        }
        
        // ─────────────────────────────────────────────────────────────────────
        // SECTION C: DIVERGENT (COURBE DE BÉZIER QUADRATIQUE - MÉTHODE RAO)
        // ─────────────────────────────────────────────────────────────────────
        //
        // La courbe de Bézier quadratique est définie par 3 points:
        //   P₀ = (0, R_throat)      - Point au col
        //   P₁ = (x_ctrl, y_ctrl)   - Point de contrôle
        //   P₂ = (L_nozzle, R_exit) - Point de sortie
        //
        // Le point de contrôle P₁ est l'intersection des deux tangentes:
        //   - Tangente au col avec angle θ_n
        //   - Tangente à la sortie avec angle θ_e
        //
        // Équation de la courbe:
        //   B(t) = (1-t)² × P₀ + 2(1-t)t × P₁ + t² × P₂
        //
        // Cette formulation garantit:
        //   - Passage par P₀ et P₂
        //   - Tangente en P₀ dirigée vers P₁ (angle θ_n)
        //   - Tangente en P₂ dirigée depuis P₁ (angle θ_e)
        
        let n_bell = 50;
        let mut x_bell: Vec<f64> = Vec::with_capacity(n_bell);
        let mut y_bell: Vec<f64> = Vec::with_capacity(n_bell);
        
        // Points de contrôle Bézier
        let p0 = (0.0, rt);     // Col (x=0, r=R_throat)
        let p2 = (lb, re);      // Sortie (x=L_nozzle, r=R_exit)
        
        // Tangentes
        let tan_n = theta_n.tan();  // tan(θ_n) - pente initiale
        let tan_e = theta_e.tan();  // tan(θ_e) - pente finale
        
        // Calcul du point de contrôle P₁ par intersection des tangentes
        //
        // Ligne 1 (tangente au col): y = tan(θ_n) × x + R_t
        // Ligne 2 (tangente à la sortie): y = tan(θ_e) × (x - L_b) + R_e
        //                                 y = tan(θ_e) × x - tan(θ_e) × L_b + R_e
        //
        // Intersection:
        //   tan(θ_n) × x + R_t = tan(θ_e) × x - tan(θ_e) × L_b + R_e
        //   x × (tan(θ_n) - tan(θ_e)) = R_e - R_t - tan(θ_e) × L_b
        //   x = (R_e - R_t - tan(θ_e) × L_b) / (tan(θ_n) - tan(θ_e))
        
        let denom = tan_n - tan_e;
        let denom = if denom.abs() < 1e-9 { 1e-9 } else { denom }; // Éviter division par zéro
        
        let x_ctrl = (re - rt - tan_e * lb) / denom;
        let y_ctrl = tan_n * x_ctrl + rt;
        let p1 = (x_ctrl, y_ctrl);
        
        // Génération des points sur la courbe de Bézier
        for i in 0..n_bell {
            let t = i as f64 / (n_bell - 1) as f64;
            let one_minus_t = 1.0 - t;
            
            // Formule de Bézier quadratique: B(t) = (1-t)²P₀ + 2(1-t)tP₁ + t²P₂
            let x = one_minus_t * one_minus_t * p0.0
                  + 2.0 * one_minus_t * t * p1.0
                  + t * t * p2.0;
                  
            let y = one_minus_t * one_minus_t * p0.1
                  + 2.0 * one_minus_t * t * p1.1
                  + t * t * p2.1;
            
            x_bell.push(x);
            y_bell.push(y);
        }
        
        // ─────────────────────────────────────────────────────────────────────
        // ÉTAPE 4: FUSION DES PROFILS
        // ─────────────────────────────────────────────────────────────────────
        //
        // Les sections sont concaténées en évitant les doublons aux jonctions.
        
        let mut x_mm: Vec<f64> = Vec::new();
        let mut r_mm: Vec<f64> = Vec::new();
        
        // Chambre (tous les points)
        x_mm.extend(&x_ch);
        r_mm.extend(&y_ch);
        
        // Convergent (sans le premier point pour éviter doublon)
        x_mm.extend(&x_conv[1..]);
        r_mm.extend(&y_conv[1..]);
        
        // Divergent (sans le premier point pour éviter doublon au col)
        x_mm.extend(&x_bell[1..]);
        r_mm.extend(&y_bell[1..]);
        
        // ─────────────────────────────────────────────────────────────────────
        // ÉTAPE 5: CONVERSION EN MÈTRES ET CALCUL DES AIRES
        // ─────────────────────────────────────────────────────────────────────
        
        let x: Vec<f64> = x_mm.iter().map(|v| v / 1000.0).collect();
        let r: Vec<f64> = r_mm.iter().map(|v| v / 1000.0).collect();
        
        // Aire au col pour le calcul des rapports de section
        let a_throat = PI * self.r_throat * self.r_throat;
        
        // Aires locales: A = π × R²
        let area: Vec<f64> = r.iter().map(|&ri| PI * ri * ri).collect();
        
        // Rapports de section: ε = A / A*
        let area_ratio: Vec<f64> = area.iter().map(|&a| a / a_throat).collect();

        GeometryProfile {
            x,
            r,
            area,
            area_ratio,
        }
    }
}

// ═══════════════════════════════════════════════════════════════════════════════
//                                    TESTS
// ═══════════════════════════════════════════════════════════════════════════════

#[cfg(test)]
mod tests {
    use super::*;

    /// Test de génération de profil avec l'algorithme Bézier
    #[test]
    fn test_geometry_generation_bezier() {
        let params = GeometryParams {
            r_throat: 0.03,
            l_chamber: 0.15,
            l_nozzle: 0.20,
            contraction_ratio: 3.0,
            expansion_ratio: 40.0,
            theta_conv: 30.0,
            theta_div: 8.0,   // Angle de sortie
            theta_n: 30.0,    // Angle initial
            nozzle_type: "bell".to_string(),
        };

        let profile = params.generate_profile(100);

        // L'algorithme Bézier génère ~97 points (20 chambre + 29 conv + 49 bell)
        assert!(profile.x.len() > 90, "Pas assez de points générés");
        assert_eq!(profile.x.len(), profile.r.len(), "x et r doivent avoir la même longueur");
        
        // Tous les rayons doivent être positifs
        assert!(profile.r.iter().all(|&r| r > 0.0), "Rayon négatif détecté");
        
        // Le rayon minimum doit être proche du rayon au col
        let min_r = profile.r.iter().cloned().fold(f64::INFINITY, f64::min);
        assert!(
            (min_r - params.r_throat).abs() < 0.001,
            "Rayon minimum {} devrait être proche de R_throat {}",
            min_r,
            params.r_throat
        );
        
        // Le rayon maximum (sortie) doit être cohérent
        // Note: Pour ε=40 et CR=3, R_exit > R_chamber car √40 > √3
        let r_exit_expected = params.r_throat * params.expansion_ratio.sqrt();
        let max_r = profile.r.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
        assert!(
            (max_r - r_exit_expected).abs() < 0.01,
            "Rayon maximum {} devrait être proche de R_exit {}",
            max_r,
            r_exit_expected
        );
    }

    /// Test des valeurs par défaut
    #[test]
    fn test_default_params() {
        let params = GeometryParams::default();
        
        assert_eq!(params.r_throat, 0.03);
        assert_eq!(params.theta_n, 30.0);
        assert_eq!(params.theta_div, 8.0);
        assert_eq!(params.contraction_ratio, 3.0);
        assert_eq!(params.expansion_ratio, 40.0);
    }
    
    /// Test de cohérence des aires
    #[test]
    fn test_area_consistency() {
        let params = GeometryParams::default();
        let profile = params.generate_profile(100);
        
        // Vérifier que area = π × r² pour chaque point
        for (i, (&a, &r)) in profile.area.iter().zip(profile.r.iter()).enumerate() {
            let expected_area = std::f64::consts::PI * r * r;
            assert!(
                (a - expected_area).abs() < 1e-10,
                "Incohérence aire au point {}: {} vs {}",
                i, a, expected_area
            );
        }
    }
    
    /// Test des rapports de section
    #[test]
    fn test_area_ratio() {
        let params = GeometryParams::default();
        let profile = params.generate_profile(100);
        
        // Trouver le rapport de section minimum (devrait être ~1 au col)
        let min_ar = profile.area_ratio.iter().cloned().fold(f64::INFINITY, f64::min);
        assert!(
            (min_ar - 1.0).abs() < 0.1,
            "Rapport de section minimum {} devrait être proche de 1.0",
            min_ar
        );
        
        // Le rapport de section max (sortie) devrait être proche de expansion_ratio
        let max_ar = profile.area_ratio.iter().cloned().fold(f64::NEG_INFINITY, f64::max);
        assert!(
            (max_ar - params.expansion_ratio).abs() < 1.0,
            "Rapport de section max {} devrait être proche de {}",
            max_ar,
            params.expansion_ratio
        );
    }
}
