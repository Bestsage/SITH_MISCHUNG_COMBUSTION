use serde::{Deserialize, Serialize};
use std::f64::consts::PI;

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
    pub theta_conv: f64,     // deg
    pub theta_div: f64,      // deg
    pub nozzle_type: String, // "conical" or "bell"
}

impl GeometryParams {
    pub fn generate_profile(&self, n_points: usize) -> GeometryProfile {
        let r_chamber = self.r_throat * self.contraction_ratio.sqrt();
        let r_exit = self.r_throat * self.expansion_ratio.sqrt();

        let mut x = Vec::with_capacity(n_points);
        let mut r = Vec::with_capacity(n_points);

        // Chamber (converging section)
        let n_chamber = n_points / 3;
        for i in 0..n_chamber {
            let frac = i as f64 / n_chamber as f64;
            let x_pos = -self.l_chamber * (1.0 - frac);
            let r_pos = r_chamber - (r_chamber - self.r_throat) * frac.powi(2);
            x.push(x_pos);
            r.push(r_pos);
        }

        // Throat
        x.push(0.0);
        r.push(self.r_throat);

        // Nozzle (diverging section)
        let n_nozzle = n_points - n_chamber - 1;
        for i in 1..=n_nozzle {
            let frac = i as f64 / n_nozzle as f64;
            let x_pos = self.l_nozzle * frac;

            let r_pos = if self.nozzle_type == "bell" {
                // Bell nozzle approximation (parabolic)
                self.r_throat + (r_exit - self.r_throat) * frac.powf(0.7)
            } else {
                // Conical nozzle
                self.r_throat + (r_exit - self.r_throat) * frac
            };

            x.push(x_pos);
            r.push(r_pos);
        }

        // Calculate areas and area ratios
        let a_throat = PI * self.r_throat * self.r_throat;
        let area: Vec<f64> = r.iter().map(|&ri| PI * ri * ri).collect();
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
    fn test_geometry_generation() {
        let params = GeometryParams {
            r_throat: 0.03,
            l_chamber: 0.15,
            l_nozzle: 0.20,
            contraction_ratio: 3.0,
            expansion_ratio: 40.0,
            theta_conv: 30.0,
            theta_div: 15.0,
            nozzle_type: "conical".to_string(),
        };

        let profile = params.generate_profile(100);

        assert_eq!(profile.x.len(), 100);
        assert_eq!(profile.r.len(), 100);
        assert!(profile.r.iter().all(|&r| r > 0.0));
    }
}
