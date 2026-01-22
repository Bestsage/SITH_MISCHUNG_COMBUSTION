"use client";

import { useState, useRef, useMemo, useCallback, useEffect } from "react";
import AppLayout from "@/components/AppLayout";
import { useCalculation } from "@/contexts/CalculationContext";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { trackActivity } from "@/lib/activity";

// ============================================================================
// TYPES
// ============================================================================

interface CFDResult {
    converged: boolean;
    iterations: number;
    mach: number[];
    pressure: number[];
    temperature: number[];
    velocity_x: number[];
    velocity_r?: number[];
    density: number[];
    x: number[];
    r: number[];
    nx: number;
    ny: number;
    residual_history?: number[];
    solver?: string;
}

type FieldType = "mach" | "pressure" | "temperature" | "velocity_x" | "density";

interface TooltipData {
    x: number;
    y: number;
    worldX: number;
    worldR: number;
    mach: number;
    pressure: number;
    temperature: number;
    velocity: number;
}

// ============================================================================
// CONFIGURATION
// ============================================================================

const FIELD_CONFIG: Record<FieldType, { name: string; unit: string; colormap: string; format: (v: number) => string }> = {
    mach: { name: "Mach", unit: "", colormap: "plasma", format: v => v.toFixed(3) },
    pressure: { name: "Pression", unit: "Pa", colormap: "viridis", format: v => (v / 1e5).toFixed(2) + " bar" },
    temperature: { name: "Température", unit: "K", colormap: "inferno", format: v => v.toFixed(0) + " K" },
    velocity_x: { name: "Vitesse", unit: "m/s", colormap: "coolwarm", format: v => v.toFixed(0) + " m/s" },
    density: { name: "Densité", unit: "kg/m³", colormap: "magma", format: v => v.toFixed(3) + " kg/m³" },
};

// ============================================================================
// CUSTOM SHADERS FOR SMOOTH INTERPOLATION
// ============================================================================

const CFD_VERTEX_SHADER = `
    attribute float fieldValue;
    attribute vec2 velocity;
    
    varying float vFieldValue;
    varying vec2 vPosition;
    varying vec2 vVelocity;
    
    void main() {
        vFieldValue = fieldValue;
        vPosition = position.xy;
        vVelocity = velocity;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.0);
    }
`;

const CFD_FRAGMENT_SHADER = `
    uniform float uMinValue;
    uniform float uMaxValue;
    uniform int uColormap;
    uniform float uContourInterval;
    uniform bool uShowContours;
    uniform float uContourWidth;
    
    varying float vFieldValue;
    varying vec2 vPosition;
    varying vec2 vVelocity;
    
    // Plasma colormap (Matplotlib)
    vec3 plasma(float t) {
        const vec3 c0 = vec3(0.050383, 0.029803, 0.527975);
        const vec3 c1 = vec3(0.494877, 0.006098, 0.658390);
        const vec3 c2 = vec3(0.798216, 0.280197, 0.469538);
        const vec3 c3 = vec3(0.973416, 0.585761, 0.252472);
        const vec3 c4 = vec3(0.940015, 0.975158, 0.131326);
        
        if (t < 0.25) return mix(c0, c1, t * 4.0);
        if (t < 0.5) return mix(c1, c2, (t - 0.25) * 4.0);
        if (t < 0.75) return mix(c2, c3, (t - 0.5) * 4.0);
        return mix(c3, c4, (t - 0.75) * 4.0);
    }
    
    // Viridis colormap
    vec3 viridis(float t) {
        const vec3 c0 = vec3(0.267004, 0.004874, 0.329415);
        const vec3 c1 = vec3(0.282327, 0.140926, 0.457517);
        const vec3 c2 = vec3(0.127568, 0.566949, 0.550556);
        const vec3 c3 = vec3(0.369214, 0.788888, 0.382914);
        const vec3 c4 = vec3(0.993248, 0.906157, 0.143936);
        
        if (t < 0.25) return mix(c0, c1, t * 4.0);
        if (t < 0.5) return mix(c1, c2, (t - 0.25) * 4.0);
        if (t < 0.75) return mix(c2, c3, (t - 0.5) * 4.0);
        return mix(c3, c4, (t - 0.75) * 4.0);
    }
    
    // Inferno colormap
    vec3 inferno(float t) {
        const vec3 c0 = vec3(0.001462, 0.000466, 0.013866);
        const vec3 c1 = vec3(0.258234, 0.038571, 0.406152);
        const vec3 c2 = vec3(0.578304, 0.148039, 0.404411);
        const vec3 c3 = vec3(0.865006, 0.316822, 0.226055);
        const vec3 c4 = vec3(0.988362, 0.998364, 0.644924);
        
        if (t < 0.25) return mix(c0, c1, t * 4.0);
        if (t < 0.5) return mix(c1, c2, (t - 0.25) * 4.0);
        if (t < 0.75) return mix(c2, c3, (t - 0.5) * 4.0);
        return mix(c3, c4, (t - 0.75) * 4.0);
    }
    
    // Coolwarm (diverging)
    vec3 coolwarm(float t) {
        const vec3 cool = vec3(0.230, 0.299, 0.754);
        const vec3 white = vec3(0.865, 0.865, 0.865);
        const vec3 warm = vec3(0.706, 0.016, 0.150);
        
        if (t < 0.5) return mix(cool, white, t * 2.0);
        return mix(white, warm, (t - 0.5) * 2.0);
    }
    
    // Magma colormap
    vec3 magma(float t) {
        const vec3 c0 = vec3(0.001462, 0.000466, 0.013866);
        const vec3 c1 = vec3(0.316654, 0.071690, 0.485380);
        const vec3 c2 = vec3(0.716387, 0.214982, 0.474030);
        const vec3 c3 = vec3(0.987053, 0.535049, 0.382719);
        const vec3 c4 = vec3(0.987053, 0.991438, 0.749504);
        
        if (t < 0.25) return mix(c0, c1, t * 4.0);
        if (t < 0.5) return mix(c1, c2, (t - 0.25) * 4.0);
        if (t < 0.75) return mix(c2, c3, (t - 0.5) * 4.0);
        return mix(c3, c4, (t - 0.75) * 4.0);
    }
    
    void main() {
        // Normalize value
        float range = uMaxValue - uMinValue;
        float t = clamp((vFieldValue - uMinValue) / max(range, 0.0001), 0.0, 1.0);
        
        // Apply colormap
        vec3 color;
        if (uColormap == 0) color = plasma(t);
        else if (uColormap == 1) color = viridis(t);
        else if (uColormap == 2) color = inferno(t);
        else if (uColormap == 3) color = coolwarm(t);
        else color = magma(t);
        
        // Improved contour lines - smoother and more stable
        if (uShowContours && uContourInterval > 0.0) {
            // Normalized contour position
            float normalizedVal = (vFieldValue - uMinValue) / max(range, 0.0001);
            float numContours = 12.0; // Fixed number of contours
            float contourVal = normalizedVal * numContours;
            
            // Distance to nearest contour line
            float contourDist = abs(fract(contourVal + 0.5) - 0.5);
            
            // Use screen-space derivatives for consistent line width
            float dx = dFdx(contourVal);
            float dy = dFdy(contourVal);
            float gradientMag = sqrt(dx * dx + dy * dy);
            
            // Prevent artifacts by clamping gradient
            gradientMag = clamp(gradientMag, 0.01, 2.0);
            
            // Anti-aliased contour line
            float lineWidth = uContourWidth * 0.8;
            float lineStrength = 1.0 - smoothstep(0.0, lineWidth * gradientMag, contourDist);
            
            // Softer, more elegant contour visualization
            vec3 contourColor = color * 0.25;
            color = mix(color, contourColor, lineStrength * 0.6);
        }
        
        gl_FragColor = vec4(color, 1.0);
    }
`;

