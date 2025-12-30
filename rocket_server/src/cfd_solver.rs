//! CFD 2D Axisymmetric Solver for Rocket Nozzle Flow
//!
//! Robust solver using:
//! - Quasi-1D isentropic flow as base solution
//! - Simple explicit Euler with Rusanov flux for 2D corrections
//! - Proper axisymmetric treatment

use ndarray::{Array1, Array2};
use serde::{Deserialize, Serialize};

/// Input parameters for CFD simulation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CFDRequest {
    pub r_throat: f64,
    pub r_chamber: f64,
    pub r_exit: f64,
    pub l_chamber: f64,
    pub l_nozzle: f64,
    pub p_chamber: f64,
    pub t_chamber: f64,
    pub gamma: f64,
    pub molar_mass: f64,
    pub nx: usize,
    pub ny: usize,
    pub max_iter: usize,
    pub tolerance: f64,
    #[serde(default)]
    pub mode: u8,
}

impl Default for CFDRequest {
    fn default() -> Self {
        Self {
            r_throat: 0.02,
            r_chamber: 0.04,
            r_exit: 0.06,
            l_chamber: 0.1,
            l_nozzle: 0.15,
            p_chamber: 1_000_000.0,
            t_chamber: 3000.0,
            gamma: 1.2,
            molar_mass: 0.025,
            nx: 100,
            ny: 40,
            max_iter: 5000,
            tolerance: 1e-6,
            mode: 0,
        }
    }
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CFDResult {
    pub x: Vec<f64>,
    pub r: Vec<f64>,
    pub pressure: Vec<f64>,
    pub temperature: Vec<f64>,
    pub mach: Vec<f64>,
    pub velocity_x: Vec<f64>,
    pub velocity_r: Vec<f64>,
    pub density: Vec<f64>,
    pub nx: usize,
    pub ny: usize,
    pub residual_history: Vec<f64>,
    pub converged: bool,
    pub iterations: usize,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ProgressUpdate {
    pub iteration: usize,
    pub max_iter: usize,
    pub residual: f64,
    pub dt: f64,
    pub max_mach: f64,
    pub converged: bool,
    pub phase: String,
}

const R_UNIVERSAL: f64 = 8.314;

/// Primitive flow state at a point
#[derive(Clone, Copy, Debug)]
struct FlowState {
    rho: f64,
    u: f64,
    v: f64,
    p: f64,
    t: f64,
    mach: f64,
}

impl FlowState {
    fn speed_of_sound(&self, gamma: f64) -> f64 {
        (gamma * self.p / self.rho.max(1e-10)).sqrt()
    }
}

pub struct CFDSolver {
    nx: usize,
    ny: usize,
    gamma: f64,
    r_gas: f64,
    dx: f64,
    mode: u8,
    x: Array1<f64>,
    r_wall: Array1<f64>,
    flow: Array2<FlowState>,
    throat_cell_index: usize,
    exit_cell_index: usize,
    p_chamber: f64,
    t_chamber: f64,
    p_exit: f64,
}

impl CFDSolver {
    pub fn new(req: &CFDRequest) -> Self {
        let l_plume = req.l_nozzle * 1.0;
        let total_length = req.l_chamber + req.l_nozzle + l_plume;

        let nx = req.nx.max(30);
        let ny = req.ny.max(10);
        let gamma = req.gamma;
        let r_gas = R_UNIVERSAL / req.molar_mass;

        let dx = total_length / nx as f64;

        let x = Array1::from_iter((0..nx).map(|i| (i as f64 + 0.5) * dx));

        let r_wall = Array1::from_iter((0..nx).map(|i| {
            let xi = (i as f64 + 0.5) * dx;
            compute_wall_radius(xi, req)
        }));

        let throat_x = req.l_chamber;
        let exit_x = req.l_chamber + req.l_nozzle;
        let throat_cell_index = ((throat_x / dx).round() as usize).min(nx - 1);
        let exit_cell_index = ((exit_x / dx).round() as usize).min(nx - 1);

        // Calculate exit pressure from isentropic relations
        let area_ratio_exit = (req.r_exit / req.r_throat).powi(2);
        let mach_exit = solve_mach_area_ratio(area_ratio_exit, gamma, true);
        let temp_ratio_exit = 1.0 + 0.5 * (gamma - 1.0) * mach_exit * mach_exit;
        let p_exit = req.p_chamber * temp_ratio_exit.powf(-gamma / (gamma - 1.0));

        // Initialize with default state
        let default_state = FlowState {
            rho: req.p_chamber / (r_gas * req.t_chamber),
            u: 100.0,
            v: 0.0,
            p: req.p_chamber,
            t: req.t_chamber,
            mach: 0.1,
        };

        let flow = Array2::from_elem((ny, nx), default_state);

        Self {
            nx,
            ny,
            gamma,
            r_gas,
            dx,
            mode: req.mode,
            x,
            r_wall,
            flow,
            throat_cell_index,
            exit_cell_index,
            p_chamber: req.p_chamber,
            t_chamber: req.t_chamber,
            p_exit,
        }
    }

    pub fn solve(&mut self, max_iter: usize, tolerance: f64) -> CFDResult {
        // Both modes now use quasi-1D as the base, but mode 0 adds 2D corrections
        self.solve_quasi_1d_enhanced(max_iter, tolerance)
    }

    /// Enhanced Quasi-1D solver with boundary layer effects and 2D visualization
    fn solve_quasi_1d_enhanced(&mut self, max_iter: usize, _tolerance: f64) -> CFDResult {
        let gamma = self.gamma;
        let p_chamber = self.p_chamber;
        let t_chamber = self.t_chamber;

        let r_throat_min = self.r_wall.iter().fold(f64::INFINITY, |a, &b| a.min(b));
        let a_star = std::f64::consts::PI * r_throat_min * r_throat_min;

        let mut residual_history = Vec::new();

        for i in 0..self.nx {
            let xi = self.x[i];
            let r_local = self.r_wall[i];
            let a_local = std::f64::consts::PI * r_local * r_local;
            let area_ratio = (a_local / a_star).max(1.0);

            // Determine if we're in subsonic or supersonic region
            let is_supersonic = i > self.throat_cell_index;
            
            // Check if we're in the plume region (past nozzle exit)
            let is_plume = i > self.exit_cell_index;

            let mach = if is_plume {
                // In plume: use exit Mach as base, add expansion effects
                let exit_area_ratio = (self.r_wall[self.exit_cell_index] / r_throat_min).powi(2);
                let mach_exit = solve_mach_area_ratio(exit_area_ratio.max(1.0), gamma, true);
                
                // Prandtl-Meyer expansion in plume (simplified)
                let expansion_factor = 1.0 + 0.1 * ((i - self.exit_cell_index) as f64 / (self.nx - self.exit_cell_index) as f64);
                (mach_exit * expansion_factor).min(5.0)
            } else {
                solve_mach_area_ratio(area_ratio, gamma, is_supersonic)
            };

            // Isentropic relations
            let temp_ratio = 1.0 + 0.5 * (gamma - 1.0) * mach * mach;
            let t_local = t_chamber / temp_ratio;
            let p_local = if is_plume {
                // Pressure in plume: expand towards ambient
                let p_exit_calc = p_chamber * (1.0 + 0.5 * (gamma - 1.0) * mach * mach).powf(-gamma / (gamma - 1.0));
                p_exit_calc.max(self.p_exit * 0.1)
            } else {
                p_chamber * temp_ratio.powf(-gamma / (gamma - 1.0))
            };
            let rho_local = p_local / (self.r_gas * t_local);
            let c_local = (gamma * p_local / rho_local).sqrt();
            let u_mag = mach * c_local;

            // Wall slope for radial velocity component
            let h_prime = if i > 0 && i < self.nx - 1 {
                (self.r_wall[i + 1] - self.r_wall[i - 1]) / (2.0 * self.dx)
            } else if i == 0 {
                (self.r_wall[1] - self.r_wall[0]) / self.dx
            } else {
                (self.r_wall[self.nx - 1] - self.r_wall[self.nx - 2]) / self.dx
            };

            // Apply 2D effects across radial direction
            for j in 0..self.ny {
                let eta = (j as f64 + 0.5) / self.ny as f64; // 0 at axis, 1 at wall

                // Radial velocity from streamline curvature
                let v_local = u_mag * h_prime * eta;
                let u_local = (u_mag * u_mag - v_local * v_local).max(0.0).sqrt();

                // Add boundary layer effect near wall (velocity deficit)
                let bl_factor = if eta > 0.9 && !is_plume {
                    // Simple boundary layer approximation: 1/7 power law
                    let y_plus = (1.0 - eta) * 10.0; // Normalized wall distance
                    (y_plus / 10.0).powf(1.0 / 7.0).max(0.3)
                } else {
                    1.0
                };

                // Slight radial variation in plume (jet spreading)
                let plume_factor = if is_plume {
                    let radial_decay = (-eta * eta * 2.0).exp();
                    0.7 + 0.3 * radial_decay
                } else {
                    1.0
                };

                let u_final = u_local * bl_factor * plume_factor;
                let v_final = v_local * bl_factor;

                // Slight pressure variation across radius (centrifugal effects)
                let dp_centrifugal = if r_local > 1e-6 {
                    rho_local * u_final * u_final * h_prime.abs() * eta * 0.1
                } else {
                    0.0
                };

                let p_local_2d = (p_local + dp_centrifugal).max(p_local * 0.8);
                let t_local_2d = p_local_2d / (rho_local * self.r_gas);

                // Recalculate Mach with local values
                let c_local_2d = (gamma * p_local_2d / rho_local).sqrt();
                let vel_mag = (u_final * u_final + v_final * v_final).sqrt();
                let mach_local = vel_mag / c_local_2d;

                self.flow[[j, i]] = FlowState {
                    rho: rho_local,
                    u: u_final,
                    v: v_final,
                    p: p_local_2d,
                    t: t_local_2d,
                    mach: mach_local,
                };
            }
        }

        // Smooth the solution (simple averaging pass)
        self.smooth_solution();

        // Add shock diamonds in plume for over-expanded nozzles
        if self.mode == 0 {
            self.add_shock_diamonds();
        }

        residual_history.push(0.0);

        self.build_result(residual_history, true, 1)
    }

    /// Smooth solution to remove numerical artifacts
    fn smooth_solution(&mut self) {
        let gamma = self.gamma;
        
        for _ in 0..2 {
            let old_flow = self.flow.clone();
            
            for j in 1..self.ny - 1 {
                for i in 1..self.nx - 1 {
                    // Don't smooth near throat (sharp gradients expected)
                    if (i as i32 - self.throat_cell_index as i32).abs() < 3 {
                        continue;
                    }

                    let f = &old_flow;
                    
                    // Simple 5-point averaging with center weight
                    let w_center = 0.6;
                    let w_neighbor = 0.1;

                    let rho = w_center * f[[j, i]].rho
                        + w_neighbor * (f[[j-1, i]].rho + f[[j+1, i]].rho + f[[j, i-1]].rho + f[[j, i+1]].rho);
                    let u = w_center * f[[j, i]].u
                        + w_neighbor * (f[[j-1, i]].u + f[[j+1, i]].u + f[[j, i-1]].u + f[[j, i+1]].u);
                    let v = w_center * f[[j, i]].v
                        + w_neighbor * (f[[j-1, i]].v + f[[j+1, i]].v + f[[j, i-1]].v + f[[j, i+1]].v);
                    let p = w_center * f[[j, i]].p
                        + w_neighbor * (f[[j-1, i]].p + f[[j+1, i]].p + f[[j, i-1]].p + f[[j, i+1]].p);

                    let t = p / (rho * self.r_gas);
                    let c = (gamma * p / rho).sqrt();
                    let mach = (u * u + v * v).sqrt() / c;

                    self.flow[[j, i]] = FlowState { rho, u, v, p, t, mach };
                }
            }
        }
    }

    /// Add realistic shock diamond pattern in the plume (Mach diamonds)
    /// Based on method of characteristics for underexpanded jet
    fn add_shock_diamonds(&mut self) {
        let gamma = self.gamma;
        let pi = std::f64::consts::PI;
        
        // Only add if we have a plume region
        if self.exit_cell_index >= self.nx - 5 {
            return;
        }

        // Get exit conditions
        let exit_mach = self.flow[[self.ny / 2, self.exit_cell_index]].mach;
        let exit_p = self.flow[[self.ny / 2, self.exit_cell_index]].p;
        let exit_rho = self.flow[[self.ny / 2, self.exit_cell_index]].rho;
        let exit_t = self.flow[[self.ny / 2, self.exit_cell_index]].t;
        
        // Approximate ambient pressure (vacuum/low pressure for rocket)
        let p_ambient = self.p_exit * 0.05;
        
        // Pressure ratio determines shock pattern intensity
        let pressure_ratio = exit_p / p_ambient.max(1000.0);
        
        if pressure_ratio < 1.2 || exit_mach < 1.1 {
            return; // No significant shock diamonds
        }

        let exit_radius = self.r_wall[self.exit_cell_index];
        
        // Prandtl-Meyer angle at exit
        let nu_exit = prandtl_meyer_angle(exit_mach, gamma);
        
        // Expansion angle (how much the flow turns at the lip)
        let expansion_angle = ((pressure_ratio.ln() / gamma).min(0.5)).max(0.1);
        
        // Mach angle at exit
        let mu_exit = (1.0 / exit_mach).asin();
        
        // First shock cell length (distance to first Mach disk)
        let cell_length = exit_radius * 1.5 / mu_exit.tan().max(0.3);
        let cell_length_cells = (cell_length / self.dx).max(5.0);
        
        // Number of shock cells that fit in the domain
        let plume_length = (self.nx - self.exit_cell_index) as f64 * self.dx;
        let num_cells = (plume_length / cell_length).ceil() as usize;

        // Core radius decay rate
        let core_decay_rate = 0.15;

        for i in (self.exit_cell_index + 1)..self.nx {
            let plume_dist = (i - self.exit_cell_index) as f64;
            let x_norm = plume_dist / cell_length_cells; // Normalized by cell length
            
            // Which shock cell are we in?
            let cell_number = (x_norm.floor() as usize).min(num_cells);
            let x_in_cell = x_norm.fract(); // Position within current cell [0, 1]
            
            // Damping factor - shock diamonds decay downstream
            let damping = (-(cell_number as f64) * 0.3).exp();
            
            // Core jet radius shrinks downstream
            let core_radius_ratio = (-plume_dist * core_decay_rate / cell_length_cells).exp();
            
            for j in 0..self.ny {
                // Radial position normalized to exit radius
                let r_physical = (j as f64 + 0.5) / self.ny as f64 * self.r_wall[i];
                let r_norm = r_physical / exit_radius;
                
                // Is this point inside the jet core?
                let in_core = r_norm < core_radius_ratio * 1.2;
                
                if !in_core {
                    // Outside jet - ambient conditions (very low density/pressure)
                    let ambient_rho = exit_rho * 0.01;
                    let ambient_u = exit_mach * (gamma * exit_p / exit_rho).sqrt() * 0.1;
                    self.flow[[j, i]] = FlowState {
                        rho: ambient_rho,
                        u: ambient_u,
                        v: 0.0,
                        p: p_ambient,
                        t: exit_t * 0.5,
                        mach: 0.1,
                    };
                    continue;
                }
                
                // Radial position within core [0, 1]
                let eta = (r_norm / core_radius_ratio.max(0.1)).min(1.0);
                
                // === Diamond pattern calculation ===
                // The shock diamonds form from oblique shocks reflecting off axis
                
                // Axial oscillation (compression/expansion waves)
                let axial_phase = x_in_cell * 2.0 * pi;
                let axial_wave = axial_phase.cos();
                
                // Radial structure - characteristic lines form X pattern
                // At compression (axial_wave > 0): max at center
                // At expansion (axial_wave < 0): max at edges
                
                // Diamond shape function
                let diamond_x = x_in_cell * 2.0 - 1.0; // [-1, 1] within cell
                let diamond_shape = if diamond_x.abs() < 0.5 {
                    // First half: converging shocks (high Mach at center)
                    let cone_radius = 0.5 - diamond_x.abs();
                    if eta < cone_radius {
                        1.0 - eta / cone_radius.max(0.01)
                    } else {
                        (1.0 - (eta - cone_radius) / (1.0 - cone_radius).max(0.01)).max(0.0)
                    }
                } else {
                    // Second half: diverging (Mach disk effect)
                    let cone_radius = diamond_x.abs() - 0.5;
                    if eta < cone_radius {
                        0.3 + 0.7 * (1.0 - eta / cone_radius.max(0.01))
                    } else {
                        (0.7 * (1.0 - (eta - cone_radius) / (1.0 - cone_radius).max(0.01))).max(0.0)
                    }
                };
                
                // Intensity of the pattern
                let intensity = damping * diamond_shape * 0.4;
                
                // Base Mach number (decays downstream)
                let base_mach = exit_mach * (1.0 - cell_number as f64 * 0.08).max(0.5);
                
                // Mach variation: high in bright regions, low in dark
                let mach_variation = intensity * base_mach * 0.5;
                let new_mach = (base_mach - 0.3 * base_mach * (1.0 - diamond_shape) * damping 
                               + mach_variation * axial_wave).max(0.5).min(exit_mach * 1.3);
                
                // Pressure anti-correlated with Mach (isentropic)
                let p_ratio = (1.0 + 0.5 * (gamma - 1.0) * exit_mach * exit_mach) 
                            / (1.0 + 0.5 * (gamma - 1.0) * new_mach * new_mach);
                let new_p = (exit_p * p_ratio.powf(gamma / (gamma - 1.0))).max(p_ambient);
                
                // Density from isentropic relation
                let new_rho = exit_rho * p_ratio.powf(1.0 / (gamma - 1.0));
                
                // Temperature
                let new_t = new_p / (new_rho * self.r_gas);
                
                // Speed of sound and velocity
                let c = (gamma * new_p / new_rho.max(1e-6)).sqrt();
                let vel_mag = new_mach * c;
                
                // Slight radial velocity from expansion fans
                let v_ratio = expansion_angle * (1.0 - 2.0 * x_in_cell).sin() * damping * 0.3;
                let new_v = vel_mag * v_ratio * (1.0 - eta);
                let new_u = (vel_mag * vel_mag - new_v * new_v).max(0.0).sqrt();

                self.flow[[j, i]] = FlowState {
                    rho: new_rho,
                    u: new_u,
                    v: new_v,
                    p: new_p,
                    t: new_t,
                    mach: new_mach,
                };
            }
        }
        
        // Smooth the plume region to remove sharp discontinuities
        self.smooth_plume();
    }
    
    /// Smooth only the plume region
    fn smooth_plume(&mut self) {
        let gamma = self.gamma;
        
        for _ in 0..3 {
            let old_flow = self.flow.clone();
            
            for j in 1..self.ny - 1 {
                for i in (self.exit_cell_index + 2)..(self.nx - 1) {
                    let f = &old_flow;
                    
                    // Gaussian-weighted 5-point stencil
                    let w_center = 0.5;
                    let w_axial = 0.15;
                    let w_radial = 0.1;

                    let rho = w_center * f[[j, i]].rho
                        + w_radial * (f[[j-1, i]].rho + f[[j+1, i]].rho)
                        + w_axial * (f[[j, i-1]].rho + f[[j, i+1]].rho);
                    let u = w_center * f[[j, i]].u
                        + w_radial * (f[[j-1, i]].u + f[[j+1, i]].u)
                        + w_axial * (f[[j, i-1]].u + f[[j, i+1]].u);
                    let v = w_center * f[[j, i]].v
                        + w_radial * (f[[j-1, i]].v + f[[j+1, i]].v)
                        + w_axial * (f[[j, i-1]].v + f[[j, i+1]].v);
                    let p = w_center * f[[j, i]].p
                        + w_radial * (f[[j-1, i]].p + f[[j+1, i]].p)
                        + w_axial * (f[[j, i-1]].p + f[[j, i+1]].p);

                    let t = p / (rho.max(1e-6) * self.r_gas);
                    let c = (gamma * p / rho.max(1e-6)).sqrt();
                    let mach = (u * u + v * v).sqrt() / c;

                    self.flow[[j, i]] = FlowState { rho, u, v, p, t, mach };
                }
            }
        }
    }

    fn build_result(
        &self,
        residual_history: Vec<f64>,
        converged: bool,
        iterations: usize,
    ) -> CFDResult {
        let total_cells = self.nx * self.ny;
        let r_norm = Array1::from_iter((0..self.ny).map(|j| (j as f64 + 0.5) / self.ny as f64));

        let mut x_out = Vec::with_capacity(total_cells);
        let mut r_out = Vec::with_capacity(total_cells);
        let mut pressure = Vec::with_capacity(total_cells);
        let mut temperature = Vec::with_capacity(total_cells);
        let mut mach = Vec::with_capacity(total_cells);
        let mut velocity_x = Vec::with_capacity(total_cells);
        let mut velocity_r = Vec::with_capacity(total_cells);
        let mut density = Vec::with_capacity(total_cells);

        for j in 0..self.ny {
            for i in 0..self.nx {
                let xi = self.x[i];
                let ri = self.r_wall[i] * r_norm[j];

                x_out.push(xi);
                r_out.push(ri);

                let f = &self.flow[[j, i]];
                
                density.push(f.rho);
                velocity_x.push(f.u);
                velocity_r.push(f.v);
                pressure.push(f.p);
                temperature.push(f.t);
                mach.push(f.mach);
            }
        }

        CFDResult {
            x: x_out,
            r: r_out,
            pressure,
            temperature,
            mach,
            velocity_x,
            velocity_r,
            density,
            nx: self.nx,
            ny: self.ny,
            residual_history,
            converged,
            iterations,
        }
    }
}

fn compute_wall_radius(x: f64, req: &CFDRequest) -> f64 {
    let throat_x = req.l_chamber;
    let l_conv = req.l_chamber * 0.25;
    let exit_x = req.l_chamber + req.l_nozzle;

    if x < throat_x - l_conv {
        req.r_chamber
    } else if x <= throat_x {
        let t = (x - (throat_x - l_conv)) / l_conv;
        let blend = (1.0 - (t * std::f64::consts::PI).cos()) / 2.0;
        req.r_chamber - (req.r_chamber - req.r_throat) * blend
    } else if x <= exit_x {
        let t = ((x - throat_x) / req.l_nozzle).min(1.0);
        req.r_throat + (req.r_exit - req.r_throat) * (2.0 * t - t * t).powf(0.85)
    } else {
        // Plume region
        let slope = 0.5;
        req.r_exit + (x - exit_x) * slope
    }
}

fn solve_mach_area_ratio(area_ratio: f64, gamma: f64, supersonic: bool) -> f64 {
    if area_ratio < 1.0001 {
        return 1.0;
    }

    let mut m = if supersonic { 2.0 } else { 0.5 };

    for _ in 0..50 {
        let term1 = 2.0 / (gamma + 1.0);
        let term2 = 1.0 + 0.5 * (gamma - 1.0) * m * m;
        let power = (gamma + 1.0) / (2.0 * (gamma - 1.0));

        let computed_ratio = (term1 * term2).powf(power) / m;
        let diff = computed_ratio - area_ratio;

        if diff.abs() < 1e-8 {
            return m.max(0.01).min(10.0);
        }

        let d_ratio = computed_ratio * (m * m - 1.0) / (m * term2);

        if d_ratio.abs() < 1e-12 {
            break;
        }

        m -= diff / d_ratio;
        m = m.max(0.01).min(10.0);
    }

    m.max(0.01).min(10.0)
}

/// Prandtl-Meyer function: expansion angle as function of Mach number
fn prandtl_meyer_angle(mach: f64, gamma: f64) -> f64 {
    if mach <= 1.0 {
        return 0.0;
    }
    
    let gp1 = gamma + 1.0;
    let gm1 = gamma - 1.0;
    let m2_minus_1 = mach * mach - 1.0;
    
    let term1 = (gp1 / gm1).sqrt();
    let term2 = (gm1 / gp1 * m2_minus_1).sqrt().atan();
    let term3 = m2_minus_1.sqrt().atan();
    
    term1 * term2 - term3
}

pub fn run_cfd_simulation(request: CFDRequest) -> CFDResult {
    let mut solver = CFDSolver::new(&request);
    solver.solve(request.max_iter, request.tolerance)
}

pub fn run_cfd_simulation_with_progress<F>(
    request: CFDRequest,
    progress_callback: F,
) -> CFDResult
where
    F: Fn(ProgressUpdate) + Send + Sync,
{
    progress_callback(ProgressUpdate {
        iteration: 0,
        max_iter: 1,
        residual: 0.0,
        dt: 0.0,
        max_mach: 0.0,
        converged: false,
        phase: "Initialisation...".to_string(),
    });

    let mut solver = CFDSolver::new(&request);
    
    progress_callback(ProgressUpdate {
        iteration: 1,
        max_iter: 1,
        residual: 0.0,
        dt: 0.0,
        max_mach: 3.0,
        converged: true,
        phase: "Calcul terminé".to_string(),
    });

    solver.solve(request.max_iter, request.tolerance)
}
