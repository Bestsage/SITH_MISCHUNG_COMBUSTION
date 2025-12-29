use crate::math;
use pyo3::prelude::*;
use pyo3::types::PyDict;

#[derive(Debug, Clone)]
#[allow(dead_code)]
struct ChannelSegment {
    x: f64,          // Axial position
    radius: f64,     // Chamber/Nozzle radius at x
    area_ratio: f64, // A / A_throat
    tw_hot: f64,     // Wall Temp (Hot Gas Side)
    tw_cold: f64,    // Wall Temp (Coolant Side)
    t_coolant: f64,  // Coolant Bulk Temp
    p_coolant: f64,  // Coolant Pressure
    q_flux: f64,     // Heat Flux
    h_gas: f64,      // Gas Coeff
    h_coolant: f64,  // Coolant Coeff
}

/// Main 1D Solver Function invoked from Python
#[pyfunction]
pub fn solve_1d_channel(
    py: Python,
    cea_callback: PyObject,
    geometry: Bound<'_, PyDict>,
    conditions: Bound<'_, PyDict>,
) -> PyResult<PyObject> {
    // 1. EXTRACT INPUTS
    // =================
    // Geometry
    let r_throat: f64 = geometry.get_item("r_throat")?.unwrap().extract()?; // m
    let area_throat = std::f64::consts::PI * r_throat * r_throat;

    let l_chamber: f64 = geometry.get_item("L_chamber")?.unwrap().extract()?;
    let l_nozzle: f64 = geometry.get_item("L_nozzle")?.unwrap().extract()?;

    let n_channels: f64 = geometry.get_item("n_channels")?.unwrap().extract()?;
    let ch_width: f64 = geometry.get_item("channel_width")?.unwrap().extract()?;
    let ch_depth: f64 = geometry.get_item("channel_depth")?.unwrap().extract()?;
    let wall_thick: f64 = geometry.get_item("wall_thickness")?.unwrap().extract()?;

    // Conditions
    let p_inlet: f64 = conditions.get_item("p_inlet")?.unwrap().extract()?; // Pa
    let t_inlet: f64 = conditions.get_item("t_inlet")?.unwrap().extract()?; // K
    let m_dot_total: f64 = conditions.get_item("m_dot")?.unwrap().extract()?; // kg/s
    let pc: f64 = conditions.get_item("pc")?.unwrap().extract()?; // Pa
    let mr: f64 = conditions.get_item("mr")?.unwrap().extract()?;

    // Material & Fluid
    let k_wall: f64 = conditions.get_item("k_wall")?.unwrap().extract()?; // W/mK

    // 2. DISCRETIZATION
    // =================
    let n_steps = 50;
    let dx = (l_chamber + l_nozzle) / (n_steps as f64);
    let m_dot_channel = m_dot_total / n_channels;

    // Generate contour (Simplified: Cylinder + Conical)
    // In real app, pass arrays. Here we generate valid test data.
    let mut segments: Vec<ChannelSegment> = Vec::with_capacity(n_steps);

    let mut current_tc = t_inlet;
    let mut current_pc = p_inlet;

    // Get CEA props for combustion (once for now, can be local if needed)
    let args = (pc / 100000.0, mr, 1.0); // Pc in Bar
    let cea_res = cea_callback.call1(py, args)?;
    let cea_dict = cea_res.bind(py).downcast::<PyDict>()?;
    let t_comb: f64 = cea_dict.get_item("t_comb")?.unwrap().extract()?;
    let _c_star: f64 = cea_dict.get_item("cstar")?.unwrap().extract()?;
    // Bartz reference factor: h_throat approx
    // h_g ~ (rho*v)^0.8 ...
    // Simplified scaling coefficient for "Powerful" stub:
    let h_g_ref = 1500.0 * (pc / 50e5).powf(0.8); // Rough scaling from 50 bar

    for i in 0..n_steps {
        let x = i as f64 * dx - l_chamber; // 0 at throat? Let's say -L_ch to +L_noz

        // Radius model
        let r_local = if x < 0.0 {
            // Chamber (Converging)
            r_throat * (1.0 + (-x / l_chamber).powi(2) * 2.0) // Fake contour
        } else {
            // Nozzle (Diverging)
            r_throat * (1.0 + (x / l_nozzle) * 3.0)
        };

        let area_local = std::f64::consts::PI * r_local * r_local;
        let area_ratio = area_local / area_throat;

        // 3. SOLVE SEGMENT
        // ================
        // Coolant Props (Simplified constant for now, should call CoolProp later)
        let rho_c = 800.0;
        let mu_c = 0.001;
        let cp_c = 2000.0;
        let k_c = 0.15;

        // Hydraulic Diam
        let d_h = 4.0 * ch_width * ch_depth / (2.0 * (ch_width + ch_depth));
        let vel_c = m_dot_channel / (rho_c * ch_width * ch_depth);
        let re = rho_c * vel_c * d_h / mu_c;
        let pr = mu_c * cp_c / k_c;

        // Friction & Heat Transfer
        let f = math::friction_factor(re, 0.00001, d_h);
        let nu = math::gnielinski(re, pr, f);
        let h_c = nu * k_c / d_h;

        // Gas Side
        let h_g = h_g_ref * math::bartz_scaling(area_ratio);
        let t_recovery = t_comb * 0.95; // Recovery factor

        // Heat Balance: q = hg(Tr-Twg) = k/t(Twg-Twc) = hc(Twc-Tc)
        // Solve linear system for q
        // R_total = 1/hg + t/k + 1/hc
        let r_conv_g = 1.0 / h_g;
        let r_cond = wall_thick / k_wall;
        let r_conv_c = 1.0 / (h_c * (1.0 + 2.0 * ch_depth / ch_width)); // Fin enhancement roughly

        let q_flux = (t_recovery - current_tc) / (r_conv_g + r_cond + r_conv_c);

        // Temperatures
        let t_w_hot = t_recovery - q_flux * r_conv_g;
        let t_w_cold = current_tc + q_flux * r_conv_c;

        // Update Bulk
        let q_total_segment = q_flux * (std::f64::consts::PI * 2.0 * r_local * dx / n_channels);
        let dt_rise = q_total_segment / (m_dot_channel * cp_c);

        let dp_drop = f * (dx / d_h) * 0.5 * rho_c * vel_c * vel_c;

        segments.push(ChannelSegment {
            x,
            radius: r_local,
            area_ratio,
            tw_hot: t_w_hot,
            tw_cold: t_w_cold,
            t_coolant: current_tc,
            p_coolant: current_pc,
            q_flux,
            h_gas: h_g,
            h_coolant: h_c,
        });

        current_tc += dt_rise;
        current_pc -= dp_drop;
    }

    // 4. PACK RESULTS
    // ===============
    // Manual packing for now, convert to PyDict
    let res = PyDict::new_bound(py);
    let x_vec: Vec<f64> = segments.iter().map(|s| s.x).collect();
    let tw_vec: Vec<f64> = segments.iter().map(|s| s.tw_hot).collect();
    let tc_vec: Vec<f64> = segments.iter().map(|s| s.t_coolant).collect();

    res.set_item("x", x_vec)?;
    res.set_item("t_wall", tw_vec)?;
    res.set_item("t_coolant", tc_vec)?;
    res.set_item("p_out", current_pc)?;
    res.set_item("t_out", current_tc)?;

    Ok(res.into())
}

pub fn simple_compatibility_wrapper(
    py: Python,
    cea_callback: PyObject,
    pc: f64,
    mr: f64,
) -> PyResult<PyObject> {
    // Basic connectivity check implementation
    let args = (pc, mr, 40.0);
    let res = cea_callback.call1(py, args)?;
    Ok(res)
}
