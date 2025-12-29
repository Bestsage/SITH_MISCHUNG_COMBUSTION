"use client";

import { useState, useRef, useEffect, useCallback } from "react";
import AppLayout from "@/components/AppLayout";

type ViewMode = "radiale" | "developpee" | "3d";
type Colormap = "inferno" | "viridis" | "plasma" | "magma" | "hot" | "coolwarm";

// Colormap definitions (simplified gradients)
const colormaps: Record<Colormap, string[]> = {
    inferno: ["#000004", "#420a68", "#932667", "#dd513a", "#fca50a", "#fcffa4"],
    viridis: ["#440154", "#414487", "#2a788e", "#22a884", "#7ad151", "#fde725"],
    plasma: ["#0d0887", "#6a00a8", "#b12a90", "#e16462", "#fca636", "#f0f921"],
    magma: ["#000004", "#3b0f70", "#8c2981", "#de4968", "#fe9f6d", "#fcfdbf"],
    hot: ["#000000", "#e60000", "#ffa500", "#ffff00", "#ffffff"],
    coolwarm: ["#3b4cc0", "#688aef", "#a8c5fc", "#f7f7f7", "#f7a789", "#e35e4f", "#b40426"],
};

function interpolateColor(colors: string[], t: number): string {
    const n = colors.length - 1;
    const i = Math.floor(t * n);
    const f = t * n - i;

    if (i >= n) return colors[n];
    if (i < 0) return colors[0];

    const c1 = colors[i];
    const c2 = colors[i + 1];

    const r1 = parseInt(c1.slice(1, 3), 16);
    const g1 = parseInt(c1.slice(3, 5), 16);
    const b1 = parseInt(c1.slice(5, 7), 16);
    const r2 = parseInt(c2.slice(1, 3), 16);
    const g2 = parseInt(c2.slice(3, 5), 16);
    const b2 = parseInt(c2.slice(5, 7), 16);

    const r = Math.round(r1 + (r2 - r1) * f);
    const g = Math.round(g1 + (g2 - g1) * f);
    const b = Math.round(b1 + (b2 - b1) * f);

    return `rgb(${r},${g},${b})`;
}