// ============================================================================
// COLOR UTILITIES
// ============================================================================

function getColormapIndex(colormap: string): number {
    switch (colormap) {
        case "plasma": return 0;
        case "viridis": return 1;
        case "inferno": return 2;
        case "coolwarm": return 3;
        case "magma": return 4;
        default: return 0;
    }
}

function getColorForValue(t: number, colormap: string): THREE.Color {
    const color = new THREE.Color();
    t = Math.max(0, Math.min(1, Number.isFinite(t) ? t : 0));

    switch (colormap) {
        case "plasma":
            if (t < 0.25) color.setRGB(0.05 + t * 1.78, 0.03 - t * 0.1, 0.53 + t * 0.52);
            else if (t < 0.5) color.setRGB(0.49 + (t - 0.25) * 1.22, 0.01 + (t - 0.25) * 1.1, 0.66 - (t - 0.25) * 0.76);
            else if (t < 0.75) color.setRGB(0.8 + (t - 0.5) * 0.69, 0.28 + (t - 0.5) * 1.22, 0.47 - (t - 0.5) * 0.87);
            else color.setRGB(0.97 - (t - 0.75) * 0.13, 0.59 + (t - 0.75) * 1.56, 0.25 - (t - 0.75) * 0.47);
            break;
        case "viridis":
            color.setHSL(0.75 - t * 0.5, 0.8, 0.25 + t * 0.35);
            break;
        case "inferno":
            color.setHSL(0.08 * t, 1, 0.15 + t * 0.5);
            break;
        case "coolwarm":
            if (t < 0.5) color.setHSL(0.6, 0.8, 0.4 + (0.5 - t) * 0.4);
            else color.setHSL(0.0, 0.8, 0.4 + (t - 0.5) * 0.4);
            break;
        case "magma":
            color.setHSL(0.85 - t * 0.15, 0.9, 0.1 + t * 0.6);
            break;
        default:
            color.setHSL(0.7 - t * 0.7, 1, 0.5);
    }
    return color;
}

// ============================================================================
// COMPONENTS: CFD HEATMAP WITH SHADER
// ============================================================================

interface CFDHeatmapProps {
    result: CFDResult;
    field: FieldType;
    colormap: string;
    showContours: boolean;
    contourInterval: number;
    showWireframe: boolean;
    onHover?: (data: TooltipData | null) => void;
}

