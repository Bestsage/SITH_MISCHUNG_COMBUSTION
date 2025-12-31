"use client";

import React, { createContext, useContext, useState, useCallback, ReactNode } from "react";

// === TYPES ===
export interface MotorConfig {
    name: string;
    oxidizer: string;
    fuel: string;
    of_ratio: number;
    pc: number;
    mdot: number;
    lstar: number;
    contraction_ratio: number;
    pe: number;
    pamb: number;
    theta_n: number;
    theta_e: number;
    material_name: string;
    wall_thickness: number;
    wall_k: number;
    twall_max: number;
    coolant_name: string;
    coolant_mdot: string;
    coolant_pressure: number;
    coolant_tin: number;
    coolant_tout_max: number;
    coolant_margin: number;
    custom_cp: number;
    custom_tboil: number;
    custom_tcrit: number;
    custom_hvap: number;
    jacket_fos: number;
    // Visualization Options
    view_inner?: boolean;
    view_channels?: boolean;
    view_outer?: boolean;
}

export interface GeometryProfile {
    x: number[];
    r: number[];
    area?: number[];
    area_ratio?: number[];
}

interface ThermalProfile {
    x: number[];
    t_wall: number[];
    t_coolant: number[];
    p_coolant: number[];
    q_flux: number[];
}

export interface CalculationResults {
    // CEA results
    isp_vac: number;
    isp_sl: number;
    c_star: number;
    cf_vac: number;
    cf_sl: number;
    t_chamber: number;
    gamma: number;
    mw: number;
    // Geometry
    r_throat: number;
    r_chamber: number;
    r_exit: number;
    l_chamber: number;
    l_nozzle: number;
    area_throat: number;
    area_exit: number;
    expansion_ratio: number;
    // Performance
    thrust_vac: number;
    thrust_sl: number;
    mass_flow: number;
    // Thermal
    max_heat_flux: number;
    max_wall_temp: number;
    coolant_temp_out: number;
    coolant_pressure_drop: number;
    cooling_status: string;
    // Profiles
    thermal_profile?: ThermalProfile;
    geometry_profile?: GeometryProfile;
}

interface SolverResults {
    x: number[];
    t_wall: number[];
    t_coolant: number[];
    p_coolant: number[];
    q_flux: number[];
    t_out: number;
    p_out: number;
    max_t_wall: number;
    max_q_flux: number;
    reynolds: number;
    h_coolant: number;
    delta_p: number;
}

interface CEAResults {
    isp_vac: number;
    isp_sl: number;
    c_star: number;
    t_chamber: number;
    gamma: number;
    mw: number;
}

interface MaterialsDB {
    [key: string]: {
        k: number;
        T_melt: number;
        T_max: number;
        rho: number;
        E: number;
        nu: number;
        alpha: number;
        sigma_y: number;
        sigma_uts: number;
        color: string;
    };
}

// === CONTEXT ===
interface CalculationContextType {
    // State
    config: MotorConfig;
    results: CalculationResults | null;
    solverResults: SolverResults | null;
    ceaResults: CEAResults | null;
    materials: MaterialsDB | null;
    wikiContent: string;
    loading: boolean;
    error: string | null;

    // Actions
    setConfig: (config: Partial<MotorConfig>) => void;
    loadMaterials: () => Promise<void>;
    calculateFull: () => Promise<void>;
    runSolver: () => Promise<void>;
    calculateCEA: (of?: number, pc?: number) => Promise<CEAResults | null>;
    generateGeometry: () => Promise<GeometryProfile | null>;
    loadWiki: () => Promise<void>;
}

const defaultConfig: MotorConfig = {
    name: "Moteur_Propane",
    oxidizer: "O2",
    fuel: "C3H8",
    of_ratio: 2.8,
    pc: 12.0,
    mdot: 0.5,
    lstar: 1.0,
    contraction_ratio: 3.5,
    pe: 1.013,
    pamb: 1.013,
    theta_n: 25.0,
    theta_e: 8.0,
    material_name: "Cuivre-Zirconium (CuZr)",
    wall_thickness: 2.0,
    wall_k: 340.0,
    twall_max: 1000.0,
    coolant_name: "Auto",
    coolant_mdot: "Auto",
    coolant_pressure: 15.0,
    coolant_tin: 293.0,
    coolant_tout_max: 350.0,
    coolant_margin: 20.0,
    custom_cp: 2500.0,
    custom_tboil: 350.0,
    custom_tcrit: 700.0,
    custom_hvap: 400.0,
    jacket_fos: 1.25,
};

// Use relative path - Next.js rewrites will proxy to http://localhost:8000
const API_BASE = "";

const CalculationContext = createContext<CalculationContextType | null>(null);

