/// Generic structural properties
pub struct FlowState {
    pub reynolds: f64,
    pub prandtl: f64,
    pub nusselt: f64,
    pub h_coeff: f64,
    pub friction_f: f64,
}

/// Calculate Friction Factor (Colebrook-White approximation)
/// Uses Haaland equation for direct calculation (no iteration needed)
pub fn friction_factor(re: f64, roughness: f64, hydraulic_diam: f64) -> f64 {
    if re < 2300.0 {
        return 64.0 / re;
    }

    // Haaland Equation
    let relative_roughness = roughness / hydraulic_diam;
    let _term = (relative_roughness / 3.7).powi(10) + (6.9 / re); // 6.9/Re is for turbulent part
                                                                  // Actually standard Haaland:
                                                                  // 1/sqrt(f) = -1.8 * log10( (eps/D)/3.7 + 6.9/Re )
    let inner = (relative_roughness / 3.7) + (6.9 / re);
    let inv_sqrt_f = -1.8 * inner.log10();
    1.0 / (inv_sqrt_f * inv_sqrt_f)
}

/// Calculate Nusselt Number (Gnielinski correlation)
/// Valid for 2300 < Re < 5e6, 0.5 < Pr < 2000
pub fn gnielinski(re: f64, pr: f64, f: f64) -> f64 {
    if re < 2300.0 {
        return 3.66; // Constant wall temp approximation for laminar
                     // Or 4.36 for constant heat flux.
                     // 3.66 is safer/conservative lower bound usually.
    }

    let numer = (f / 8.0) * (re - 1000.0) * pr;
    let denom = 1.0 + 12.7 * (f / 8.0).sqrt() * (pr.powf(2.0 / 3.0) - 1.0);
    numer / denom
}

/// Bartz Equation for Gas Side Heat Transfer Coefficient
/// normalized to throat.
/// h_g = 0.026 / D_t^0.2 * (mu^0.2 Cp / Pr^0.6) * (Pc/c_star)^0.8 * (A_t/A)^0.9 * sigma
/// Simplified scaling: h(x) approx h_throat * (A_t/A(x))^0.9
pub fn bartz_scaling(area_ratio: f64) -> f64 {
    // A_t / A
    let inv_ar = 1.0 / area_ratio;
    // Approximating the sonic velocity variation part as well typically results in ~0.9 power of Area ratio
    inv_ar.powf(0.9)
}