function CFDHeatmapShader({ result, field, colormap, showContours, contourInterval, showWireframe, onHover }: CFDHeatmapProps) {
    const meshRef = useRef<THREE.Mesh>(null);
    const meshMirrorRef = useRef<THREE.Mesh>(null);
    const wireframeRef = useRef<THREE.LineSegments>(null);
    const wireframeMirrorRef = useRef<THREE.LineSegments>(null);
    const { camera, gl } = useThree();
    const raycaster = useRef(new THREE.Raycaster());
    const mouse = useRef(new THREE.Vector2());

    const { geometry, geometryMirror, shaderMaterial, wireframeGeometry, wireframeGeometryMirror, minVal, maxVal } = useMemo(() => {
        const nx = result.nx;
        const ny = result.ny;
        const fieldData = result[field];

        if (!fieldData || fieldData.length === 0 || nx < 2 || ny < 2) {
            return { geometry: null, geometryMirror: null, shaderMaterial: null, wireframeGeometry: null, wireframeGeometryMirror: null, minVal: 0, maxVal: 1 };
        }

        // Calculate Min/Max
        let min = Infinity, max = -Infinity;
        for (const v of fieldData) {
            if (Number.isFinite(v)) {
                if (v < min) min = v;
                if (v > max) max = v;
            }
        }
        if (!Number.isFinite(min)) { min = 0; max = 1; }
        if (max <= min) max = min + 1e-6;

        // Generate geometry - HORIZONTAL with FULL SYMMETRY (top + bottom)
        const numPoints = result.x.length;
        const positions = new Float32Array(numPoints * 3);
        const positionsMirror = new Float32Array(numPoints * 3);
        const fieldValues = new Float32Array(numPoints);
        const velocities = new Float32Array(numPoints * 2);

        const max_x = Math.max(...result.x) || 1;
        const scale = 20 / max_x;
        
        // Find nozzle exit position (where throat is minimum r on wall)
        let nozzleExitX = 0;
        let minWallR = Infinity;
        for (let i = 0; i < nx; i++) {
            const wallIdx = i * ny + (ny - 1);
            if (wallIdx < result.r.length && result.r[wallIdx] < minWallR) {
                minWallR = result.r[wallIdx];
            }
        }
        // Find where wall radius starts expanding beyond throat (that's nozzle region)
        for (let i = 0; i < nx; i++) {
            const wallIdx = i * ny + (ny - 1);
            const axisIdx = i * ny;
            if (wallIdx < result.r.length) {
                // Check if this is past the divergent section (wall expanding rapidly or constant = far-field)
                if (i > 0) {
                    const prevWallIdx = (i - 1) * ny + (ny - 1);
                    const wallR = result.r[wallIdx];
                    const prevWallR = result.r[prevWallIdx];
                    const deltaR = wallR - prevWallR;
                    const deltaX = result.x[wallIdx] - result.x[prevWallIdx];
                    const slope = deltaR / (deltaX + 1e-10);
                    // Far-field has very steep expansion (slope > 1) - mark exit before that
                    if (slope > 0.8 && wallR > minWallR * 1.5) {
                        nozzleExitX = result.x[prevWallIdx];
                        break;
                    }
                }
            }
        }
        if (nozzleExitX === 0) nozzleExitX = max_x * 0.3; // Fallback

        for (let i = 0; i < numPoints; i++) {
            // Horizontal: x stays x, r becomes y
            const posX = result.x[i] * scale - 10;  // Axial -> horizontal (centered)
            const posY = result.r[i] * scale;       // Radial -> vertical
            
            // Upper half (positive Y)
            positions[i * 3] = posX;
            positions[i * 3 + 1] = posY;
            positions[i * 3 + 2] = 0;
            
            // Lower half (negative Y) - mirror
            positionsMirror[i * 3] = posX;
            positionsMirror[i * 3 + 1] = -posY;
            positionsMirror[i * 3 + 2] = 0;

            let val = fieldData[i];
            if (!Number.isFinite(val)) val = min;
            fieldValues[i] = val;

            // Velocity for vector field
            velocities[i * 2] = result.velocity_x?.[i] || 0;
            velocities[i * 2 + 1] = result.velocity_r?.[i] || 0;
        }

        // Generate indices for triangulated mesh
        // SKIP triangles that are in "ambient" zone (very low Mach outside nozzle)
        const indexArray: number[] = [];
        const machData = result.mach;
        const ambientThreshold = 0.02; // Below this = ambient air, don't draw
        
        for (let i = 0; i < nx - 1; i++) {
            for (let j = 0; j < ny - 1; j++) {
                const a = i * ny + j;
                const b = i * ny + j + 1;
                const c = (i + 1) * ny + j;
                const d = (i + 1) * ny + j + 1;
                
                // Check if this quad is in the plume region or nozzle
                const xi = result.x[a];
                const isInsideNozzle = xi <= nozzleExitX;
                
                // For far-field, only draw if at least one vertex has significant Mach
                const maxMachInQuad = Math.max(
                    machData[a] || 0,
                    machData[b] || 0,
                    machData[c] || 0,
                    machData[d] || 0
                );
                
                // Draw if inside nozzle OR if there's significant flow
                if (isInsideNozzle || maxMachInQuad > ambientThreshold) {
                    indexArray.push(a, d, b);
                    indexArray.push(a, c, d);
                }
            }
        }

        // Upper half geometry
        const geom = new THREE.BufferGeometry();
        geom.setAttribute('position', new THREE.BufferAttribute(positions, 3));
        geom.setAttribute('fieldValue', new THREE.BufferAttribute(fieldValues, 1));
        geom.setAttribute('velocity', new THREE.BufferAttribute(velocities, 2));
        geom.setIndex(indexArray);

        // Lower half (mirrored) geometry
        const geomMirror = new THREE.BufferGeometry();
        geomMirror.setAttribute('position', new THREE.BufferAttribute(positionsMirror, 3));
        geomMirror.setAttribute('fieldValue', new THREE.BufferAttribute(fieldValues.slice(), 1));
        geomMirror.setAttribute('velocity', new THREE.BufferAttribute(velocities.slice(), 2));
        geomMirror.setIndex(indexArray.slice());

        // Wireframe geometry - upper
        const wireGeom = new THREE.BufferGeometry();
        wireGeom.setAttribute('position', new THREE.BufferAttribute(positions.slice(), 3));
        const wireIndices: number[] = [];
        for (let i = 0; i < nx - 1; i++) {
            for (let j = 0; j < ny - 1; j++) {
                const a = i * ny + j;
                const b = i * ny + j + 1;
                const c = (i + 1) * ny + j;
                wireIndices.push(a, b, a, c);
            }
        }
        // Edge lines
        for (let j = 0; j < ny - 1; j++) {
            wireIndices.push((nx - 1) * ny + j, (nx - 1) * ny + j + 1);
        }
        for (let i = 0; i < nx - 1; i++) {
            wireIndices.push(i * ny + ny - 1, (i + 1) * ny + ny - 1);
        }
        wireGeom.setIndex(wireIndices);

        // Wireframe geometry - lower (mirrored)
        const wireGeomMirror = new THREE.BufferGeometry();
        wireGeomMirror.setAttribute('position', new THREE.BufferAttribute(positionsMirror.slice(), 3));
        wireGeomMirror.setIndex(wireIndices.slice());

        // Shader material
        const shader = new THREE.ShaderMaterial({
            vertexShader: CFD_VERTEX_SHADER,
            fragmentShader: CFD_FRAGMENT_SHADER,
            uniforms: {
                uMinValue: { value: min },
                uMaxValue: { value: max },
                uColormap: { value: getColormapIndex(colormap) },
                uShowContours: { value: showContours },
                uContourInterval: { value: contourInterval },
                uContourWidth: { value: 0.15 },
            },
            side: THREE.DoubleSide,
        });

        return { geometry: geom, geometryMirror: geomMirror, shaderMaterial: shader, wireframeGeometry: wireGeom, wireframeGeometryMirror: wireGeomMirror, minVal: min, maxVal: max };
    }, [result, field, colormap, showContours, contourInterval]);

    // Update uniforms when props change
    useEffect(() => {
        if (shaderMaterial) {
            shaderMaterial.uniforms.uColormap.value = getColormapIndex(colormap);
            shaderMaterial.uniforms.uShowContours.value = showContours;
            shaderMaterial.uniforms.uContourInterval.value = contourInterval;
        }
    }, [colormap, showContours, contourInterval, shaderMaterial]);

    // Raycaster for tooltip
    useFrame(() => {
        if (!meshRef.current || !onHover) return;

        raycaster.current.setFromCamera(mouse.current, camera);
        const intersects = raycaster.current.intersectObjects([meshRef.current, meshMirrorRef.current!].filter(Boolean));

        if (intersects.length > 0) {
            const hit = intersects[0];
            const faceIdx = hit.faceIndex;
            if (faceIdx === undefined) return;

            // Find closest data point - HORIZONTAL
            const max_x = Math.max(...result.x) || 1;
            const scale = 20 / max_x;
            const worldX = (hit.point.x + 10) / scale;  // Axial position
            const worldR = Math.abs(hit.point.y) / scale;  // Radial (absolute)

            // Find nearest index
            let nearestIdx = 0;
            let minDist = Infinity;
            for (let i = 0; i < result.x.length; i++) {
                const dx = result.x[i] - worldX;
                const dr = result.r[i] - worldR;
                const dist = dx * dx + dr * dr;
                if (dist < minDist) {
                    minDist = dist;
                    nearestIdx = i;
                }
            }

            onHover({
                x: hit.point.x,
                y: hit.point.y,
                worldX: result.x[nearestIdx],
                worldR: result.r[nearestIdx],
                mach: result.mach[nearestIdx],
                pressure: result.pressure[nearestIdx],
                temperature: result.temperature[nearestIdx],
                velocity: result.velocity_x[nearestIdx],
            });
        }
    });

    // Mouse move handler
    useEffect(() => {
        const canvas = gl.domElement;
        const handleMouseMove = (event: MouseEvent) => {
            const rect = canvas.getBoundingClientRect();
            mouse.current.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
            mouse.current.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
        };
        const handleMouseLeave = () => {
            if (onHover) onHover(null);
        };

        canvas.addEventListener('mousemove', handleMouseMove);
        canvas.addEventListener('mouseleave', handleMouseLeave);
        return () => {
            canvas.removeEventListener('mousemove', handleMouseMove);
            canvas.removeEventListener('mouseleave', handleMouseLeave);
        };
    }, [gl, onHover]);

    if (!geometry || !geometryMirror || !shaderMaterial) return null;

    return (
        <group>
            {/* Upper half */}
            <mesh ref={meshRef} geometry={geometry} material={shaderMaterial} />
            {/* Lower half (mirrored) */}
            <mesh ref={meshMirrorRef} geometry={geometryMirror} material={shaderMaterial} />
            {showWireframe && wireframeGeometry && wireframeGeometryMirror && (
                <>
                    <lineSegments ref={wireframeRef} geometry={wireframeGeometry}>
                        <lineBasicMaterial attach="material" color="#ffffff" opacity={0.15} transparent linewidth={1} />
                    </lineSegments>
                    <lineSegments ref={wireframeMirrorRef} geometry={wireframeGeometryMirror}>
                        <lineBasicMaterial attach="material" color="#ffffff" opacity={0.15} transparent linewidth={1} />
                    </lineSegments>
                </>
            )}
        </group>
    );
}

// ============================================================================
// COMPONENT: VECTOR FIELD (ARROWS)
// ============================================================================