export function CalculationProvider({ children }: { children: ReactNode }) {
    const [config, setConfigState] = useState<MotorConfig>(defaultConfig);
    const [results, setResults] = useState<CalculationResults | null>(null);
    const [solverResults, setSolverResults] = useState<SolverResults | null>(null);
    const [ceaResults, setCeaResults] = useState<CEAResults | null>(null);
    const [materials, setMaterials] = useState<MaterialsDB | null>(null);
    const [wikiContent, setWikiContent] = useState<string>("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const setConfig = useCallback((partial: Partial<MotorConfig>) => {
        setConfigState(prev => ({ ...prev, ...partial }));
    }, []);

    // === API: /api/materials ===
    const loadMaterials = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/api/materials`);
            const data = await res.json();
            setMaterials(data.materials);
        } catch (e) {
            console.error("Materials load failed:", e);
            setError("Échec du chargement des matériaux");
        }
    }, []);

    // === API: /api/calculate/full ===
    const calculateFull = useCallback(async () => {
        setLoading(true);
        setError(null);
        try {
            const res = await fetch(`${API_BASE}/api/calculate/full`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(config)
            });
            const data = await res.json();
            setResults(data);
        } catch (e) {
            console.error("Calculation failed:", e);
            setError("Échec du calcul");
        } finally {
            setLoading(false);
        }
    }, [config]);

    // === API: /api/solve ===
    const runSolver = useCallback(async () => {
        if (!results) {
            setError("Calculez d'abord le moteur avant le solveur thermique");
            return;
        }

        setLoading(true);
        setError(null);
        try {
            const solverRequest = {
                geometry: {
                    r_throat: results.r_throat,
                    l_chamber: results.l_chamber,
                    l_nozzle: results.l_nozzle,
                    n_channels: 48,
                    channel_width: 0.003,  // 3mm
                    channel_depth: 0.004,  // 4mm
                    wall_thickness: config.wall_thickness / 1000,  // mm to m
                },
                conditions: {
                    p_inlet: config.coolant_pressure * 1e5,  // bar to Pa
                    t_inlet: config.coolant_tin,
                    m_dot: config.mdot * 0.3,  // ~30% for cooling
                    pc: config.pc * 1e5,  // bar to Pa
                    mr: config.of_ratio,
                    k_wall: config.wall_k,
                }
            };

            const res = await fetch(`${API_BASE}/api/solve`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(solverRequest)
            });
            const data = await res.json();

            if (data.status === "success") {
                setSolverResults(data.data);
            } else {
                setError("Solver failed");
            }
        } catch (e) {
            console.error("Solver failed:", e);
            setError("Échec du solveur thermique");
        } finally {
            setLoading(false);
        }
    }, [results, config]);

    // === API: /api/cea/calculate ===
    const calculateCEA = useCallback(async (of?: number, pc?: number): Promise<CEAResults | null> => {
        try {
            const ceaRequest = {
                fuel: config.fuel,
                oxidizer: config.oxidizer,
                of_ratio: of ?? config.of_ratio,
                pc: pc ?? config.pc,
                expansion_ratio: 40.0
            };

            const res = await fetch(`${API_BASE}/api/cea/calculate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(ceaRequest)
            });
            const data: CEAResults = await res.json();
            setCeaResults(data);
            return data;
        } catch (e) {
            console.error("CEA calculation failed:", e);
            return null;
        }
    }, [config]);

    // === API: /api/geometry/generate ===
    const generateGeometry = useCallback(async (): Promise<GeometryProfile | null> => {
        if (!results) return null;

        try {
            const geometryRequest = {
                r_throat: results.r_throat,
                r_chamber: results.r_chamber,
                r_exit: results.r_exit,
                l_chamber: results.l_chamber,
                l_nozzle: results.l_nozzle,
                theta_n: config.theta_n,
                theta_e: config.theta_e
            };

            const res = await fetch(`${API_BASE}/api/geometry/generate`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(geometryRequest)
            });
            const data: GeometryProfile = await res.json();
            return data;
        } catch (e) {
            console.error("Geometry generation failed:", e);
            return null;
        }
    }, [results, config]);

    // === API: /api/wiki ===
    const loadWiki = useCallback(async () => {
        try {
            const res = await fetch(`${API_BASE}/api/wiki`);
            if (res.ok) {
                const content = await res.text();
                setWikiContent(content);
            }
        } catch (e) {
            console.error("Wiki load failed:", e);
        }
    }, []);

    return (
        <CalculationContext.Provider value={{
            config,
            results,
            solverResults,
            ceaResults,
            materials,
            wikiContent,
            loading,
            error,
            setConfig,
            loadMaterials,
            calculateFull,
            runSolver,
            calculateCEA,
            generateGeometry,
            loadWiki,
        }}>
            {children}
        </CalculationContext.Provider>
    );
}

export function useCalculation() {
    const context = useContext(CalculationContext);
    if (!context) {
        throw new Error("useCalculation must be used within CalculationProvider");
    }
    return context;
}
