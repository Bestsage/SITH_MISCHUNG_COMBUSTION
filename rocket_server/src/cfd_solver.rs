//! CFD 2D Axisymmetric Solver for Rocket Nozzle Flow
//!
//! Solves compressible Euler equations on a structured grid using
//! finite volume method with Rusanov flux scheme.

use ndarray::{Array1, Array2};
#[allow(unused_imports)]
use rayon::prelude::*;
use serde::{Deserialize, Serialize};

/// Input parameters for CFD simulation
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CFDRequest {
    /// Throat radius (m)
    pub r_throat: f64,
    /// Chamber radius (m)
    pub r_chamber: f64,
    /// Exit radius (m)
    pub r_exit: f64,
    /// Chamber length (m)
    pub l_chamber: f64,
    /// Nozzle length (m)
    pub l_nozzle: f64,
    /// Chamber pressure (Pa)
    pub p_chamber: f64,
    /// Chamber temperature (K)
    pub t_chamber: f64,
    /// Gas gamma (Cp/Cv)
    pub gamma: f64,
    /// Gas molar mass (kg/mol)
    pub molar_mass: f64,
    /// Grid resolution in x direction
    pub nx: usize,
    /// Grid resolution in r direction
    pub ny: usize,
    /// Max iterations
    pub max_iter: usize,
    /// Convergence tolerance
    pub tolerance: f64,
    /// Solver mode: 0 = Euler 2D (time marching), 1 = Quasi-1D (isentropic)
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

/// CFD simulation results
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct CFDResult {
    /// X coordinates of cell centers
    pub x: Vec<f64>,
    /// R coordinates of cell centers
    pub r: Vec<f64>,
    /// Pressure field (Pa) - flattened [ny][nx]
    pub pressure: Vec<f64>,
    /// Temperature field (K)
    pub temperature: Vec<f64>,
    /// Mach number field
    pub mach: Vec<f64>,
    /// Axial velocity field (m/s)
    pub velocity_x: Vec<f64>,
    /// Radial velocity field (m/s)
    pub velocity_r: Vec<f64>,
    /// Density field (kg/m³)
    pub density: Vec<f64>,
    /// Grid dimensions
    pub nx: usize,
    pub ny: usize,
    /// Convergence history (residual per iteration)
    pub residual_history: Vec<f64>,
    /// Did the simulation converge?
    pub converged: bool,
    /// Number of iterations run
    pub iterations: usize,
}

/// Gas constant R = 8.314 J/(mol·K)
const R_UNIVERSAL: f64 = 8.314;

/// Conservative variables for Euler equations
/// U = [rho, rho*u, rho*v, E]
#[derive(Clone, Copy)]
struct ConservativeVars {
    rho: f64,   // density
    rho_u: f64, // x-momentum
    rho_v: f64, // r-momentum (radial)
    e: f64,     // total energy per volume
}

impl ConservativeVars {
    fn new(rho: f64, u: f64, v: f64, p: f64, gamma: f64) -> Self {
        let e = p / (gamma - 1.0) + 0.5 * rho * (u * u + v * v);
        Self {
            rho,
            rho_u: rho * u,
            rho_v: rho * v,
            e,
        }
    }

    fn to_primitive(&self, gamma: f64) -> (f64, f64, f64, f64) {
        let rho = self.rho.max(1e-10);
        let u = self.rho_u / rho;
        let v = self.rho_v / rho;
        let p = (gamma - 1.0) * (self.e - 0.5 * rho * (u * u + v * v));
        let p = p.max(1e-10);
        (rho, u, v, p)
    }

    fn speed_of_sound(&self, gamma: f64) -> f64 {
        let (rho, _, _, p) = self.to_primitive(gamma);
        (gamma * p / rho).sqrt()
    }

    /// Compute Flux vector F(U) in x-direction
    fn flux_x(&self, gamma: f64) -> (f64, f64, f64, f64) {
        let (rho, u, v, p) = self.to_primitive(gamma);
        (rho * u, rho * u * u + p, rho * u * v, (self.e + p) * u)
    }
}

/// CFD Solver struct
pub struct CFDSolver {
    nx: usize,
    ny: usize,
    gamma: f64,
    r_gas: f64,
    dx: f64,
    _dy: f64,
    mode: u8,
    x: Array1<f64>,
    r: Array1<f64>,
    r_wall: Array1<f64>,
    u: Array2<ConservativeVars>,
    exit_cell_index: usize,
}

impl CFDSolver {
    /// Create a new CFD solver from request parameters
    pub fn new(req: &CFDRequest) -> Self {
        // Plume simulation: extend domain by 1.5x nozzle length
        let l_plume = req.l_nozzle * 1.5;
        let total_length = req.l_chamber + req.l_nozzle + l_plume;

        // Adjust dx to maintain resolution? Or keep fixed nx?
        // User sets nx. If we increase L, dx increases.
        // We should probably keep dx similar to nozzle resolution if possible?
        // But req.nx is fixed. Let's just use req.nx for the WHOLE domain for now
        // (might need higher nx from frontend default!).
        let nx = req.nx;
        let ny = req.ny;
        let gamma = req.gamma;
        let r_gas = R_UNIVERSAL / req.molar_mass;

        let dx = total_length / nx as f64;
        let dy = req.r_chamber / ny as f64;

        // X coordinates (cell centers)
        let x = Array1::from_iter((0..nx).map(|i| (i as f64 + 0.5) * dx));

        // Wall radius profile
        let r_wall = Array1::from_iter((0..nx).map(|i| {
            let xi = (i as f64 + 0.5) * dx;
            compute_wall_radius(xi, req)
        }));

        // R coordinates (cell centers) - normalized 0 to 1
        let r = Array1::from_iter((0..ny).map(|j| (j as f64 + 0.5) / ny as f64));

        // Initialize with 1D quasi-steady flow guess
        let rho_chamber = req.p_chamber / (r_gas * req.t_chamber);
        let a_star = std::f64::consts::PI * req.r_throat * req.r_throat;

        // Speed of sound at chamber
        let c_chamber = (gamma * req.p_chamber / rho_chamber).sqrt();

        // Mass flow from choked throat
        let gamma_factor = ((gamma + 1.0) / 2.0).powf(-(gamma + 1.0) / (2.0 * (gamma - 1.0)));
        let _mdot = rho_chamber * a_star * c_chamber * gamma_factor;

        let mut u = Array2::from_elem(
            (ny, nx),
            ConservativeVars::new(rho_chamber, 10.0, 0.0, req.p_chamber, gamma),
        );

        // Initialize each column with 1D isentropic estimate
        for i in 0..nx {
            let r_local = r_wall[i];
            let a_local = std::f64::consts::PI * r_local * r_local;
            let _area_ratio = a_local / a_star;

            // Approximate Mach number from area ratio (subsonic or supersonic)
            let throat_x = req.l_chamber;
            let xi = (i as f64 + 0.5) * dx;

            let mach = if xi < throat_x {
                // Subsonic: M ~ 0.1 to 1.0 in convergent
                let progress = xi / throat_x;
                0.1 + 0.9 * progress.powf(2.0)
            } else {
                // Supersonic: M ~ 1.0 to 3.0+ in divergent
                let progress = (xi - throat_x) / req.l_nozzle;
                1.0 + 2.5 * progress.powf(0.8)
            };

            // Isentropic relations
            let temp_ratio = 1.0 + 0.5 * (gamma - 1.0) * mach * mach;
            let t_local = req.t_chamber / temp_ratio;
            let p_local = req.p_chamber * temp_ratio.powf(-gamma / (gamma - 1.0));
            let rho_local = p_local / (r_gas * t_local);
            let c_local = (gamma * p_local / rho_local).sqrt();
            let u_local = mach * c_local;

            // Set all radial cells in this column
            for j in 0..ny {
                u[[j, i]] = ConservativeVars::new(rho_local, u_local, 0.0, p_local, gamma);
            }
        }

        let exit_x_pos = req.l_chamber + req.l_nozzle;
        let exit_cell_index = (exit_x_pos / dx).round() as usize;

        Self {
            nx,
            ny,
            gamma,
            r_gas,
            dx,
            _dy: dy,
            mode: req.mode,
            x,
            r,
            r_wall,
            u,
            exit_cell_index,
        }
    }

    /// Run the simulation based on selected mode
    pub fn solve(
        &mut self,
        max_iter: usize,
        tolerance: f64,
        p_chamber: f64,
        t_chamber: f64,
    ) -> CFDResult {
        match self.mode {
            1 => self.solve_quasi_1d(p_chamber, t_chamber),
            _ => self.solve_2d_euler(max_iter, tolerance, p_chamber, t_chamber),
        }
    }

    /// Quasi-1D Isentropic Solver (Instant)
    fn solve_quasi_1d(&mut self, p_chamber: f64, t_chamber: f64) -> CFDResult {
        let gamma = self.gamma;
        // Throat area (assuming minimum radius in r_wall is throat)
        let r_throat_min = self.r_wall.iter().fold(f64::INFINITY, |a, &b| a.min(b));
        let a_star = std::f64::consts::PI * r_throat_min * r_throat_min;

        let throat_idx = self
            .r_wall
            .iter()
            .position(|&r| r == r_throat_min)
            .unwrap_or(0);

        for i in 0..self.nx {
            let r_local = self.r_wall[i];
            let a_local = std::f64::consts::PI * r_local * r_local;
            let area_ratio = a_local / a_star;

            // Solve M for Area Ratio
            // Subsonic before throat, supersonic after
            let is_supersonic = i > throat_idx;
            let mach = solve_mach_area_ratio(area_ratio, gamma, is_supersonic);

            // Isentropic relations
            let temp_ratio = 1.0 + 0.5 * (gamma - 1.0) * mach * mach;
            let t_local = t_chamber / temp_ratio;
            let p_local = p_chamber * temp_ratio.powf(-gamma / (gamma - 1.0));
            let rho_local = p_local / (self.r_gas * t_local);
            let c_local = (gamma * p_local / rho_local).sqrt();
            let u_mag = mach * c_local;

            // Flow direction
            // Assume flow follows wall angle linearly: angle = (r/R_wall) * atan(dR_wall/dx)
            // But simple 1D assumes mostly axial. Let's add a small radial component for viz.
            let h_prime = if i > 0 && i < self.nx - 1 {
                (self.r_wall[i + 1] - self.r_wall[i - 1]) / (2.0 * self.dx)
            } else {
                0.0
            };

            for j in 0..self.ny {
                let r_frac = (j as f64 + 0.5) / self.ny as f64; // 0 at axis, 1 at wall (approx)

                // Simple radial velocity distribution
                let v_local = u_mag * h_prime * r_frac;
                let u_local = (u_mag * u_mag - v_local * v_local).max(0.0).sqrt();

                self.u[[j, i]] = ConservativeVars::new(rho_local, u_local, v_local, p_local, gamma);
            }
        }

        // Return immediately with "converged" result
        self.build_result(vec![0.0], true, 1)
    }

    /// Run the 2D Euler time-marching simulation
    pub fn solve_2d_euler(
        &mut self,
        max_iter: usize,
        tolerance: f64,
        p_chamber: f64,
        t_chamber: f64,
    ) -> CFDResult {
        let mut residual_history = Vec::with_capacity(max_iter);
        let mut converged = false;
        let mut iterations = 0;

        let cfl = 0.5;

        for iter in 0..max_iter {
            // Compute fluxes and update
            let (residual, dt) = self.step(cfl, p_chamber, t_chamber);
            residual_history.push(residual);
            iterations = iter + 1;

            if residual < tolerance {
                converged = true;
                break;
            }

            // Print progress every 500 iterations (for debugging)
            if iter % 500 == 0 {
                eprintln!(
                    "CFD Iter {}: residual = {:.2e}, dt = {:.2e}",
                    iter, residual, dt
                );
            }
        }

        self.build_result(residual_history, converged, iterations)
    }

    /// Single time step with Rusanov flux and metric terms
    fn step(&mut self, cfl: f64, p_chamber: f64, t_chamber: f64) -> (f64, f64) {
        let gamma = self.gamma;

        // Compute max wave speed for CFL
        let mut max_speed = 1e-10_f64;
        for j in 0..self.ny {
            for i in 0..self.nx {
                let (_, u, v, _) = self.u[[j, i]].to_primitive(gamma);
                let c = self.u[[j, i]].speed_of_sound(gamma);
                let speed = (u.abs() + c).max(v.abs() + c);
                max_speed = max_speed.max(speed);
            }
        }

        // CFL condition adapted for mapped grid
        // Physical size roughly dx and dy_local
        // dy_local approx r_wall / ny
        let min_dy_physical =
            self.r_wall.iter().fold(f64::INFINITY, |a, &b| a.min(b)) / self.ny as f64;
        let dt = cfl * self.dx.min(min_dy_physical) / max_speed;

        // Store old values
        let u_old = self.u.clone();

        // Compute residual
        let mut max_residual = 0.0_f64;

        // Update interior cells
        // Using non-conservative chain rule form for metric terms:
        // d/dx = d/dxi - (eta * h' / h) d/deta
        // d/dr = (1/h) d/deta
        // where h(x) = r_wall(x) and eta = r/h in [0,1]

        // d_eta = 1/ny
        let d_eta = 1.0 / self.ny as f64;

        for j in 1..self.ny - 1 {
            let eta = (j as f64 + 0.5) * d_eta;

            for i in 1..self.nx - 1 {
                let _xi = self.x[i];

                // Use central difference for h' from precomputed r_wall
                let h_val = self.r_wall[i];
                let h_prime = (self.r_wall[i + 1] - self.r_wall[i - 1]) / (2.0 * self.dx);

                let r_local = h_val * eta;

                // X-direction fluxes (dF/dxi)
                let flux_x_right = rusanov_flux_x(&u_old[[j, i]], &u_old[[j, i + 1]], gamma);
                let flux_x_left = rusanov_flux_x(&u_old[[j, i - 1]], &u_old[[j, i]], gamma);
                let df_dxi = (
                    (flux_x_right.0 - flux_x_left.0) / self.dx,
                    (flux_x_right.1 - flux_x_left.1) / self.dx,
                    (flux_x_right.2 - flux_x_left.2) / self.dx,
                    (flux_x_right.3 - flux_x_left.3) / self.dx,
                );

                // Eta-direction fluxes of F (dF/deta)
                // We use central difference of F
                let f_up = u_old[[j + 1, i]].flux_x(gamma);
                let f_down = u_old[[j - 1, i]].flux_x(gamma);
                let df_deta = (
                    (f_up.0 - f_down.0) / (2.0 * d_eta),
                    (f_up.1 - f_down.1) / (2.0 * d_eta),
                    (f_up.2 - f_down.2) / (2.0 * d_eta),
                    (f_up.3 - f_down.3) / (2.0 * d_eta),
                );

                // Eta-direction fluxes of G (dG/deta)
                let flux_r_up = rusanov_flux_r(&u_old[[j, i]], &u_old[[j + 1, i]], gamma);
                let flux_r_down = rusanov_flux_r(&u_old[[j - 1, i]], &u_old[[j, i]], gamma);
                let dg_deta = (
                    (flux_r_up.0 - flux_r_down.0) / d_eta,
                    (flux_r_up.1 - flux_r_down.1) / d_eta,
                    (flux_r_up.2 - flux_r_down.2) / d_eta,
                    (flux_r_up.3 - flux_r_down.3) / d_eta,
                );

                // Axisymmetric source terms (S = -G/r)
                // At j=0 (first cell), r is small. 1/r is large.
                // L'Hopital's rule for v/r at r->0 is dv/dr.
                // We are at cell center j (r = eta * h).
                // If j is small, we should be careful.

                // Calculate G (flux_r_local)
                let (rho, u, v, p) = u_old[[j, i]].to_primitive(gamma);

                let r_eff = r_local.max(1e-10);

                let (s0, s1, s2, s3) = if j <= 2 {
                    // NEAR AXIS: Use approximation v/r ~ dv/dr

                    // Simple singularity fix:
                    // If r is very small, assume flow is 1D axial, so v=0, source=0.
                    let damping = (r_local / (0.1 * h_val)).min(1.0); // Ramp up from 0 to 1 over 10% of radius

                    (
                        -rho * v / r_eff * damping,
                        0.0,
                        -rho * v * v / r_eff * damping + p / r_eff * damping,
                        -(u_old[[j, i]].e + p) * v / r_eff * damping,
                    )
                } else {
                    (
                        -rho * v / r_eff,
                        -rho * u * v / r_eff,
                        -rho * v * v / r_eff, // Explicitly cancelled form as derived in comments
                        -(u_old[[j, i]].e + p) * v / r_eff,
                    )
                };

                let source_total = (s0, s1, s2, s3);

                // Metric term factor
                let metric_factor = eta * h_prime / h_val;

                // Total Update
                // dU/dt = - (dF/dxi - metric * dF/deta) - (1/h * dG/deta) + S

                let du_0 = -(df_dxi.0 - metric_factor * df_deta.0) - (1.0 / h_val * dg_deta.0)
                    + source_total.0;
                let du_1 = -(df_dxi.1 - metric_factor * df_deta.1) - (1.0 / h_val * dg_deta.1)
                    + source_total.1;
                let du_2 = -(df_dxi.2 - metric_factor * df_deta.2) - (1.0 / h_val * dg_deta.2)
                    + source_total.2;
                let du_3 = -(df_dxi.3 - metric_factor * df_deta.3) - (1.0 / h_val * dg_deta.3)
                    + source_total.3;

                self.u[[j, i]].rho = (u_old[[j, i]].rho + dt * du_0).max(1e-10);
                self.u[[j, i]].rho_u = u_old[[j, i]].rho_u + dt * du_1;
                self.u[[j, i]].rho_v = u_old[[j, i]].rho_v + dt * du_2;
                self.u[[j, i]].e = (u_old[[j, i]].e + dt * du_3).max(1e-10);

                max_residual = max_residual.max(du_0.abs() / self.u[[j, i]].rho);
            }
        }

        // Apply boundary conditions
        self.apply_bc(p_chamber, t_chamber);

        (max_residual, dt)
    }

    /// Apply boundary conditions
    fn apply_bc(&mut self, p_chamber: f64, t_chamber: f64) {
        let gamma = self.gamma;
        let rho_chamber = p_chamber / (self.r_gas * t_chamber);

        // Inlet (left): Subsonic constant total pressure/temp
        // Or just fixed Dirichlet for visualization stability
        for j in 0..self.ny {
            // Simple fix: if M < 1, fix stagnation conditions.
            // For visualization, sticking to hardcoded chamber state at inlet is robust.
            self.u[[j, 0]] = ConservativeVars::new(rho_chamber, 150.0, 0.0, p_chamber, gamma);
            // Inject with some velocity
        }

        // Outlet (right): extrapolation
        for j in 0..self.ny {
            self.u[[j, self.nx - 1]] = self.u[[j, self.nx - 2]];
        }

        // Axis (bottom, j=0): Symmetry
        for i in 0..self.nx {
            self.u[[0, i]] = self.u[[1, i]];
            self.u[[0, i]].rho_v = 0.0; // v = 0
        }

        // Wall (top, j=ny-1)
        // With mapped grid, j=ny-1 is exactly the wall.
        // For x <= exit_x, this is the nozzle wall (Tangency).
        // For x > exit_x, this is the far-field plume boundary (Pressure Outlet / Ambient).

        let p_ambient = p_chamber * 0.05; // Assume 20:1 expansion ratio for simulation
                                          // Ideally this should be a parameter, but for visualization we want to guarantee over/under expansion.

        for i in 1..self.nx - 1 {
            if i <= self.exit_cell_index {
                // NOZZLE WALL: Tangency
                let h_prime = (self.r_wall[i + 1] - self.r_wall[i - 1]) / (2.0 * self.dx);

                // Extrapolate pressure and density from interior
                let u_inner = self.u[[self.ny - 2, i]];
                let (rho, u_x, _, p) = u_inner.to_primitive(gamma);

                // Enforce tangency: v_r = u_x * h'
                let v_r = u_x * h_prime;

                self.u[[self.ny - 1, i]] = ConservativeVars::new(rho, u_x, v_r, p, gamma);
            } else {
                // PLUME JET BOUNDARY (Far Field)
                // Set to ambient conditions to allow waves to reflect off the pressure boundary
                // or simply be an open boundary.
                // To see diamonds, we need the jet to feel the ambient pressure.
                let t_ambient = 300.0;
                let rho_ambient = p_ambient / (self.r_gas * t_ambient);

                // Set ghost cell to static ambient air
                self.u[[self.ny - 1, i]] =
                    ConservativeVars::new(rho_ambient, 0.0, 0.0, p_ambient, gamma);
            }
        }
    }

    /// Build the result structure
    // ... no change needed in build_result structure, but make sure r_out uses r_wall

    /// Build the result structure
    fn build_result(
        &self,
        residual_history: Vec<f64>,
        converged: bool,
        iterations: usize,
    ) -> CFDResult {
        let gamma = self.gamma;
        let total_cells = self.nx * self.ny;

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
                let ri = self.r_wall[i] * self.r[j];

                x_out.push(xi);
                r_out.push(ri);

                let (rho, u, v, p) = self.u[[j, i]].to_primitive(gamma);
                let t = p / (rho * self.r_gas);
                let c = (gamma * p / rho).sqrt();
                let vel = (u * u + v * v).sqrt();
                let m = vel / c;

                density.push(rho);
                velocity_x.push(u);
                velocity_r.push(v);
                pressure.push(p);
                temperature.push(t);
                mach.push(m);
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

/// Compute wall radius at axial position x
fn compute_wall_radius(x: f64, req: &CFDRequest) -> f64 {
    let throat_x = req.l_chamber;
    let l_conv = req.l_chamber * 0.25; // Convergent length
    let exit_x = req.l_chamber + req.l_nozzle;

    if x < throat_x - l_conv {
        // Cylindrical chamber
        req.r_chamber
    } else if x <= throat_x {
        // Convergent section (cosine blend)
        let t = (x - (throat_x - l_conv)) / l_conv;
        let blend = (1.0 - (t * std::f64::consts::PI).cos()) / 2.0;
        req.r_chamber - (req.r_chamber - req.r_throat) * blend
    } else if x <= exit_x {
        // Divergent section (parabolic bell)
        let t = (x - throat_x) / req.l_nozzle;
        let t = t.min(1.0);
        req.r_throat + (req.r_exit - req.r_throat) * (2.0 * t - t * t).powf(0.85)
    } else {
        // Plume Region (Free expansion domain)
        // Expand continuously to avoid grid discontinuity.
        // Assume 45 degree opening angle (slope 1.0)
        let slope = 1.0;
        req.r_exit + (x - exit_x) * slope
    }
}

/// Rusanov flux in x-direction
fn rusanov_flux_x(
    ul: &ConservativeVars,
    ur: &ConservativeVars,
    gamma: f64,
) -> (f64, f64, f64, f64) {
    let (rho_l, u_l, v_l, p_l) = ul.to_primitive(gamma);
    let (rho_r, u_r, v_r, p_r) = ur.to_primitive(gamma);

    let c_l = ul.speed_of_sound(gamma);
    let c_r = ur.speed_of_sound(gamma);

    // Max wave speed
    let s_max = (u_l.abs() + c_l).max(u_r.abs() + c_r);

    // Fluxes
    let f_l = (
        rho_l * u_l,
        rho_l * u_l * u_l + p_l,
        rho_l * u_l * v_l,
        (ul.e + p_l) * u_l,
    );
    let f_r = (
        rho_r * u_r,
        rho_r * u_r * u_r + p_r,
        rho_r * u_r * v_r,
        (ur.e + p_r) * u_r,
    );

    // Rusanov flux
    (
        0.5 * (f_l.0 + f_r.0 - s_max * (ur.rho - ul.rho)),
        0.5 * (f_l.1 + f_r.1 - s_max * (ur.rho_u - ul.rho_u)),
        0.5 * (f_l.2 + f_r.2 - s_max * (ur.rho_v - ul.rho_v)),
        0.5 * (f_l.3 + f_r.3 - s_max * (ur.e - ul.e)),
    )
}

/// Rusanov flux in r-direction
fn rusanov_flux_r(
    ul: &ConservativeVars,
    ur: &ConservativeVars,
    gamma: f64,
) -> (f64, f64, f64, f64) {
    let (rho_l, u_l, v_l, p_l) = ul.to_primitive(gamma);
    let (rho_r, u_r, v_r, p_r) = ur.to_primitive(gamma);

    let c_l = ul.speed_of_sound(gamma);
    let c_r = ur.speed_of_sound(gamma);

    // Max wave speed
    let s_max = (v_l.abs() + c_l).max(v_r.abs() + c_r);

    // Fluxes (in r-direction, v is the convecting velocity)
    let g_l = (
        rho_l * v_l,
        rho_l * u_l * v_l,
        rho_l * v_l * v_l + p_l,
        (ul.e + p_l) * v_l,
    );
    let g_r = (
        rho_r * v_r,
        rho_r * u_r * v_r,
        rho_r * v_r * v_r + p_r,
        (ur.e + p_r) * v_r,
    );

    // Rusanov flux
    (
        0.5 * (g_l.0 + g_r.0 - s_max * (ur.rho - ul.rho)),
        0.5 * (g_l.1 + g_r.1 - s_max * (ur.rho_u - ul.rho_u)),
        0.5 * (g_l.2 + g_r.2 - s_max * (ur.rho_v - ul.rho_v)),
        0.5 * (g_l.3 + g_r.3 - s_max * (ur.e - ul.e)),
    )
}

/// Public function to run CFD simulation
pub fn run_cfd_simulation(request: CFDRequest) -> CFDResult {
    let mut solver = CFDSolver::new(&request);
    solver.solve(
        request.max_iter,
        request.tolerance,
        request.p_chamber,
        request.t_chamber,
    )
}

/// Solve Mach number for a given Area Ratio A/A*
fn solve_mach_area_ratio(area_ratio: f64, gamma: f64, supersonic: bool) -> f64 {
    if area_ratio < 1.0001 {
        return 1.0;
    }

    let mut m = if supersonic { 3.0 } else { 0.1 };

    // Newton-Raphson
    for _ in 0..20 {
        let term1 = 2.0 / (gamma + 1.0);
        let term2 = 1.0 + 0.5 * (gamma - 1.0) * m * m;
        let power = (gamma + 1.0) / (gamma - 1.0);

        let contour = (term1 * term2).powf(power * 0.5) / m;
        let diff = contour - area_ratio;

        if diff.abs() < 1e-6 {
            return m;
        }

        // Derivative d(A/A*)/dM
        // A/A* = (1/M) * [...]^((g+1)/(2(g-1)))
        let _d_contour = contour * ((m * m - 1.0) / (term2 * m * 2.0 / (gamma - 1.0)));
        // Approximate derivative is safer often
        /*
        let d_contour = (area_ratio_func(m + 1e-4, gamma) - area_ratio_func(m - 1e-4, gamma)) / 2e-4;
        */

        // Use secant or simple derivative logic?
        // Let's use simple iterative if derivative is annoying?
        // No, derivative is cleaner.
        // d(A/A*)/dM = (A/A*) * (M^2 - 1) / (M * (1 + (g-1)/2 M^2))
        let derivative = contour * (m * m - 1.0) / (m * term2);

        m = m - diff / derivative;

        if m < 0.0 {
            m = 0.001;
        }
    }

    m
}