function VectorFieldOverlay({ result, scale = 1 }: { result: CFDResult; scale?: number }) {
    const arrowsGeometry = useMemo(() => {
        const nx = result.nx;
        const ny = result.ny;
        if (nx < 2 || ny < 2) return null;

        // Sample every nth point for arrows
        const sampleX = Math.max(1, Math.floor(nx / 20));
        const sampleY = Math.max(1, Math.floor(ny / 10));

        const positions: number[] = [];
        const colors: number[] = [];

        const max_x = Math.max(...result.x) || 1;
        const scalePos = 20 / max_x;

        // Normalize velocities
        let maxVel = 0;
        for (let i = 0; i < result.velocity_x.length; i++) {
            const vx = result.velocity_x[i] || 0;
            const vr = result.velocity_r?.[i] || 0;
            const vel = Math.sqrt(vx * vx + vr * vr);
            if (vel > maxVel) maxVel = vel;
        }
        if (maxVel < 1) maxVel = 1;

        // Helper to add arrow at position
        const addArrow = (posX: number, posY: number, vx: number, vy: number, vel: number) => {
            if (vel < maxVel * 0.01) return; // Skip near-zero velocity

            // Arrow length proportional to velocity magnitude
            const arrowLength = 0.3 * scale * (vel / maxVel);
            const angle = Math.atan2(vy, vx);

            // Arrow shaft
            const endX = posX + Math.cos(angle) * arrowLength;
            const endY = posY + Math.sin(angle) * arrowLength;

            // Shaft line
            positions.push(posX, posY, 0.01, endX, endY, 0.01);

            // Arrow head
            const headSize = arrowLength * 0.3;
            const headAngle1 = angle + Math.PI * 0.8;
            const headAngle2 = angle - Math.PI * 0.8;

            positions.push(
                endX, endY, 0.01,
                endX + Math.cos(headAngle1) * headSize, endY + Math.sin(headAngle1) * headSize, 0.01
            );
            positions.push(
                endX, endY, 0.01,
                endX + Math.cos(headAngle2) * headSize, endY + Math.sin(headAngle2) * headSize, 0.01
            );

            // Color based on velocity magnitude
            const t = vel / maxVel;
            const color = new THREE.Color().setHSL(0.55 - t * 0.55, 0.9, 0.6);

            // 6 vertices per arrow (shaft + 2 head lines)
            for (let k = 0; k < 6; k++) {
                colors.push(color.r, color.g, color.b);
            }
        };

        for (let i = 0; i < nx; i += sampleX) {
            for (let j = 0; j < ny; j += sampleY) {
                const idx = i * ny + j;
                if (idx >= result.x.length) continue;

                // Horizontal orientation
                const posX = result.x[idx] * scalePos - 10;
                const posY = result.r[idx] * scalePos;

                const vx = result.velocity_x[idx] || 0;
                const vy = result.velocity_r?.[idx] || 0;
                const vel = Math.sqrt(vx * vx + vy * vy);

                // Upper half
                addArrow(posX, posY, vx, vy, vel);
                // Lower half (mirrored)
                addArrow(posX, -posY, vx, -vy, vel);
            }
        }

        if (positions.length === 0) return null;

        const geom = new THREE.BufferGeometry();
        geom.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
        geom.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
        return geom;
    }, [result, scale]);

    if (!arrowsGeometry) return null;

    return (
        <lineSegments geometry={arrowsGeometry}>
            <lineBasicMaterial attach="material" vertexColors transparent opacity={0.8} />
        </lineSegments>
    );
}

// ============================================================================
// COMPONENT: NOZZLE CONTOUR OUTLINE
// ============================================================================

function NozzleContour({ result }: { result: CFDResult }) {
    const { wallGeomUpper, wallGeomLower, axisGeom } = useMemo(() => {
        const nx = result.nx;
        const ny = result.ny;
        if (nx < 2 || ny < 2) return { wallGeomUpper: null, wallGeomLower: null, axisGeom: null };

        const max_x = Math.max(...result.x) || 1;
        const scale = 20 / max_x;

        // Extract wall radii to find nozzle exit
        const wallRadii: number[] = [];
        const wallX: number[] = [];
        for (let i = 0; i < nx; i++) {
            const idx = i * ny + (ny - 1);
            if (idx < result.x.length) {
                wallRadii.push(result.r[idx]);
                wallX.push(result.x[idx]);
            }
        }

        // Find throat (minimum radius)
        let throatIdx = 0;
        let minR = Infinity;
        for (let i = 0; i < wallRadii.length; i++) {
            if (wallRadii[i] < minR) {
                minR = wallRadii[i];
                throatIdx = i;
            }
        }

        // Find nozzle exit: after throat, find where radius stops increasing 
        // or starts decreasing (that's where far-field begins)
        let exitIdx = wallRadii.length - 1;
        for (let i = throatIdx + 1; i < wallRadii.length - 1; i++) {
            // If radius starts decreasing or stays flat after divergent, that's the exit
            if (wallRadii[i + 1] < wallRadii[i] - 0.0001) {
                exitIdx = i;
                break;
            }
            // Also detect if we're past the main divergent section (far-field typically has linear expansion)
            // Check for sudden change in slope
            if (i > throatIdx + 5) {
                const slope1 = (wallRadii[i] - wallRadii[i - 1]) / (wallX[i] - wallX[i - 1] + 1e-10);
                const slope2 = (wallRadii[i + 1] - wallRadii[i]) / (wallX[i + 1] - wallX[i] + 1e-10);
                // If slope suddenly increases a lot (far-field expansion), stop here
                if (slope2 > slope1 * 2 && slope2 > 0.3) {
                    exitIdx = i;
                    break;
                }
            }
        }

        const wallPositionsUpper: number[] = [];
        const wallPositionsLower: number[] = [];
        const axisPositions: number[] = [];

        // Only draw wall contour up to nozzle exit (not far-field)
        for (let i = 0; i <= exitIdx; i++) {
            const idx = i * ny + (ny - 1);
            if (idx < result.x.length) {
                const posX = result.x[idx] * scale - 10;
                const posY = result.r[idx] * scale;
                
                wallPositionsUpper.push(posX, posY, 0.02);
                wallPositionsLower.push(posX, -posY, 0.02);
            }
        }

        // Axis line only up to nozzle exit
        for (let i = 0; i <= exitIdx; i++) {
            const idx = i * ny;
            if (idx < result.x.length) {
                const posX = result.x[idx] * scale - 10;
                axisPositions.push(posX, 0, 0.02);
            }
        }

        // Add closing lines at exit (vertical lines to show nozzle end)
        if (exitIdx > 0) {
            const exitWallIdx = exitIdx * ny + (ny - 1);
            const exitAxisIdx = exitIdx * ny;
            if (exitWallIdx < result.x.length && exitAxisIdx < result.x.length) {
                const exitX = result.x[exitWallIdx] * scale - 10;
                const exitR = result.r[exitWallIdx] * scale;
                // Add exit plane vertices
                wallPositionsUpper.push(exitX, exitR, 0.02);
                wallPositionsLower.push(exitX, -exitR, 0.02);
            }
        }

        const wGeomUpper = new THREE.BufferGeometry();
        wGeomUpper.setAttribute('position', new THREE.Float32BufferAttribute(wallPositionsUpper, 3));

        const wGeomLower = new THREE.BufferGeometry();
        wGeomLower.setAttribute('position', new THREE.Float32BufferAttribute(wallPositionsLower, 3));

        const aGeom = new THREE.BufferGeometry();
        aGeom.setAttribute('position', new THREE.Float32BufferAttribute(axisPositions, 3));

        return { wallGeomUpper: wGeomUpper, wallGeomLower: wGeomLower, axisGeom: aGeom };
    }, [result]);

    if (!wallGeomUpper || !wallGeomLower || !axisGeom) return null;

    return (
        <group>
            {/* Upper wall contour */}
            <primitive object={new THREE.Line(wallGeomUpper, new THREE.LineBasicMaterial({ color: 0x00ffff, opacity: 0.9, transparent: true, linewidth: 2 }))} />
            {/* Lower wall contour (mirrored) */}
            <primitive object={new THREE.Line(wallGeomLower, new THREE.LineBasicMaterial({ color: 0x00ffff, opacity: 0.9, transparent: true, linewidth: 2 }))} />
            {/* Centerline axis */}
            <primitive object={new THREE.Line(axisGeom, new THREE.LineBasicMaterial({ color: 0xffffff, opacity: 0.15, transparent: true }))} />
        </group>
    );
}