export default function ThermalPage() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [mode, setMode] = useState<ViewMode>("developpee");
    const [colormap, setColormap] = useState<Colormap>("inferno");
    const [resolution, setResolution] = useState(50);
    const [showIsotherms, setShowIsotherms] = useState(true);
    const [showMaterialLimits, setShowMaterialLimits] = useState(true);
    const [showFluxVectors, setShowFluxVectors] = useState(false);
    const [showCoolantChannels, setShowCoolantChannels] = useState(true);
    const [positionX, setPositionX] = useState(0);

    // Thermal parameters
    const [params, setParams] = useState({
        t_gas: 3223,
        t_hot: 1225,
        t_cold: 1000,
        t_cool: 293,
        flux: 38.24,
        h_g: 19140,
        wall_thickness: 2.0,  // mm
        length: 350,  // mm
    });

    const drawHeatmap = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        const width = canvas.width;
        const height = canvas.height;
        const colors = colormaps[colormap];

        // Clear
        ctx.fillStyle = "#0a0a0f";
        ctx.fillRect(0, 0, width, height);

        const resX = resolution;
        const resY = Math.floor(resolution / 2);
        const cellW = width / resX;
        const cellH = height / resY;

        // Generate thermal gradient
        for (let j = 0; j < resY; j++) {
            for (let i = 0; i < resX; i++) {
                const x = i / resX;  // 0 to 1 along length
                const y = j / resY;  // 0 to 1 through thickness (0=coolant, 1=gas)

                // Temperature varies: hot at throat (x~0.4), coolest at ends
                const throatFactor = 1 - Math.abs(x - 0.4) * 1.5;
                const throatEffect = Math.max(0, throatFactor);

                // Temperature through wall thickness
                const t_wall_hot = params.t_cold + (params.t_hot - params.t_cold) * throatEffect;
                const t_wall_cold = params.t_cool + (t_wall_hot - params.t_cool) * 0.3;

                // Linear interpolation through wall
                const temp = t_wall_cold + (t_wall_hot - t_wall_cold) * y;

                // Normalize to color range  
                const t_min = params.t_cool;
                const t_max = params.t_hot;
                const t_norm = (temp - t_min) / (t_max - t_min);

                ctx.fillStyle = interpolateColor(colors, Math.max(0, Math.min(1, t_norm)));
                ctx.fillRect(i * cellW, (resY - 1 - j) * cellH, cellW + 1, cellH + 1);
            }
        }

        // Draw isotherms as smooth curves following the temperature field
        if (showIsotherms) {
            ctx.lineWidth = 1;

            // Temperature levels for isotherms
            const isoTemps = [400, 500, 600, 700, 800, 900, 1000, 1100, 1200];
            const t_min = params.t_cool;
            const t_max = params.t_hot;

            isoTemps.forEach((targetTemp) => {
                if (targetTemp < t_min || targetTemp > t_max) return;

                // Color based on temperature
                const t_norm = (targetTemp - t_min) / (t_max - t_min);
                ctx.strokeStyle = `rgba(255, 255, 255, ${0.3 + t_norm * 0.4})`;

                ctx.beginPath();
                let started = false;

                // For each x position, find the y where temperature equals targetTemp
                for (let i = 0; i <= resX; i++) {
                    const x_frac = i / resX;
                    const xPos = i * cellW;

                    // Calculate temperature profile at this x position
                    // Throat at x~0.4, using cosine for smooth curve
                    const throatDist = Math.abs(x_frac - 0.43);
                    const throatEffect = Math.exp(-throatDist * throatDist * 15); // Gaussian peak

                    const t_wall_hot = params.t_cold + (params.t_hot - params.t_cold) * (0.4 + 0.6 * throatEffect);
                    const t_wall_cold = params.t_cool + (t_wall_hot - params.t_cool) * 0.25;

                    // Temperature gradient through wall
                    // T(y) = t_wall_cold + (t_wall_hot - t_wall_cold) * y
                    // Find y where T(y) = targetTemp
                    const deltaT = t_wall_hot - t_wall_cold;
                    if (deltaT < 1) continue;

                    const y_norm = (targetTemp - t_wall_cold) / deltaT;

                    if (y_norm >= 0 && y_norm <= 1) {
                        const yPos = height * (1 - y_norm);

                        if (!started) {
                            ctx.moveTo(xPos, yPos);
                            started = true;
                        } else {
                            ctx.lineTo(xPos, yPos);
                        }
                    }
                }
                ctx.stroke();

                // Draw temperature label at the end of the line
                if (started) {
                    ctx.fillStyle = "rgba(255, 255, 255, 0.6)";
                    ctx.font = "10px monospace";
                    ctx.fillText(`${targetTemp}K`, width - 40, height * (1 - (targetTemp - t_min) / (t_max - t_min)));
                }
            });
        }

        // Draw material limits (horizontal lines)
        if (showMaterialLimits) {
            ctx.strokeStyle = "#00d4ff";
            ctx.lineWidth = 2;
            ctx.setLineDash([5, 5]);

            // Gas side
            ctx.beginPath();
            ctx.moveTo(0, 10);
            ctx.lineTo(width, 10);
            ctx.stroke();

            // Coolant side
            ctx.beginPath();
            ctx.moveTo(0, height - 10);
            ctx.lineTo(width, height - 10);
            ctx.stroke();

            ctx.setLineDash([]);
        }

        // Draw coolant channels
        if (showCoolantChannels) {
            ctx.strokeStyle = "#00d4ff";
            ctx.fillStyle = "rgba(0, 212, 255, 0.1)";
            ctx.lineWidth = 1;

            const nChannels = 12;
            const channelWidth = width / nChannels;

            for (let i = 0; i < nChannels; i++) {
                const x = i * channelWidth + channelWidth * 0.2;
                const w = channelWidth * 0.6;
                ctx.fillRect(x, height - 30, w, 20);
                ctx.strokeRect(x, height - 30, w, 20);
            }
        }

        // Draw position indicator
        const posXPixel = (positionX / params.length) * width;
        ctx.strokeStyle = "#ffffff";
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(posXPixel, 0);
        ctx.lineTo(posXPixel, height);
        ctx.stroke();

        // Labels
        ctx.fillStyle = "#ffffff";
        ctx.font = "12px monospace";
        ctx.fillText("Côté gaz", 10, 25);
        ctx.fillText("Côté coolant", 10, height - 35);

    }, [colormap, resolution, showIsotherms, showMaterialLimits, showFluxVectors, showCoolantChannels, positionX, params]);

    useEffect(() => {
        drawHeatmap();
    }, [drawHeatmap]);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (canvas) {
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            drawHeatmap();
        }
    }, [drawHeatmap]);

    return (
        <AppLayout>
            <div className="h-full flex flex-col overflow-hidden">
                {/* Header */}
                <div className="p-4 border-b border-[#27272a] flex-shrink-0">
                    <div className="flex items-center justify-between mb-4">
                        <h1 className="text-xl font-bold text-[#00d4ff]">🔥 Carte Thermique 2D</h1>
                        <div className="flex gap-2">
                            <button className="btn-secondary text-sm">💾</button>
                            <button className="btn-primary text-sm">Ouvrir Visualisation</button>
                        </div>
                    </div>

                    {/* Mode Selection */}
                    <div className="flex flex-wrap items-center gap-6 text-sm">
                        <div className="flex items-center gap-2">
                            <span className="text-[#71717a]">Mode:</span>
                            {(["radiale", "developpee", "3d"] as ViewMode[]).map((m) => (
                                <label key={m} className="flex items-center gap-1 cursor-pointer">
                                    <input
                                        type="radio"
                                        name="mode"
                                        checked={mode === m}
                                        onChange={() => setMode(m)}
                                        className="accent-[#00d4ff]"
                                    />
                                    <span className={mode === m ? "text-[#00d4ff]" : "text-[#a1a1aa]"}>
                                        {m === "radiale" ? "Coupe Radiale" : m === "developpee" ? "Développée" : "3D Surface"}
                                    </span>
                                </label>
                            ))}
                        </div>

                        <div className="flex items-center gap-2">
                            <span className="text-[#71717a]">Colormap:</span>
                            <select
                                value={colormap}
                                onChange={(e) => setColormap(e.target.value as Colormap)}
                                className="input-field py-1 px-2 text-sm"
                            >
                                {Object.keys(colormaps).map((cm) => (
                                    <option key={cm} value={cm}>{cm}</option>
                                ))}
                            </select>
                        </div>

                        <div className="flex items-center gap-2">
                            <span className="text-[#71717a]">Résolution:</span>
                            <input
                                type="number"
                                value={resolution}
                                onChange={(e) => setResolution(parseInt(e.target.value))}
                                className="input-field py-1 px-2 w-16 text-sm"
                                min={10}
                                max={200}
                            />
                        </div>
                    </div>

                    {/* Options */}
                    <div className="flex flex-wrap items-center gap-4 mt-3 text-sm">
                        {[
                            { label: "Isothermes", checked: showIsotherms, set: setShowIsotherms },
                            { label: "Limites matériau", checked: showMaterialLimits, set: setShowMaterialLimits },
                            { label: "Vecteurs flux", checked: showFluxVectors, set: setShowFluxVectors },
                            { label: "Canaux coolant", checked: showCoolantChannels, set: setShowCoolantChannels },
                        ].map((opt) => (
                            <label key={opt.label} className="flex items-center gap-2 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={opt.checked}
                                    onChange={(e) => opt.set(e.target.checked)}
                                    className="w-4 h-4 rounded bg-[#1a1a25] border-[#27272a] accent-[#00d4ff]"
                                />
                                <span className="text-[#a1a1aa]">{opt.label}</span>
                            </label>
                        ))}

                        <div className="flex items-center gap-2 ml-4">
                            <span className="text-[#71717a]">Position X (mm):</span>
                            <input
                                type="range"
                                min={0}
                                max={params.length}
                                value={positionX}
                                onChange={(e) => setPositionX(parseInt(e.target.value))}
                                className="w-32 accent-[#00d4ff]"
                            />
                            <span className="text-[#00d4ff] font-mono">{positionX.toFixed(1)} mm</span>
                        </div>
                    </div>

                    {/* Thermal Values */}
                    <div className="flex flex-wrap gap-4 mt-3 text-xs font-mono">
                        <span className="text-[#ef4444]">T gaz: {params.t_gas} K</span>
                        <span className="text-[#f59e0b]">T hot: {params.t_hot} K</span>
                        <span className="text-[#eab308]">T cold: {params.t_cold} K</span>
                        <span className="text-[#00d4ff]">T cool: {params.t_cool} K</span>
                        <span className="text-white">Flux: {params.flux} MW/m²</span>
                        <span className="text-white">h_g: {params.h_g} W/m²K</span>
                    </div>
                </div>

                {/* Canvas */}
                <div className="flex-1 flex overflow-hidden">
                    <div className="flex-1 relative p-4">
                        <div className="absolute inset-4 bg-[#0a0a0f] rounded-lg border border-[#27272a]">
                            <canvas
                                ref={canvasRef}
                                className="w-full h-full"
                                style={{ display: "block" }}
                            />

                            {/* Title overlay */}
                            <div className="absolute top-2 left-1/2 transform -translate-x-1/2 text-xs text-[#71717a]">
                                Carte Thermique Développée - Température dans la paroi
                            </div>
                        </div>
                    </div>

                    {/* Color Legend */}
                    <div className="w-20 p-4 flex flex-col items-center">
                        <div
                            className="w-6 flex-1 rounded"
                            style={{
                                background: `linear-gradient(to bottom, ${colormaps[colormap].slice().reverse().join(", ")})`
                            }}
                        />
                        <div className="mt-2 text-xs text-[#71717a] space-y-1 text-right w-full">
                            <div>{params.t_hot} K</div>
                            <div className="flex-1"></div>
                            <div>{params.t_cool} K</div>
                        </div>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
