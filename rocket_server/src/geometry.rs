use serde::{Deserialize, Serialize};


#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct GeometryProfile {
    pub x: Vec<f64>,          // Axial positions
    pub r: Vec<f64>,          // Radii
    pub area: Vec<f64>,       // Cross-sectional areas
    pub area_ratio: Vec<f64>, // Area ratios (A/A*)
}

#[derive(Debug, Serialize, Deserialize)]
pub struct GeometryParams {
    pub r_throat: f64,
    pub l_chamber: f64,
    pub l_nozzle: f64,
    pub contraction_ratio: f64,
    pub expansion_ratio: f64,
    pub theta_conv: f64,     // deg - convergent angle (not used in new algo)
    pub theta_div: f64,      // deg - divergent angle (theta_e)
    pub theta_n: f64,        // deg - initial nozzle angle (optional, default 30°)
    pub nozzle_type: String, // "conical" or "bell"
}

impl Default for GeometryParams {
    fn default() -> Self {
        Self {
            r_throat: 0.03,
            l_chamber: 0.15,
            l_nozzle: 0.20,
            contraction_ratio: 3.0,
            expansion_ratio: 40.0,
            theta_conv: 30.0,
            theta_div: 8.0,   // theta_e - exit angle
            theta_n: 30.0,    // initial nozzle angle
            nozzle_type: "bell".to_string(),
        }
    }
}

impl GeometryParams {
    /// Génère le profil de contour en utilisant l'algorithme Bézier de l'ancienne version Python
    /// Basé sur la méthode de Rao pour les tuyères bell optimisées
    pub fn generate_profile(&self, n_points: usize) -> GeometryProfile {
        let r_chamber = self.r_throat * self.contraction_ratio.sqrt();
        let r_exit = self.r_throat * self.expansion_ratio.sqrt();
        
        // Convert to mm internally for consistency with Python (then back to m)
        let rt = self.r_throat * 1000.0;  // mm
        let rc = r_chamber * 1000.0;       // mm
        let re = r_exit * 1000.0;          // mm
        let lc = self.l_chamber * 1000.0;  // mm
        let lb = self.l_nozzle * 1000.0;   // mm
        
        // Angles in radians
        let theta_n = self.theta_n.to_radians();  // Initial nozzle angle (30° typical)
        let theta_e = self.theta_div.to_radians(); // Exit angle (8-15° typical)
        
        // === CONVERGENT: Longueur basée sur différence de rayons ===
        let l_conv = (rc - rt) * 1.5;
        
        // === CHAMBRE CYLINDRIQUE ===
        let n_chamber = 20;
        let mut x_ch: Vec<f64> = Vec::with_capacity(n_chamber);
        let mut y_ch: Vec<f64> = Vec::with_capacity(n_chamber);
        for i in 0..n_chamber {
            let x = -(lc + l_conv) + (l_conv) * (i as f64 / (n_chamber - 1) as f64);
            x_ch.push(x);
            y_ch.push(rc);  // Rayon constant dans la chambre
        }
        
        // === CONVERGENT avec courbe cosinus (lisse) ===
        let n_conv = 30;
        let mut x_conv: Vec<f64> = Vec::with_capacity(n_conv);
        let mut y_conv: Vec<f64> = Vec::with_capacity(n_conv);
        for i in 0..n_conv {
            let x = -l_conv + l_conv * (i as f64 / (n_conv - 1) as f64);
            let t = (x + l_conv) / l_conv;
            let y = rt + (rc - rt) * (1.0 - (std::f64::consts::PI * t / 2.0).sin());
            x_conv.push(x);
            y_conv.push(y);
        }
        
        // === DIVERGENT avec courbe de Bézier quadratique (méthode Rao) ===
        let n_bell = 50;
        let mut x_bell: Vec<f64> = Vec::with_capacity(n_bell);
        let mut y_bell: Vec<f64> = Vec::with_capacity(n_bell);
        
        // Points de contrôle Bézier
        let p0 = (0.0, rt);           // Point au col
        let p2 = (lb, re);            // Point de sortie
        let tn = theta_n.tan();       // tan(angle initial)
        let te = theta_e.tan();       // tan(angle de sortie)
        
        // Calcul du point de contrôle P1 (intersection des tangentes)
        let denom = tn - te;
        let denom = if denom.abs() < 1e-9 { 1e-9 } else { denom };
        let x_int = (re - rt - te * lb) / denom;
        let p1 = (x_int, tn * x_int + rt);
        
        // Courbe de Bézier quadratique: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
        for i in 0..n_bell {
            let t = i as f64 / (n_bell - 1) as f64;
            let one_minus_t = 1.0 - t;
            
            let x = one_minus_t * one_minus_t * p0.0 
                  + 2.0 * one_minus_t * t * p1.0 
                  + t * t * p2.0;
            let y = one_minus_t * one_minus_t * p0.1 
                  + 2.0 * one_minus_t * t * p1.1 
                  + t * t * p2.1;
            
            x_bell.push(x);
            y_bell.push(y);
        }
        
        // === FUSION DES PROFILS ===
        let mut x_mm: Vec<f64> = Vec::new();
        let mut r_mm: Vec<f64> = Vec::new();
        
        // Chambre
        x_mm.extend(&x_ch);
        r_mm.extend(&y_ch);
        
        // Convergent (skip first point to avoid duplicate)
        x_mm.extend(&x_conv[1..]);
        r_mm.extend(&y_conv[1..]);
        
        // Bell/Divergent (skip first point to avoid duplicate at throat)
        x_mm.extend(&x_bell[1..]);
        r_mm.extend(&y_bell[1..]);
        
        // Convert back to meters and calculate areas
        let x: Vec<f64> = x_mm.iter().map(|v| v / 1000.0).collect();
        let r: Vec<f64> = r_mm.iter().map(|v| v / 1000.0).collect();
        
        let a_throat = std::f64::consts::PI * self.r_throat * self.r_throat;
        let area: Vec<f64> = r.iter().map(|&ri| std::f64::consts::PI * ri * ri).collect();
        let area_ratio: Vec<f64> = area.iter().map(|&a| a / a_throat).collect();

        GeometryProfile {
            x,
            r,
            area,
            area_ratio,
        }
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_geometry_generation_bezier() {
        let params = GeometryParams {
            r_throat: 0.03,
            l_chamber: 0.15,
            l_nozzle: 0.20,
            contraction_ratio: 3.0,
            expansion_ratio: 40.0,
            theta_conv: 30.0,
            theta_div: 8.0,   // Exit angle
            theta_n: 30.0,    // Initial nozzle angle
            nozzle_type: "bell".to_string(),
        };

        let profile = params.generate_profile(100);

        // Bézier algorithm generates ~97 points (20 chamber + 29 conv + 49 bell)
        assert!(profile.x.len() > 90);
        assert_eq!(profile.x.len(), profile.r.len());
        assert!(profile.r.iter().all(|&r| r > 0.0));
        
        // Verify throat is at minimum radius
        let min_r = profile.r.iter().cloned().fold(f64::INFINITY, f64::min);
        assert!((min_r - params.r_throat).abs() < 0.001);
    }

    #[test]
    fn test_default_params() {
        let params = GeometryParams::default();
        assert_eq!(params.r_throat, 0.03);
        assert_eq!(params.theta_n, 30.0);
    }
}