// ============================================================================
// COMPONENT: RESIDUAL PLOT
// ============================================================================

function ResidualPlot({ history }: { history: number[] }) {
    if (!history || history.length < 2) {
        return <div className="text-gray-500 text-xs italic">Pas de données de convergence</div>;
    }

    const width = 200;
    const height = 80;
    const padding = 10;

    const logValues = history.map(v => Math.log10(Math.max(v, 1e-12)));
    const min = Math.min(...logValues);
    const max = Math.max(...logValues);
    const range = max - min || 1;

    const points = logValues.map((val, i) => {
        const x = padding + (i / (history.length - 1)) * (width - 2 * padding);
        const y = height - (padding + ((val - min) / range) * (height - 2 * padding));
        return `${x},${y}`;
    }).join(" ");

    return (
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-full">
            <defs>
                <linearGradient id="residualGrad" x1="0%" y1="0%" x2="100%" y2="0%">
                    <stop offset="0%" stopColor="#06b6d4" />
                    <stop offset="100%" stopColor="#22c55e" />
                </linearGradient>
            </defs>
            {/* Grid lines */}
            <g stroke="#27272a" strokeWidth="0.5">
                {[0.25, 0.5, 0.75].map(f => (
                    <line key={f} x1={padding} x2={width - padding} y1={height - padding - f * (height - 2 * padding)} y2={height - padding - f * (height - 2 * padding)} />
                ))}
            </g>
            {/* Curve */}
            <polyline points={points} fill="none" stroke="url(#residualGrad)" strokeWidth="2" strokeLinecap="round" />
            {/* Labels */}
            <text x={padding} y={height - 2} fill="#666" fontSize="8" fontFamily="monospace">1e{min.toFixed(0)}</text>
            <text x={width - padding} y={padding} fill="#666" fontSize="8" fontFamily="monospace" textAnchor="end">1e{max.toFixed(0)}</text>
        </svg>
    );
}

// ============================================================================
// COMPONENT: DYNAMIC LEGEND
// ============================================================================

function DynamicLegend({ field, min, max, colormap }: { field: FieldType; min: number; max: number; colormap: string }) {
    const gradientId = `legend-grad-${colormap}`;
    const config = FIELD_CONFIG[field];

    // Generate gradient stops
    const stops = useMemo(() => {
        const numStops = 10;
        return Array.from({ length: numStops }, (_, i) => {
            const t = i / (numStops - 1);
            const color = getColorForValue(t, colormap);
            return { offset: `${t * 100}%`, color: `#${color.getHexString()}` };
        });
    }, [colormap]);

    const formatValue = (v: number) => {
        if (field === "pressure") return `${(v / 1e5).toFixed(1)}`;
        if (field === "temperature") return `${v.toFixed(0)}`;
        if (field === "velocity_x") return `${v.toFixed(0)}`;
        if (field === "density") return v.toFixed(2);
        return v.toFixed(2);
    };

    return (
        <div className="absolute bottom-4 right-4 bg-black/80 p-3 rounded-lg border border-cyan-900/50 backdrop-blur-sm">
            <div className="text-cyan-400 text-xs font-bold mb-2">{config.name} {config.unit && `(${config.unit})`}</div>
            <svg width="140" height="20" className="mb-1">
                <defs>
                    <linearGradient id={gradientId} x1="0%" y1="0%" x2="100%" y2="0%">
                        {stops.map((s, i) => (
                            <stop key={i} offset={s.offset} stopColor={s.color} />
                        ))}
                    </linearGradient>
                </defs>
                <rect x="0" y="0" width="140" height="12" rx="2" fill={`url(#${gradientId})`} />
            </svg>
            <div className="flex justify-between text-[10px] text-gray-400 font-mono">
                <span>{formatValue(min)}</span>
                <span>{formatValue((min + max) / 2)}</span>
                <span>{formatValue(max)}</span>
            </div>
        </div>
    );
}

// ============================================================================
// COMPONENT: PROGRESS BAR
// ============================================================================

function ProgressBar({ progress, message }: { progress: number; message: string }) {
    return (
        <div className="bg-[#1a1a25] rounded-lg border border-[#27272a] p-4">
            <div className="flex justify-between items-center mb-2">
                <span className="text-sm text-gray-400">{message}</span>
                <span className="text-sm font-mono text-cyan-400">{(progress * 100).toFixed(1)}%</span>
            </div>
            <div className="h-2 bg-[#0a0a0f] rounded-full overflow-hidden">
                <div
                    className="h-full bg-gradient-to-r from-cyan-600 to-blue-500 transition-all duration-300 ease-out"
                    style={{ width: `${progress * 100}%` }}
                />
            </div>
        </div>
    );
}

// ============================================================================
// MAIN PAGE COMPONENT
// ============================================================================

