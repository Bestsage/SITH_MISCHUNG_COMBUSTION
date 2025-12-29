use pyo3::prelude::*;
use pyo3::types::PyDict;

pub mod math;
pub mod optimizer;
pub mod solver;

/// Main library interface
#[pymodule]
fn rocket_core(_py: Python, m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(run_cooling_loop, m)?)?;
    m.add_function(wrap_pyfunction!(solver::solve_1d_channel, m)?)?;
    m.add_function(wrap_pyfunction!(optimizer::run_optimization, m)?)?;
    Ok(())
}

/// Legacy/Simple Loop (Keep for compatibility if needed, else deprecate)
#[pyfunction]
fn run_cooling_loop(
    py: Python,
    cea_callback: PyObject,
    pc_psi: f64,
    mr: f64,
    _thrust_n: f64,
    _geometry: Bound<'_, PyDict>,
) -> PyResult<PyObject> {
    // Redirect to new solver logic eventually?
    // For now, keep as simple stub or re-implement using new solver
    solver::simple_compatibility_wrapper(py, cea_callback, pc_psi, mr)
}
