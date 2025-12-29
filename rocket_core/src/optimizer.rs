use crate::solver;
use pyo3::prelude::*;
use pyo3::types::PyDict;
use rand::Rng;

/// Simple bounds struct
pub struct Bounds {
    pub min: Vec<f64>,
    pub max: Vec<f64>,
}

pub struct DifferentialEvolution {
    dim: usize,
    pop_size: usize,
    population: Vec<Vec<f64>>,
    fitness: Vec<f64>,
    bounds: Bounds,

    // Evaluation Context
    py_callback: PyObject,
    template_geo: PyObject,
    template_cond: PyObject,
}

impl DifferentialEvolution {
    pub fn new(
        dim: usize,
        pop_size: usize,
        bounds: Bounds,
        callback: PyObject,
        t_geo: PyObject,
        t_cond: PyObject,
    ) -> Self {
        DifferentialEvolution {
            dim,
            pop_size,
            population: Vec::new(),
            fitness: Vec::new(),
            bounds,
            py_callback: callback,
            template_geo: t_geo,
            template_cond: t_cond,
        }
    }

    pub fn init_population(&mut self) {
        let mut rng = rand::thread_rng();
        self.population.clear();
        for _ in 0..self.pop_size {
            let mut ind = Vec::with_capacity(self.dim);
            for i in 0..self.dim {
                let range = self.bounds.max[i] - self.bounds.min[i];
                ind.push(self.bounds.min[i] + rng.gen::<f64>() * range);
            }
            self.population.push(ind);
            self.fitness.push(1e9); // Infinity
        }
    }

    /// Evaluate a single individual
    /// TODO: This reconstructs PyDicts every time. Optimization possible.
    fn evaluate(&self, py: Python, candidate: &[f64]) -> f64 {
        // Map candidate vector to dictionary keys (hardcoded for now to prove point)
        // Assume [L_chamber, L_nozzle, n_channels]

        let geo_any = self.template_geo.bind(py);
        let cond_any = self.template_cond.bind(py);

        let geo = geo_any.downcast::<PyDict>().expect("Geo must be dict");
        let cond = cond_any.downcast::<PyDict>().expect("Cond must be dict");

        // Clone to modify
        // In real app, we need efficient updates. For MVP, we presume read-only logic
        // OR we'd create a new dict.
        // Here we just pass the clones to the solver.

        // MOCK INPUT MAPPING (This needs to be dynamic based on user config)
        // For MVP: index 0 -> n_channels (example)
        // We'd need to set_item on the dicts here.
        // let _ = geo.set_item("n_channels", candidate[0]);

        // Simulating the call cost:
        let _ = solver::solve_1d_channel(
            py,
            self.py_callback.clone_ref(py),
            geo.clone(),
            cond.clone(),
        );

        // Fake Objective
        let val: f64 = candidate.iter().sum();
        (val - 10.0).abs() // Target sum 10
    }

    pub fn run(&mut self, py: Python, max_generations: usize) -> PyResult<Vec<f64>> {
        let cr = 0.9;
        let f_scale = 0.8;
        let mut rng = rand::thread_rng();

        // 1. Evaluate Initial
        for i in 0..self.pop_size {
            let score = self.evaluate(py, &self.population[i]);
            self.fitness[i] = score;
        }

        for _g in 0..max_generations {
            for i in 0..self.pop_size {
                // Mutation: a + F(b-c)
                let a = rng.gen_range(0..self.pop_size);
                let b = rng.gen_range(0..self.pop_size);
                let c = rng.gen_range(0..self.pop_size);

                let mut trial = self.population[i].clone();
                let r_idx = rng.gen_range(0..self.dim);

                for j in 0..self.dim {
                    if j == r_idx || rng.gen::<f64>() < cr {
                        let diff = self.population[a][j]
                            + f_scale * (self.population[b][j] - self.population[c][j]);
                        // Clamp
                        trial[j] = diff.max(self.bounds.min[j]).min(self.bounds.max[j]);
                    }
                }

                let f_trial = self.evaluate(py, &trial);

                if f_trial < self.fitness[i] {
                    self.fitness[i] = f_trial;
                    self.population[i] = trial;
                }
            }
        }

        // Find best
        let mut best_idx = 0;
        let mut best_score = self.fitness[0];
        for i in 1..self.pop_size {
            if self.fitness[i] < best_score {
                best_score = self.fitness[i];
                best_idx = i;
            }
        }

        Ok(self.population[best_idx].clone())
    }
}

#[pyfunction]
pub fn run_optimization(
    py: Python,
    cea_call: PyObject,
    geo_template: PyObject,
    cond_template: PyObject,
    bounds_min: Vec<f64>,
    bounds_max: Vec<f64>,
    pop_size: usize,
    generations: usize,
) -> PyResult<Vec<f64>> {
    let bounds = Bounds {
        min: bounds_min,
        max: bounds_max,
    };
    let dim = bounds.min.len();

    let mut de =
        DifferentialEvolution::new(dim, pop_size, bounds, cea_call, geo_template, cond_template);

    de.init_population();
    de.run(py, generations)
}