export default function CFDPage() {
    const { config: mainConfig, results } = useCalculation();

    // State
    const [status, setStatus] = useState<"idle" | "running" | "completed" | "error">("idle");
    const [progress, setProgress] = useState(0);
    const [progressMessage, setProgressMessage] = useState("");
    const [logs, setLogs] = useState<string[]>([]);
    const [result, setResult] = useState<CFDResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [field, setField] = useState<FieldType>("mach");

    // Visualization options
    const [showContours, setShowContours] = useState(true);
    const [contourInterval, setContourInterval] = useState(0.5);
    const [showWireframe, setShowWireframe] = useState(false);
    const [showVectorField, setShowVectorField] = useState(false);
    const [tooltip, setTooltip] = useState<TooltipData | null>(null);

    // Save state
    const [currentJobId, setCurrentJobId] = useState<string | null>(null);
    const [currentParams, setCurrentParams] = useState<Record<string, unknown> | null>(null);
    const [saving, setSaving] = useState(false);
    const [saveName, setSaveName] = useState("");
    const [showSaveDialog, setShowSaveDialog] = useState(false);

    const abortControllerRef = useRef<AbortController | null>(null);
    const OPENFOAM_API = process.env.NEXT_PUBLIC_OPENFOAM_URL || "/api/cfd";

    const addLog = useCallback((message: string) => {
        setLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ${message}`]);
    }, []);

    // ========================================================================
    // RUN SIMULATION - SYNCHRONISÉ AVEC LE CONTEXTE DE CALCUL
    // ========================================================================
    const runSimulation = async () => {
        if (status === "running") return;

        setStatus("running");
        setProgress(0);
        setProgressMessage("Initialisation...");
        setLogs([]);
        setResult(null);
        setError(null);

        addLog("🚀 Initialisation de la simulation OpenFOAM...");

        if (abortControllerRef.current) abortControllerRef.current.abort();
        abortControllerRef.current = new AbortController();

        try {
            // ================================================================
            // EXTRACTION DYNAMIQUE DE TOUTES LES VALEURS DU CONTEXTE
            // ================================================================
            
            // Géométrie (depuis results ou valeurs par défaut)
            const r_throat = results?.r_throat ?? 0.025;          // [m]
            const r_chamber = results?.r_chamber ?? 0.05;         // [m]
            const r_exit = results?.r_exit ?? 0.075;              // [m]
            const l_chamber = results?.l_chamber ?? 0.1;          // [m]
            const l_nozzle = results?.l_nozzle ?? 0.2;            // [m]
            
            // Conditions thermodynamiques (depuis CEA via results)
            const t_chamber = results?.t_chamber ?? 3000;          // [K]
            const gamma = results?.gamma ?? 1.2;                   // [-]
            const mw_gmol = results?.mw ?? 20;                     // [g/mol] (CEA output)
            
            // Pression : mainConfig.pc est en bar, convertir en Pa
            const p_chamber_pa = mainConfig.pc * 1e5;              // bar → Pa
            const p_ambient_pa = mainConfig.pamb * 1e5;            // bar → Pa
            
            // Masse molaire : convertir g/mol → kg/mol pour le backend
            const molar_mass_kgmol = mw_gmol / 1000;               // g/mol → kg/mol

            const simParams = {
                // Géométrie
                r_throat,
                r_chamber,
                r_exit,
                l_chamber,
                l_nozzle,
                
                // Conditions thermodynamiques
                p_chamber: p_chamber_pa,
                p_ambient: p_ambient_pa,
                t_chamber,
                gamma,
                molar_mass: molar_mass_kgmol,
                
                // Résolution du maillage (haute résolution)
                nx: 200,
                ny: 80,
                
                // Paramètres solveur
                max_iter: 5000,
                tolerance: 1e-6,
                solver: "openfoam"
            };

            addLog("📊 Paramètres extraits du contexte de calcul :");
            addLog(`   • Géométrie: Rt=${(r_throat * 1000).toFixed(2)}mm, Rc=${(r_chamber * 1000).toFixed(2)}mm, Re=${(r_exit * 1000).toFixed(2)}mm`);
            addLog(`   • Longueurs: Lc=${(l_chamber * 1000).toFixed(1)}mm, Ln=${(l_nozzle * 1000).toFixed(1)}mm`);
            addLog(`   • Pression chambre: ${(p_chamber_pa / 1e5).toFixed(2)} bar (${(p_chamber_pa / 1e6).toFixed(2)} MPa)`);
            addLog(`   • Température chambre: ${t_chamber.toFixed(0)} K`);
            addLog(`   • Gamma (Cp/Cv): ${gamma.toFixed(4)}`);
            addLog(`   • Masse molaire: ${mw_gmol.toFixed(2)} g/mol → ${(molar_mass_kgmol * 1000).toFixed(2)} g/mol pour OpenFOAM`);
            addLog(`   • Maillage: ${simParams.nx}×${simParams.ny} = ${simParams.nx * simParams.ny} cellules`);

            setProgress(0.05);
            setProgressMessage("Envoi au serveur OpenFOAM...");
            addLog("📡 Envoi de la requête au serveur OpenFOAM...");

            const startResponse = await fetch(`${OPENFOAM_API}/run`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(simParams),
                signal: abortControllerRef.current.signal,
            });

            if (!startResponse.ok) {
                const text = await startResponse.text();
                throw new Error(`Erreur démarrage (${startResponse.status}): ${text}`);
            }

            const jobInfo = await startResponse.json();
            const jobId = jobInfo.job_id;
            setCurrentJobId(jobId);
            setCurrentParams(simParams);
            addLog(`✅ Job créé: ${jobId} (${jobInfo.message})`);

            setProgress(0.1);
            setProgressMessage("Simulation en cours...");

            // ================================================================
            // POLLING AVEC PROGRESS BAR BASÉE SUR LES LOGS RÉELS
            // ================================================================
            let completed = false;
            let attempts = 0;
            const maxAttempts = 600;

            while (!completed && attempts < maxAttempts) {
                await new Promise(r => setTimeout(r, 1500));
                attempts++;

                const statusRes = await fetch(`${OPENFOAM_API}/status?jobId=${jobId}`, {
                    signal: abortControllerRef.current.signal
                });

                if (!statusRes.ok) throw new Error("Erreur vérification status");

                const statusData = await statusRes.json();
                const serverProgress = statusData.progress || 0;

                setProgress(serverProgress);
                setProgressMessage(statusData.message || "Calcul...");

                if (statusData.status === "running") {
                    if (attempts % 3 === 0) {
                        addLog(`⏳ ${statusData.message} [${(serverProgress * 100).toFixed(1)}%]`);
                    }
                } else if (statusData.status === "completed") {
                    completed = true;
                    setProgress(0.95);
                    setProgressMessage("Post-traitement...");
                    addLog("🏁 Simulation terminée avec succès !");
                } else if (statusData.status === "failed") {
                    throw new Error(`Simulation échouée: ${statusData.message}`);
                }
            }

            if (!completed) throw new Error("Timeout: La simulation prend trop de temps (>15min).");

            addLog("📥 Téléchargement des résultats...");
            const resultRes = await fetch(`${OPENFOAM_API}/result?jobId=${jobId}`, {
                signal: abortControllerRef.current.signal
            });

            if (!resultRes.ok) throw new Error("Erreur récupération résultats");

            const resultData: CFDResult = await resultRes.json();
            setResult(resultData);
            setStatus("completed");
            setProgress(1);
            setProgressMessage("Terminé !");

            // Statistiques
            const machMax = Math.max(...(resultData.mach || [0]));
            const pMin = Math.min(...(resultData.pressure || [0]));
            const tMax = Math.max(...(resultData.temperature || [0]));

            addLog(`✨ Résultats chargés (solveur: ${resultData.solver || 'openfoam'})`);
            addLog(`   • Mach max: ${machMax.toFixed(3)}`);
            addLog(`   • Pression min: ${(pMin / 1e5).toFixed(2)} bar`);
            addLog(`   • Température max: ${tMax.toFixed(0)} K`);
            addLog(`   • Convergé: ${resultData.converged ? '✅ OUI' : '❌ NON'}`);

            // Track activity
            trackActivity("cfd_run", {
                jobId,
                converged: resultData.converged,
                iterations: resultData.iterations,
                machMax,
                solver: resultData.solver
            });

        } catch (err: unknown) {
            const error = err as Error;
            if (error.name === 'AbortError') {
                addLog("🛑 Simulation annulée.");
                setStatus("idle");
            } else {
                console.error(err);
                setError(error.message || "Erreur inconnue");
                addLog(`❌ Erreur: ${error.message}`);
                setStatus("error");
            }
            setProgress(0);
            setProgressMessage("");
        }
    };

    // ========================================================================
    // SAVE & EXPORT
    // ========================================================================
    const saveSimulation = async () => {
        if (!result || !saveName.trim()) return;

        setSaving(true);
        try {
            const response = await fetch("/api/cfd/save", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    name: saveName.trim(),
                    description: `OpenFOAM Simulation - Job ${currentJobId}`,
                    jobId: currentJobId,
                    params: currentParams,
                    result: result
                })
            });

            if (response.ok) {
                addLog("💾 Simulation sauvegardée avec succès !");
                setShowSaveDialog(false);
                setSaveName("");
            } else {
                const data = await response.json();
                addLog(`❌ Erreur sauvegarde: ${data.error}`);
            }
        } catch (err: unknown) {
            const error = err as Error;
            addLog(`❌ Erreur sauvegarde: ${error.message}`);
        } finally {
            setSaving(false);
        }
    };

    const exportResults = () => {
        if (!result) return;

        const exportData = {
            metadata: {
                jobId: currentJobId,
                exportedAt: new Date().toISOString(),
                solver: result.solver || "openfoam",
                converged: result.converged,
                iterations: result.iterations
            },
            params: currentParams,
            grid: {
                nx: result.nx,
                ny: result.ny,
                x: result.x,
                r: result.r
            },
            fields: {
                mach: result.mach,
                pressure: result.pressure,
                temperature: result.temperature,
                velocity_x: result.velocity_x,
                velocity_r: result.velocity_r,
                density: result.density
            },
            convergence: {
                residual_history: result.residual_history
            }
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cfd-simulation-${currentJobId || 'export'}.json`;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        addLog("📁 Résultats exportés en JSON !");
    };

    // ========================================================================
    // COMPUTED VALUES
    // ========================================================================
    const fieldMinMax = useMemo(() => {
        if (!result) return { min: 0, max: 1 };
        const data = result[field];
        if (!data || data.length === 0) return { min: 0, max: 1 };

        let min = Infinity, max = -Infinity;
        for (const v of data) {
            if (Number.isFinite(v)) {
                if (v < min) min = v;
                if (v > max) max = v;
            }
        }
        if (!Number.isFinite(min)) return { min: 0, max: 1 };
        return { min, max };
    }, [result, field]);

    // Auto-adjust contour interval based on field
    useEffect(() => {
        if (!result) return;
        const { min, max } = fieldMinMax;
        const range = max - min;
        // ~10 contour lines
        setContourInterval(range / 10);
    }, [field, fieldMinMax, result]);

    // ========================================================================
    // RENDER
    // ========================================================================
    return (
        <AppLayout>
            <div className="flex flex-col h-screen bg-[#0a0a0f] text-white p-6 gap-4">
                {/* Header */}
                <header className="flex justify-between items-end shrink-0">
                    <div>
                        <h1 className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-600">
                            🔥 OpenFOAM CFD Simulation
                        </h1>
                        <p className="text-gray-500 text-sm">Simulation haute-fidélité avec rhoCentralFoam • Visualisation par shaders GPU</p>
                    </div>

                    {/* Action buttons */}
                    <div className="flex gap-3 items-center">
                        {result && (
                            <>
                                <button
                                    onClick={() => setShowSaveDialog(true)}
                                    className="px-4 py-2 rounded-lg font-bold bg-green-600/20 hover:bg-green-600/40 text-green-400 border border-green-600/50 transition-all"
                                >
                                    💾 Sauvegarder
                                </button>
                                <button
                                    onClick={exportResults}
                                    className="px-4 py-2 rounded-lg font-bold bg-purple-600/20 hover:bg-purple-600/40 text-purple-400 border border-purple-600/50 transition-all"
                                >
                                    📁 Exporter
                                </button>
                            </>
                        )}
                        <button
                            onClick={runSimulation}
                            disabled={status === "running"}
                            className={`px-6 py-2.5 rounded-lg font-bold transition-all ${status === "running"
                                    ? "bg-gray-800 cursor-not-allowed text-gray-500"
                                    : "bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white shadow-lg shadow-cyan-500/30"
                                }`}
                        >
                            {status === "running" ? "⏳ Simulation en cours..." : "🚀 Lancer Simulation"}
                        </button>
                    </div>
                </header>

                {/* Progress bar (when running) */}
                {status === "running" && (
                    <ProgressBar progress={progress} message={progressMessage} />
                )}

                {/* Error display */}
                {error && (
                    <div className="bg-red-900/30 border border-red-600/50 rounded-lg p-4 text-red-400">
                        <strong>Erreur:</strong> {error}
                    </div>
                )}

                {/* Save Dialog Modal */}
                {showSaveDialog && (
                    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50 backdrop-blur-sm">
                        <div className="bg-[#1a1a25] rounded-xl border border-cyan-900/50 p-6 w-96 shadow-2xl">
                            <h3 className="text-lg font-bold mb-4 text-cyan-400">💾 Sauvegarder la Simulation</h3>
                            <input
                                type="text"
                                value={saveName}
                                onChange={(e) => setSaveName(e.target.value)}
                                placeholder="Nom de la simulation..."
                                className="w-full px-4 py-3 bg-[#0a0a0f] border border-[#27272a] rounded-lg mb-4 text-white focus:border-cyan-500 focus:outline-none transition-colors"
                                autoFocus
                            />
                            <div className="flex gap-3 justify-end">
                                <button
                                    onClick={() => setShowSaveDialog(false)}
                                    className="px-4 py-2 rounded-lg bg-gray-700 hover:bg-gray-600 text-white transition-colors"
                                >
                                    Annuler
                                </button>
                                <button
                                    onClick={saveSimulation}
                                    disabled={!saveName.trim() || saving}
                                    className="px-4 py-2 rounded-lg bg-green-600 hover:bg-green-500 text-white disabled:opacity-50 transition-colors"
                                >
                                    {saving ? "⏳ Sauvegarde..." : "✓ Sauvegarder"}
                                </button>
                            </div>
                        </div>
                    </div>
                )}

                {/* Main Content */}
                <div className="flex flex-1 gap-4 min-h-0">
                    {/* Left Panel: Logs & Stats */}
                    <div className="w-80 flex flex-col gap-4 shrink-0">
                        {/* Logs Console */}
                        <div className="flex-1 bg-[#1a1a25] rounded-xl border border-[#27272a] p-4 flex flex-col overflow-hidden">
                            <h2 className="text-cyan-400 font-bold mb-3 uppercase text-xs tracking-wider border-b border-[#27272a] pb-2">
                                📋 Logs de Simulation
                            </h2>
                            <div className="flex-1 overflow-y-auto space-y-1 font-mono text-xs scrollbar-thin scrollbar-thumb-gray-700">
                                {logs.length === 0 && (
                                    <span className="text-gray-600 italic">En attente de démarrage...</span>
                                )}
                                {logs.map((log, i) => (
                                    <div key={i} className="text-gray-300 border-b border-[#27272a]/30 pb-1 leading-relaxed">
                                        {log}
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Stats Panel */}
                        {result && (
                            <div className="bg-[#1a1a25] rounded-xl border border-[#27272a] p-4 shrink-0">
                                <h2 className="text-cyan-400 font-bold mb-3 uppercase text-xs tracking-wider">📊 Statistiques</h2>

                                <div className="grid grid-cols-2 gap-2 mb-4">
                                    <div className="bg-[#0a0a0f] p-3 rounded-lg border border-purple-900/30">
                                        <div className="text-gray-500 text-[10px] uppercase">Mach Max</div>
                                        <div className="text-purple-400 font-bold text-xl">{Math.max(...(result.mach || [0])).toFixed(2)}</div>
                                    </div>
                                    <div className="bg-[#0a0a0f] p-3 rounded-lg border border-orange-900/30">
                                        <div className="text-gray-500 text-[10px] uppercase">Pression Min</div>
                                        <div className="text-orange-400 font-bold text-xl">{(Math.min(...(result.pressure || [0])) / 1e5).toFixed(1)} bar</div>
                                    </div>
                                    <div className="bg-[#0a0a0f] p-3 rounded-lg border border-red-900/30">
                                        <div className="text-gray-500 text-[10px] uppercase">Temp Max</div>
                                        <div className="text-red-400 font-bold text-xl">{Math.max(...(result.temperature || [0])).toFixed(0)} K</div>
                                    </div>
                                    <div className="bg-[#0a0a0f] p-3 rounded-lg border border-green-900/30">
                                        <div className="text-gray-500 text-[10px] uppercase">Vitesse Max</div>
                                        <div className="text-green-400 font-bold text-xl">{Math.max(...(result.velocity_x || [0])).toFixed(0)} m/s</div>
                                    </div>
                                </div>

                                <h3 className="text-gray-500 font-bold mb-2 uppercase text-[10px]">Convergence</h3>
                                <div className="h-20 w-full bg-[#0a0a0f] rounded-lg border border-[#27272a] p-1">
                                    <ResidualPlot history={result.residual_history || []} />
                                </div>
                            </div>
                        )}
                    </div>

                    {/* Right Panel: Visualization */}
                    <div className="flex-1 bg-[#1a1a25] rounded-xl border border-[#27272a] p-4 flex flex-col overflow-hidden">
                        {/* Toolbar */}
                        <div className="flex justify-between items-center mb-3 flex-wrap gap-2">
                            {/* Field selector */}
                            <div className="flex bg-[#0a0a0f] rounded-lg p-1 border border-[#27272a]">
                                {(Object.keys(FIELD_CONFIG) as FieldType[]).map((f) => (
                                    <button
                                        key={f}
                                        onClick={() => setField(f)}
                                        className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all ${field === f
                                                ? "bg-cyan-600 text-white shadow-lg shadow-cyan-600/30"
                                                : "text-gray-400 hover:text-white hover:bg-white/5"
                                            }`}
                                    >
                                        {FIELD_CONFIG[f].name}
                                    </button>
                                ))}
                            </div>

                            {/* Visualization options */}
                            <div className="flex gap-2">
                                <button
                                    onClick={() => setShowContours(!showContours)}
                                    className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all border ${showContours
                                            ? "bg-cyan-600/20 text-cyan-400 border-cyan-600/50"
                                            : "bg-transparent text-gray-500 border-gray-700 hover:text-gray-300"
                                        }`}
                                >
                                    📈 Contours
                                </button>
                                <button
                                    onClick={() => setShowWireframe(!showWireframe)}
                                    className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all border ${showWireframe
                                            ? "bg-cyan-600/20 text-cyan-400 border-cyan-600/50"
                                            : "bg-transparent text-gray-500 border-gray-700 hover:text-gray-300"
                                        }`}
                                >
                                    🔲 Maillage
                                </button>
                                <button
                                    onClick={() => setShowVectorField(!showVectorField)}
                                    className={`px-3 py-1.5 rounded-md text-xs font-bold transition-all border ${showVectorField
                                            ? "bg-cyan-600/20 text-cyan-400 border-cyan-600/50"
                                            : "bg-transparent text-gray-500 border-gray-700 hover:text-gray-300"
                                        }`}
                                >
                                    ➡️ Vecteurs
                                </button>
                            </div>
                        </div>

                        {/* Canvas */}
                        <div className="flex-1 bg-[#050508] rounded-lg border border-[#27272a] relative overflow-hidden">
                            {result ? (
                                <>
                                    <Canvas orthographic camera={{ zoom: 28, position: [0, 0, 50] }}>
                                        <color attach="background" args={["#050508"]} />
                                        <CFDHeatmapShader
                                            result={result}
                                            field={field}
                                            colormap={FIELD_CONFIG[field].colormap}
                                            showContours={showContours}
                                            contourInterval={contourInterval}
                                            showWireframe={showWireframe}
                                            onHover={setTooltip}
                                        />
                                        {showVectorField && <VectorFieldOverlay result={result} scale={1.2} />}
                                        <NozzleContour result={result} />
                                    </Canvas>

                                    {/* Dynamic Legend */}
                                    <DynamicLegend
                                        field={field}
                                        min={fieldMinMax.min}
                                        max={fieldMinMax.max}
                                        colormap={FIELD_CONFIG[field].colormap}
                                    />

                                    {/* Tooltip */}
                                    {tooltip && (
                                        <div
                                            className="absolute pointer-events-none bg-black/90 px-3 py-2 rounded-lg border border-cyan-800/50 text-xs font-mono shadow-xl"
                                            style={{
                                                left: '50%',
                                                top: 16,
                                                transform: 'translateX(-50%)'
                                            }}
                                        >
                                            <div className="grid grid-cols-2 gap-x-4 gap-y-1">
                                                <span className="text-gray-500">Position:</span>
                                                <span className="text-white">x={tooltip.worldX.toFixed(4)}m, r={tooltip.worldR.toFixed(4)}m</span>
                                                <span className="text-purple-400">Mach:</span>
                                                <span className="text-white font-bold">{tooltip.mach.toFixed(3)}</span>
                                                <span className="text-orange-400">Pression:</span>
                                                <span className="text-white font-bold">{(tooltip.pressure / 1e5).toFixed(2)} bar</span>
                                                <span className="text-red-400">Température:</span>
                                                <span className="text-white font-bold">{tooltip.temperature.toFixed(0)} K</span>
                                                <span className="text-green-400">Vitesse:</span>
                                                <span className="text-white font-bold">{tooltip.velocity.toFixed(0)} m/s</span>
                                            </div>
                                        </div>
                                    )}

                                    {/* Info overlay */}
                                    <div className="absolute top-3 left-3 text-[10px] text-gray-600 font-mono">
                                        {result.nx}×{result.ny} mesh • {result.solver || 'openfoam'} • {result.converged ? '✓ converged' : '⚠ not converged'}
                                    </div>
                                </>
                            ) : (
                                <div className="flex items-center justify-center h-full">
                                    <div className="text-center">
                                        <div className="text-6xl mb-4 opacity-20">🚀</div>
                                        <div className="text-gray-600 italic">
                                            Cliquez sur &quot;Lancer Simulation&quot; pour démarrer
                                        </div>
                                        <div className="text-gray-700 text-xs mt-2">
                                            Les paramètres seront extraits automatiquement du contexte de calcul
                                        </div>
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>
        </AppLayout>
    );
}
