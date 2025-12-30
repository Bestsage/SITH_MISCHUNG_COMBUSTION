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
}

/// CFD Solver struct
pub struct CFDSolver {
    nx: usize,
    ny: usize,
    gamma: f64,
    r_gas: f64,
    dx: f64,
    dy: f64,
    x: Array1<f64>,
    r: Array1<f64>,
    r_wall: Array1<f64>,
    u: Array2<ConservativeVars>,
}

impl CFDSolver {
    /// Create a new CFD solver from request parameters
    pub fn new(req: &CFDRequest) -> Self {
        let total_length = req.l_chamber + req.l_nozzle;
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
        let mdot = rho_chamber * a_star * c_chamber * gamma_factor;

        let mut u = Array2::from_elem(
            (ny, nx),
            ConservativeVars::new(rho_chamber, 10.0, 0.0, req.p_chamber, gamma),
        );

        // Initialize each column with 1D isentropic estimate
        for i in 0..nx {
            let r_local = r_wall[i];
            let a_local = std::f64::consts::PI * r_local * r_local;
            let area_ratio = a_local / a_star;

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

        Self {
            nx,
            ny,
            gamma,
            r_gas,
            dx,
            dy,
            x,
            r,
            r_wall,
            u,
        }
    }

    /// Run the simulation
    pub fn solve(
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

    /// Single time step with Rusanov flux
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

        let dt = cfl * self.dx.min(self.dy) / max_speed;

        // Store old values
        let u_old = self.u.clone();

        // Compute residual
        let mut max_residual = 0.0_f64;

        // Update interior cells
        for j in 1..self.ny - 1 {
            for i in 1..self.nx - 1 {
                let r_local = self.r_wall[i] * self.r[j];

                // X-direction fluxes
                let flux_x_right = rusanov_flux_x(&u_old[[j, i]], &u_old[[j, i + 1]], gamma);
                let flux_x_left = rusanov_flux_x(&u_old[[j, i - 1]], &u_old[[j, i]], gamma);

                // R-direction fluxes
                let flux_r_up = rusanov_flux_r(&u_old[[j, i]], &u_old[[j + 1, i]], gamma);
                let flux_r_down = rusanov_flux_r(&u_old[[j - 1, i]], &u_old[[j, i]], gamma);

                // Axisymmetric source term
                let (rho, _, v, p) = u_old[[j, i]].to_primitive(gamma);
                let source_rho = -rho * v / r_local.max(1e-10);
                let source_rhou = 0.0;
                let source_rhov = -rho * v * v / r_local.max(1e-10);
                let source_e = -(u_old[[j, i]].e + p) * v / r_local.max(1e-10);

                // Update
                let du_rho = -dt / self.dx * (flux_x_right.0 - flux_x_left.0)
                    - dt / self.dy * (flux_r_up.0 - flux_r_down.0)
                    + dt * source_rho;
                let du_rhou = -dt / self.dx * (flux_x_right.1 - flux_x_left.1)
                    - dt / self.dy * (flux_r_up.1 - flux_r_down.1)
                    + dt * source_rhou;
                let du_rhov = -dt / self.dx * (flux_x_right.2 - flux_x_left.2)
                    - dt / self.dy * (flux_r_up.2 - flux_r_down.2)
                    + dt * source_rhov;
                let du_e = -dt / self.dx * (flux_x_right.3 - flux_x_left.3)
                    - dt / self.dy * (flux_r_up.3 - flux_r_down.3)
                    + dt * source_e;

                self.u[[j, i]].rho = (u_old[[j, i]].rho + du_rho).max(1e-10);
                self.u[[j, i]].rho_u = u_old[[j, i]].rho_u + du_rhou;
                self.u[[j, i]].rho_v = u_old[[j, i]].rho_v + du_rhov;
                self.u[[j, i]].e = (u_old[[j, i]].e + du_e).max(1e-10);

                max_residual = max_residual.max(du_rho.abs() / self.u[[j, i]].rho);
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

        // Inlet (left boundary): fixed chamber conditions, subsonic inflow
        for j in 0..self.ny {
            self.u[[j, 0]] = ConservativeVars::new(rho_chamber, 50.0, 0.0, p_chamber, gamma);
        }

        // Outlet (right boundary): supersonic extrapolation
        for j in 0..self.ny {
            self.u[[j, self.nx - 1]] = self.u[[j, self.nx - 2]];
        }

        // Axis (bottom boundary, j=0): symmetry (v=0, zero gradient)
        for i in 0..self.nx {
            self.u[[0, i]] = self.u[[1, i]];
            self.u[[0, i]].rho_v = 0.0;
        }

        // Wall (top boundary): slip wall (v=0 at wall, reflect)
        for i in 0..self.nx {
            self.u[[self.ny - 1, i]] = self.u[[self.ny - 2, i]];
            self.u[[self.ny - 1, i]].rho_v = -self.u[[self.ny - 2, i]].rho_v;
        }
    }

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

    if x < throat_x - l_conv {
        // Cylindrical chamber
        req.r_chamber
    } else if x <= throat_x {
        // Convergent section (cosine blend)
        let t = (x - (throat_x - l_conv)) / l_conv;
        let blend = (1.0 - (t * std::f64::consts::PI).cos()) / 2.0;
        req.r_chamber - (req.r_chamber - req.r_throat) * blend
    } else {
        // Divergent section (parabolic bell)
        let t = (x - throat_x) / req.l_nozzle;
        let t = t.min(1.0);
        req.r_throat + (req.r_exit - req.r_throat) * (2.0 * t - t * t).powf(0.85)
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

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_simulation() {
        let req = CFDRequest {
            nx: 30,
            ny: 15,
            max_iter: 100,
            ..Default::default()
        };
        let result = run_cfd_simulation(req);
        assert_eq!(result.pressure.len(), 30 * 15);
        assert!(result.mach.iter().all(|m| *m >= 0.0));
    }
}
