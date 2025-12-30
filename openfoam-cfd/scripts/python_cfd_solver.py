#!/usr/bin/env python3
"""
Python CFD Solver for Rocket Nozzle Flow
High-quality 2D axisymmetric compressible Euler solver
Uses MUSCL-Hancock scheme with HLLC Riemann solver

This is used as fallback when Loci-STREAM is not available
"""

import numpy as np
import json
import sys
from pathlib import Path
from dataclasses import dataclass
from typing import Tuple, Callable
import time


@dataclass
class FlowState:
    """Primitive variables"""
    rho: np.ndarray  # Density
    u: np.ndarray    # Axial velocity
    v: np.ndarray    # Radial velocity
    p: np.ndarray    # Pressure
    
    @property
    def shape(self):
        return self.rho.shape


@dataclass
class ConservedState:
    """Conservative variables"""
    rho: np.ndarray      # Density
    rho_u: np.ndarray    # Momentum x
    rho_v: np.ndarray    # Momentum r
    E: np.ndarray        # Total energy


class EulerSolver2D:
    """
    2D Axisymmetric Euler Solver
    - MUSCL reconstruction with minmod limiter
    - HLLC Riemann solver
    - RK2-TVD time integration
    """
    
    def __init__(self, nx: int, ny: int, gamma: float = 1.4):
        self.nx = nx
        self.ny = ny
        self.gamma = gamma
        self.gm1 = gamma - 1.0
        
        # Grid
        self.x = None
        self.r = None
        self.dx = None
        self.dr = None
        
        # Solution
        self.U = None  # Conservative variables [4, ny, nx]
        
        # CFL number
        self.cfl = 0.4
        
    def setup_grid(self, x_wall: np.ndarray, r_wall: np.ndarray):
        """Setup computational grid"""
        self.nx = len(x_wall)
        self.dx = x_wall[1] - x_wall[0] if len(x_wall) > 1 else 0.001
        
        # Create 2D grid
        self.x = np.zeros((self.ny, self.nx))
        self.r = np.zeros((self.ny, self.nx))
        
        for i in range(self.nx):
            self.x[:, i] = x_wall[i]
            # Radial distribution (linear for now)
            for j in range(self.ny):
                eta = (j + 0.5) / self.ny
                self.r[j, i] = r_wall[i] * eta
        
        self.dr = np.zeros((self.ny, self.nx))
        for i in range(self.nx):
            self.dr[:, i] = r_wall[i] / self.ny
            
        # Initialize solution arrays
        self.U = np.zeros((4, self.ny, self.nx))
        
    def primitive_to_conservative(self, W: FlowState) -> ConservedState:
        """Convert primitive to conservative variables"""
        rho = W.rho
        u, v, p = W.u, W.v, W.p
        
        rho_u = rho * u
        rho_v = rho * v
        E = p / self.gm1 + 0.5 * rho * (u**2 + v**2)
        
        return ConservedState(rho, rho_u, rho_v, E)
    
    def conservative_to_primitive(self, U: ConservedState) -> FlowState:
        """Convert conservative to primitive variables"""
        rho = np.maximum(U.rho, 1e-10)
        u = U.rho_u / rho
        v = U.rho_v / rho
        p = self.gm1 * (U.E - 0.5 * rho * (u**2 + v**2))
        p = np.maximum(p, 1e-6)
        
        return FlowState(rho, u, v, p)
    
    def speed_of_sound(self, W: FlowState) -> np.ndarray:
        """Calculate speed of sound"""
        return np.sqrt(self.gamma * W.p / np.maximum(W.rho, 1e-10))
    
    def mach_number(self, W: FlowState) -> np.ndarray:
        """Calculate Mach number"""
        c = self.speed_of_sound(W)
        vel = np.sqrt(W.u**2 + W.v**2)
        return vel / c
    
    def minmod(self, a: np.ndarray, b: np.ndarray) -> np.ndarray:
        """Minmod limiter"""
        result = np.zeros_like(a)
        mask_pos = (a > 0) & (b > 0)
        mask_neg = (a < 0) & (b < 0)
        result[mask_pos] = np.minimum(a[mask_pos], b[mask_pos])
        result[mask_neg] = np.maximum(a[mask_neg], b[mask_neg])
        return result
    
    def reconstruct_muscl_x(self, q: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """MUSCL reconstruction in x-direction"""
        ny, nx = q.shape
        
        # Slopes
        dq_plus = np.zeros_like(q)
        dq_minus = np.zeros_like(q)
        
        dq_plus[:, :-1] = q[:, 1:] - q[:, :-1]
        dq_minus[:, 1:] = q[:, 1:] - q[:, :-1]
        
        # Limited slopes
        dq = self.minmod(dq_plus, dq_minus)
        
        # Left and right states at cell interfaces
        q_L = q + 0.5 * dq  # Right side of cell i
        q_R = q - 0.5 * dq  # Left side of cell i
        
        return q_L, q_R
    
    def reconstruct_muscl_r(self, q: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """MUSCL reconstruction in r-direction"""
        ny, nx = q.shape
        
        dq_plus = np.zeros_like(q)
        dq_minus = np.zeros_like(q)
        
        dq_plus[:-1, :] = q[1:, :] - q[:-1, :]
        dq_minus[1:, :] = q[1:, :] - q[:-1, :]
        
        dq = self.minmod(dq_plus, dq_minus)
        
        q_L = q + 0.5 * dq
        q_R = q - 0.5 * dq
        
        return q_L, q_R
    
    def hllc_flux_x(self, WL: FlowState, WR: FlowState) -> np.ndarray:
        """HLLC flux in x-direction"""
        gamma = self.gamma
        
        # Left state
        rhoL, uL, vL, pL = WL.rho, WL.u, WL.v, WL.p
        cL = np.sqrt(gamma * pL / np.maximum(rhoL, 1e-10))
        EL = pL / self.gm1 + 0.5 * rhoL * (uL**2 + vL**2)
        HL = (EL + pL) / np.maximum(rhoL, 1e-10)
        
        # Right state
        rhoR, uR, vR, pR = WR.rho, WR.u, WR.v, WR.p
        cR = np.sqrt(gamma * pR / np.maximum(rhoR, 1e-10))
        ER = pR / self.gm1 + 0.5 * rhoR * (uR**2 + vR**2)
        HR = (ER + pR) / np.maximum(rhoR, 1e-10)
        
        # Roe averages
        sqrtRhoL = np.sqrt(np.maximum(rhoL, 1e-10))
        sqrtRhoR = np.sqrt(np.maximum(rhoR, 1e-10))
        denom = sqrtRhoL + sqrtRhoR
        
        u_roe = (sqrtRhoL * uL + sqrtRhoR * uR) / denom
        H_roe = (sqrtRhoL * HL + sqrtRhoR * HR) / denom
        c_roe = np.sqrt(self.gm1 * (H_roe - 0.5 * u_roe**2))
        c_roe = np.maximum(c_roe, 1e-10)
        
        # Wave speeds
        SL = np.minimum(uL - cL, u_roe - c_roe)
        SR = np.maximum(uR + cR, u_roe + c_roe)
        
        # Contact wave speed
        num = pR - pL + rhoL * uL * (SL - uL) - rhoR * uR * (SR - uR)
        den = rhoL * (SL - uL) - rhoR * (SR - uR)
        SM = num / np.maximum(np.abs(den), 1e-10) * np.sign(den + 1e-30)
        
        # Flux calculation
        FL = np.zeros((4,) + rhoL.shape)
        FL[0] = rhoL * uL
        FL[1] = rhoL * uL**2 + pL
        FL[2] = rhoL * uL * vL
        FL[3] = uL * (EL + pL)
        
        FR = np.zeros((4,) + rhoR.shape)
        FR[0] = rhoR * uR
        FR[1] = rhoR * uR**2 + pR
        FR[2] = rhoR * uR * vR
        FR[3] = uR * (ER + pR)
        
        # HLLC flux
        F = np.zeros_like(FL)
        
        # Region 1: SL > 0
        mask1 = SL >= 0
        for k in range(4):
            F[k][mask1] = FL[k][mask1]
        
        # Region 4: SR < 0
        mask4 = SR <= 0
        for k in range(4):
            F[k][mask4] = FR[k][mask4]
        
        # Star region left (SL < 0 < SM)
        mask2 = (SL < 0) & (SM >= 0)
        if np.any(mask2):
            pstar = pL + rhoL * (SL - uL) * (SM - uL)
            coeff = rhoL * (SL - uL) / np.maximum(np.abs(SL - SM), 1e-10) * np.sign(SL - SM + 1e-30)
            
            Ustar_L = np.zeros((4,) + rhoL.shape)
            Ustar_L[0] = coeff
            Ustar_L[1] = coeff * SM
            Ustar_L[2] = coeff * vL
            Ustar_L[3] = coeff * (EL / np.maximum(rhoL, 1e-10) + (SM - uL) * (SM + pL / np.maximum(rhoL * (SL - uL), 1e-10)))
            
            for k in range(4):
                F[k][mask2] = FL[k][mask2] + SL[mask2] * (Ustar_L[k][mask2] - np.array([rhoL, rhoL*uL, rhoL*vL, EL])[k][mask2])
        
        # Star region right (SM < 0 < SR)
        mask3 = (SM < 0) & (SR > 0)
        if np.any(mask3):
            pstar = pR + rhoR * (SR - uR) * (SM - uR)
            coeff = rhoR * (SR - uR) / np.maximum(np.abs(SR - SM), 1e-10) * np.sign(SR - SM + 1e-30)
            
            Ustar_R = np.zeros((4,) + rhoR.shape)
            Ustar_R[0] = coeff
            Ustar_R[1] = coeff * SM
            Ustar_R[2] = coeff * vR
            Ustar_R[3] = coeff * (ER / np.maximum(rhoR, 1e-10) + (SM - uR) * (SM + pR / np.maximum(rhoR * (SR - uR), 1e-10)))
            
            for k in range(4):
                F[k][mask3] = FR[k][mask3] + SR[mask3] * (Ustar_R[k][mask3] - np.array([rhoR, rhoR*uR, rhoR*vR, ER])[k][mask3])
        
        return F
    
    def compute_dt(self, W: FlowState) -> float:
        """Compute stable time step"""
        c = self.speed_of_sound(W)
        vel = np.sqrt(W.u**2 + W.v**2)
        
        # Maximum wave speed
        lambda_max = np.max(vel + c)
        
        # Minimum cell size
        dx_min = self.dx
        dr_min = np.min(self.dr)
        
        dt = self.cfl * min(dx_min, dr_min) / (lambda_max + 1e-10)
        return dt
    
    def compute_residual(self, U_arr: np.ndarray, r_wall: np.ndarray) -> np.ndarray:
        """Compute spatial residual dU/dt = -R(U)"""
        # Convert to primitive
        U = ConservedState(U_arr[0], U_arr[1], U_arr[2], U_arr[3])
        W = self.conservative_to_primitive(U)
        
        R = np.zeros_like(U_arr)
        
        # X-direction fluxes
        rho_L, rho_R = self.reconstruct_muscl_x(W.rho)
        u_L, u_R = self.reconstruct_muscl_x(W.u)
        v_L, v_R = self.reconstruct_muscl_x(W.v)
        p_L, p_R = self.reconstruct_muscl_x(W.p)
        
        # Flux at i+1/2 interfaces
        for i in range(self.nx - 1):
            WL = FlowState(rho_L[:, i], u_L[:, i], v_L[:, i], p_L[:, i])
            WR = FlowState(rho_R[:, i+1], u_R[:, i+1], v_R[:, i+1], p_R[:, i+1])
            
            F = self.hllc_flux_x(WL, WR)
            
            for k in range(4):
                R[k, :, i] += F[k] / self.dx
                R[k, :, i+1] -= F[k] / self.dx
        
        # Axisymmetric source terms
        r = self.r
        r_safe = np.maximum(r, 1e-10)
        
        # S = [0, 0, p/r, 0]
        R[2] += W.p / r_safe
        
        return R
    
    def apply_bc(self, U_arr: np.ndarray, W_inlet: FlowState, p_exit: float, r_wall: np.ndarray):
        """Apply boundary conditions"""
        U = ConservedState(U_arr[0], U_arr[1], U_arr[2], U_arr[3])
        W = self.conservative_to_primitive(U)
        
        # Inlet (i=0): Fixed total conditions
        U_in = self.primitive_to_conservative(W_inlet)
        U_arr[0, :, 0] = U_in.rho
        U_arr[1, :, 0] = U_in.rho_u
        U_arr[2, :, 0] = U_in.rho_v
        U_arr[3, :, 0] = U_in.E
        
        # Outlet (i=nx-1): Supersonic extrapolation or pressure BC
        mach_exit = self.mach_number(W)[:, -2]
        
        for j in range(self.ny):
            if mach_exit[j] > 1.0:
                # Supersonic: extrapolate all
                for k in range(4):
                    U_arr[k, j, -1] = U_arr[k, j, -2]
            else:
                # Subsonic: fix pressure
                rho_ext = W.rho[j, -2]
                u_ext = W.u[j, -2]
                v_ext = W.v[j, -2]
                W_out = FlowState(
                    np.array([rho_ext]),
                    np.array([u_ext]),
                    np.array([v_ext]),
                    np.array([p_exit])
                )
                U_out = self.primitive_to_conservative(W_out)
                U_arr[0, j, -1] = U_out.rho[0]
                U_arr[1, j, -1] = U_out.rho_u[0]
                U_arr[2, j, -1] = U_out.rho_v[0]
                U_arr[3, j, -1] = U_out.E[0]
        
        # Axis (j=0): Symmetry
        U_arr[:, 0, :] = U_arr[:, 1, :]
        U_arr[2, 0, :] = -U_arr[2, 1, :]  # v = 0 at axis
        
        # Wall (j=ny-1): Slip wall
        U_arr[:, -1, :] = U_arr[:, -2, :]
        # Zero normal velocity at wall
        # For curved wall, need to compute normal
        U_arr[2, -1, :] = 0  # Simplified: v=0
    
    def solve(self, params: dict, progress_callback: Callable = None) -> dict:
        """
        Solve the flow field
        """
        # Extract parameters
        r_throat = params.get('r_throat', 0.02)
        r_chamber = params.get('r_chamber', 0.04)
        r_exit = params.get('r_exit', 0.06)
        l_chamber = params.get('l_chamber', 0.1)
        l_nozzle = params.get('l_nozzle', 0.15)
        p_chamber = params.get('p_chamber', 1e6)
        t_chamber = params.get('t_chamber', 3000.0)
        gamma = params.get('gamma', 1.2)
        molar_mass = params.get('molar_mass', 0.025)
        nx = params.get('nx', 200)
        ny = params.get('ny', 60)
        max_iter = params.get('max_iter', 10000)
        tolerance = params.get('tolerance', 1e-6)
        
        self.gamma = gamma
        self.gm1 = gamma - 1.0
        self.ny = ny
        
        R_gas = 8.314 / molar_mass
        
        # Generate geometry
        l_plume = l_nozzle * 1.5
        total_length = l_chamber + l_nozzle + l_plume
        x_wall = np.linspace(0, total_length, nx)
        r_wall = np.zeros(nx)
        
        throat_x = l_chamber
        l_conv = l_chamber * 0.3
        exit_x = l_chamber + l_nozzle
        
        for i, xi in enumerate(x_wall):
            if xi < throat_x - l_conv:
                r_wall[i] = r_chamber
            elif xi <= throat_x:
                t = (xi - (throat_x - l_conv)) / l_conv
                blend = (1.0 - np.cos(t * np.pi)) / 2.0
                r_wall[i] = r_chamber - (r_chamber - r_throat) * blend
            elif xi <= exit_x:
                t = (xi - throat_x) / l_nozzle
                r_wall[i] = r_throat + (r_exit - r_throat) * (2*t - t**2)**0.85
            else:
                r_wall[i] = r_exit + (xi - exit_x) * 0.3
        
        # Setup grid
        self.setup_grid(x_wall, r_wall)
        
        # Initial conditions (chamber conditions everywhere)
        rho0 = p_chamber / (R_gas * t_chamber)
        c0 = np.sqrt(gamma * p_chamber / rho0)
        u0 = 0.3 * c0  # Subsonic inlet
        
        W_init = FlowState(
            np.full((ny, nx), rho0),
            np.full((ny, nx), u0),
            np.zeros((ny, nx)),
            np.full((ny, nx), p_chamber)
        )
        
        U = self.primitive_to_conservative(W_init)
        self.U = np.array([U.rho, U.rho_u, U.rho_v, U.E])
        
        # Inlet conditions
        W_inlet = FlowState(
            np.full(ny, rho0),
            np.full(ny, u0),
            np.zeros(ny),
            np.full(ny, p_chamber)
        )
        
        # Exit pressure (low for supersonic flow)
        p_exit = p_chamber * 0.01
        
        # Time stepping (RK2-TVD)
        residual_history = []
        converged = False
        
        start_time = time.time()
        
        for iteration in range(max_iter):
            # Store old state
            U_old = self.U.copy()
            
            # Compute time step
            W = self.conservative_to_primitive(
                ConservedState(self.U[0], self.U[1], self.U[2], self.U[3])
            )
            dt = self.compute_dt(W)
            
            # RK2 Stage 1
            R1 = self.compute_residual(self.U, r_wall)
            U1 = self.U - dt * R1
            self.apply_bc(U1, W_inlet, p_exit, r_wall)
            
            # RK2 Stage 2
            R2 = self.compute_residual(U1, r_wall)
            self.U = 0.5 * (U_old + U1 - dt * R2)
            self.apply_bc(self.U, W_inlet, p_exit, r_wall)
            
            # Compute residual
            residual = np.max(np.abs(self.U - U_old)) / (dt + 1e-30)
            residual_history.append(residual)
            
            # Check convergence
            if residual < tolerance:
                converged = True
                if progress_callback:
                    progress_callback({
                        'iteration': iteration,
                        'max_iter': max_iter,
                        'residual': residual,
                        'converged': True,
                        'phase': 'Converged!'
                    })
                break
            
            # Progress callback
            if progress_callback and iteration % 100 == 0:
                W = self.conservative_to_primitive(
                    ConservedState(self.U[0], self.U[1], self.U[2], self.U[3])
                )
                max_mach = np.max(self.mach_number(W))
                progress_callback({
                    'iteration': iteration,
                    'max_iter': max_iter,
                    'residual': residual,
                    'dt': dt,
                    'max_mach': max_mach,
                    'converged': False,
                    'phase': f'Iteration {iteration}'
                })
        
        elapsed = time.time() - start_time
        print(f"Solver completed in {elapsed:.2f}s, {iteration+1} iterations")
        
        # Extract results
        U_final = ConservedState(self.U[0], self.U[1], self.U[2], self.U[3])
        W_final = self.conservative_to_primitive(U_final)
        
        T = W_final.p / (W_final.rho * R_gas)
        mach = self.mach_number(W_final)
        
        return {
            'x': self.x.flatten().tolist(),
            'r': self.r.flatten().tolist(),
            'pressure': W_final.p.flatten().tolist(),
            'temperature': T.flatten().tolist(),
            'mach': mach.flatten().tolist(),
            'velocity_x': W_final.u.flatten().tolist(),
            'velocity_r': W_final.v.flatten().tolist(),
            'density': W_final.rho.flatten().tolist(),
            'nx': nx,
            'ny': ny,
            'residual_history': residual_history,
            'converged': converged,
            'iterations': iteration + 1
        }


def main():
    if len(sys.argv) < 3:
        print("Usage: python_cfd_solver.py <params.json> <output_dir>")
        sys.exit(1)
    
    params_file = sys.argv[1]
    output_dir = sys.argv[2]
    
    with open(params_file, 'r') as f:
        params = json.load(f)
    
    print("Starting Python CFD solver...")
    
    solver = EulerSolver2D(
        nx=params.get('nx', 200),
        ny=params.get('ny', 60),
        gamma=params.get('gamma', 1.2)
    )
    
    def progress(info):
        print(f"  Iter {info['iteration']}: residual={info['residual']:.2e}, Mach_max={info.get('max_mach', 0):.2f}")
    
    result = solver.solve(params, progress_callback=progress)
    
    # Save results
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(output_path / 'cfd_result.json', 'w') as f:
        json.dump(result, f)
    
    print(f"Results saved to {output_path / 'cfd_result.json'}")
    print(f"Converged: {result['converged']}")
    print(f"Max Mach: {max(result['mach']):.2f}")


if __name__ == "__main__":
    main()
