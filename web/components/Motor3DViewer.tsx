"use client";

import { useRef, useMemo, useEffect } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Environment } from "@react-three/drei";
import * as THREE from "three";

interface MotorMeshProps {
    profile: { x: number[]; r: number[] } | null;
    showInner?: boolean;
    showChannels?: boolean;
    showOuter?: boolean;
    nChannels?: number;
    rotate?: boolean;
    wallColor?: string;
    outerShellColor?: string;
    wallThickness?: number; // in mm
    outerShellThickness?: number; // in mm
}

function MotorMesh({
    profile,
    showInner = true,
    showChannels = false,
    showOuter = false,
    nChannels = 60,
    rotate = true,
    wallColor = "#cc7733",
    outerShellColor = "#71717a",
    wallThickness = 2, // Liner thickness
    outerShellThickness = 2 // Jacket thickness
}: MotorMeshProps) {
    const meshRef = useRef<THREE.Mesh>(null);
    const groupRef = useRef<THREE.Group>(null);
    const ribsRef = useRef<THREE.InstancedMesh>(null);

    useFrame((state) => {
        if (groupRef.current && rotate) {
            groupRef.current.rotation.y = state.clock.elapsedTime * 0.2;
        }
    });

    /**
     * Generate nozzle radius using Python's Bézier curve algorithm (Rao method)
     * This matches the oldmain.py calculate_geometry_profile function
     */
    const getDefaultRadius = (t: number): number => {
        // Geometry parameters (matching typical motor)
        const rThroat = 0.020;  // 20mm throat radius
        const contractionRatio = 3.5;
        const expansionRatio = 8.0;
        const rChamber = rThroat * Math.sqrt(contractionRatio);
        const rExit = rThroat * Math.sqrt(expansionRatio);

        // Lengths (normalized t goes from 0 to 1)
        const totalLength = 0.35;  // meters
        const lChamber = 0.12;     // chamber length
        const lNozzle = totalLength - lChamber;  // nozzle length

        // Angles (Python defaults)
        const thetaN = 30 * Math.PI / 180;  // 30° initial nozzle angle
        const thetaE = 8 * Math.PI / 180;   // 8° exit angle

        // Convergent section ratio
        const lConv = (rChamber - rThroat) * 1.5;
        const chamberStart = 0;
        const convStart = lChamber - lConv;
        const throatPos = lChamber;

        const x = t * totalLength;

        if (x < convStart) {
            // Cylindrical chamber
            return rChamber;
        } else if (x < throatPos) {
            // Convergent with cosine curve (smooth like Python)
            const xLocal = x - convStart;
            const tConv = xLocal / lConv;
            return rThroat + (rChamber - rThroat) * (1.0 - Math.sin(Math.PI * tConv / 2.0));
        } else {
            // Divergent with Bézier quadratic curve (Rao method)
            const xLocal = x - throatPos;
            const lb = lNozzle;

            // Bézier control points
            const p0 = { x: 0, y: rThroat };
            const p2 = { x: lb, y: rExit };
            const tanN = Math.tan(thetaN);
            const tanE = Math.tan(thetaE);

            // P1 = intersection of tangent lines
            let denom = tanN - tanE;
            if (Math.abs(denom) < 1e-9) denom = 1e-9;
            const xInt = (rExit - rThroat - tanE * lb) / denom;
            const p1 = { x: xInt, y: tanN * xInt + rThroat };

            // Bézier parameter (0 to 1 along nozzle)
            const tBez = Math.min(1.0, xLocal / lb);
            const oneMinusT = 1.0 - tBez;

            // Quadratic Bézier: B(t) = (1-t)²P0 + 2(1-t)tP1 + t²P2
            const r = oneMinusT * oneMinusT * p0.y
                + 2.0 * oneMinusT * tBez * p1.y
                + tBez * tBez * p2.y;

            return r;
        }
    };

    // 1. Inner Liner Geometry
    const innerGeometry = useMemo(() => {
        let points: THREE.Vector2[] = [];

        if (!profile || !profile.x || !profile.r) {
            for (let i = 0; i <= 50; i++) {
                const t = i / 50;
                const x = t * 0.35;
                const r = getDefaultRadius(t);
                points.push(new THREE.Vector2(r, x - 0.175));
            }
        } else {
            points = profile.x.map((x, i) =>
                new THREE.Vector2(profile.r[i], x - profile.x[profile.x.length - 1] / 2)
            );
        }
        // LatheGeometry expects points to be Vector2(r, y) where axis of rotation is Y
        return new THREE.LatheGeometry(points, 64);
    }, [profile]);

    // 2. Outer Jacket Geometry
    const outerGeometry = useMemo(() => {
        // The jacket sits on top of the ribs.
        // Radius = Inner Radius + Liner Thickness + Channel Height + Jacket Thickness/2 ?
        // Usually Jacket starts AFTER the channels.
        // So R_Jacket_Inner = R_Inner + Liner + ChannelHeight.
        const channelHeight = 0.005; // 5mm fixed channel height for viz
        const t_offset = (wallThickness / 1000) + channelHeight;

        // We want the jacket mesh to represent the THICKNESS of the jacket?
        // Or just the surface? Let's give it thickness by using standard Lathe but potentially with backface?
        // Or just a single shell at the outer radius.

        let points: THREE.Vector2[] = [];
        if (!profile || !profile.x || !profile.r) {
            for (let i = 0; i <= 50; i++) {
                const t = i / 50;
                const x = t * 0.35;
                const r = getDefaultRadius(t) + t_offset;
                points.push(new THREE.Vector2(r, x - 0.175));
            }
        } else {
            points = profile.x.map((x, i) =>
                new THREE.Vector2(profile.r[i] + t_offset, x - profile.x[profile.x.length - 1] / 2)
            );
        }
        return new THREE.LatheGeometry(points, 64);
    }, [profile, wallThickness]);

    // 3. Rib (Separator) Geometry
    // We create a SINGLE rib geometry that follows the profile, then instance it.
    const ribGeometry = useMemo(() => {
        // Custom BufferGeometry
        // We create a strip of quads following the profile.
        // Width of rib = 1.5mm?
        const ribWidth = 0.0015;
        const channelHeight = 0.005; // 5mm

        // Get profile points
        let xs: number[] = [];
        let rs: number[] = [];

        if (!profile || !profile.x || !profile.r) {
            for (let i = 0; i <= 50; i++) {
                const t = i / 50;
                xs.push(t * 0.35 - 0.175);
                rs.push(getDefaultRadius(t));
            }
        } else {
            xs = profile.x.map(x => x - profile.x[profile.x.length - 1] / 2);
            rs = [...profile.r];
        }

        // Build vertices and indices
        const vertices: number[] = [];
        const indices: number[] = [];
        const normals: number[] = [];

        // For each segment i to i+1
        for (let i = 0; i < xs.length; i++) {
            const x = xs[i];
            const r = rs[i] + wallThickness / 1000; // Start on top of liner

            // We define a cross section at this x,r
            // 4 vertices per profile point:
            // 0: Bottom-Left (-width/2)
            // 1: Bottom-Right (+width/2)
            // 2: Top-Left (-width/2)
            // 3: Top-Right (+width/2)

            // Vertices
            // y is along the axis (x in our data), z/x are radial in Threejs frame if we rotate?
            // Wait, we are building this in a canonical frame where we will rotate Y.
            // So we build it at Angle 0.
            // X is radial (r), Y is axial (x), Z is tangential width.

            // BL
            vertices.push(r, x, -ribWidth / 2);
            // BR
            vertices.push(r, x, ribWidth / 2);
            // TL
            vertices.push(r + channelHeight, x, -ribWidth / 2);
            // TR
            vertices.push(r + channelHeight, x, ribWidth / 2);

            // Normals (approximate, pointing out)
            // Just simple box normals? We need smooth shading? Flat is fine for ribs.
            normals.push(1, 0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 0);
        }

        // Indices
        for (let i = 0; i < xs.length - 1; i++) {
            const base = i * 4;
            // Face Side 1 (Left) - BL, TL, NextTL, NextBL
            indices.push(base + 0, base + 4, base + 2);
            indices.push(base + 2, base + 4, base + 6);

            // Face Side 2 (Right) - BR, NextBR, NextTR, TR
            indices.push(base + 1, base + 3, base + 5);
            indices.push(base + 3, base + 7, base + 5);

            // Face Top - TL, TR, NextTR, NextTL
            indices.push(base + 2, base + 6, base + 3);
            indices.push(base + 3, base + 6, base + 7);

            // Face Bottom? (Hidden by liner, usually) - Skip to save tris
        }

        const geom = new THREE.BufferGeometry();
        geom.setAttribute('position', new THREE.Float32BufferAttribute(vertices, 3));
        geom.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
        geom.setIndex(indices);
        geom.computeVertexNormals(); // Smooth it out

        return geom;
    }, [profile, wallThickness]);

    // Update instances
    useEffect(() => {
        if (!ribsRef.current || !showChannels) return;

        const tempObject = new THREE.Object3D();

        for (let i = 0; i < nChannels; i++) {
            const angle = (i / nChannels) * Math.PI * 2;
            tempObject.rotation.set(0, angle, 0);
            // We rotate around Y axis because our geometry was built with Y as axis, X as radius.
            tempObject.updateMatrix();
            ribsRef.current.setMatrixAt(i, tempObject.matrix);
        }
        ribsRef.current.instanceMatrix.needsUpdate = true;
    }, [nChannels, showChannels]);

    return (
        <group ref={groupRef}>
            {/* Inner Liner */}
            {showInner && (
                <mesh ref={meshRef} geometry={innerGeometry}>
                    <meshStandardMaterial
                        color={wallColor}
                        metalness={0.6}
                        roughness={0.3}
                        side={THREE.DoubleSide}
                    />
                </mesh>
            )}

            {/* Separators (Ribs) */}
            {showChannels && (
                <instancedMesh ref={ribsRef} args={[ribGeometry, undefined, nChannels]}>
                    <meshStandardMaterial
                        color={wallColor}
                        metalness={0.6}
                        roughness={0.3}
                    />
                </instancedMesh>
            )}

            {/* Outer Jacket */}
            {showOuter && (
                <mesh geometry={outerGeometry}>
                    <meshStandardMaterial
                        color={outerShellColor}
                        metalness={0.5}
                        roughness={0.5}
                        transparent
                        opacity={0.3} // Semi-transparent to see ribs
                        side={THREE.DoubleSide}
                        depthWrite={false}
                    />
                </mesh>
            )}
        </group>
    );
}

function Flames() {
    const flameRef = useRef<THREE.Mesh>(null);

    useFrame((state) => {
        if (flameRef.current) {
            flameRef.current.scale.y = 1 + Math.sin(state.clock.elapsedTime * 10) * 0.1;
            flameRef.current.scale.x = 1 + Math.sin(state.clock.elapsedTime * 8) * 0.05;
        }
    });

    return (
        <mesh ref={flameRef} position={[0, 0.2, 0]}>
            <coneGeometry args={[0.08, 0.3, 32]} />
            <meshBasicMaterial color="#ff6600" transparent opacity={0.8} />
        </mesh>
    );
}

interface Motor3DViewerProps {
    profile?: { x: number[]; r: number[] } | null;
    height?: number;
    showFlames?: boolean;

    // Viz Toggles
    showInner?: boolean;
    showChannels?: boolean;
    showOuter?: boolean;

    nChannels?: number;
    wallColor?: string;
    outerShellColor?: string;
    wallThickness?: number;
    outerShellThickness?: number;
}

export default function Motor3DViewer({
    profile = null,
    height = 400,
    showFlames = false,

    // Toggles defaults
    showInner = true,
    showChannels = true, // Default to showing channels as requested "vrais channels"
    showOuter = true,

    nChannels = 60, // Increased for "realism"
    wallColor = "#b87333", // Copper-ish
    outerShellColor = "#71717a", // Steel-ish
    wallThickness = 2,
    outerShellThickness = 2
}: Motor3DViewerProps) {
    return (
        <div style={{ height, width: "100%", background: "#09090b", borderRadius: 12, overflow: "hidden", position: "relative" }}>
            {/* Simple Overlay for controls could go here, but user asked for toggles in the tab? 
                 We will stick to passing props and letting parent control. */}
            <Canvas camera={{ position: [0.3, 0.2, 0.3], fov: 50 }}>
                <ambientLight intensity={0.5} />
                <directionalLight position={[5, 2, 5]} intensity={1.5} />
                <directionalLight position={[-5, 2, -5]} intensity={0.5} />

                {/* Environment reflection */}
                <Environment preset="city" />

                <MotorMesh
                    profile={profile}
                    showInner={showInner}
                    showChannels={showChannels}
                    showOuter={showOuter}
                    nChannels={nChannels}
                    wallColor={wallColor}
                    outerShellColor={outerShellColor}
                    wallThickness={wallThickness}
                    outerShellThickness={outerShellThickness}
                />

                {showFlames && <Flames />}

                <OrbitControls
                    enablePan={true}
                    enableZoom={true}
                    enableRotate={true}
                    autoRotate={true}
                    autoRotateSpeed={0.5}
                    minDistance={0.1}
                    maxDistance={2}
                />

                <gridHelper args={[2, 20, "#3f3f46", "#18181b"]} position={[0, -0.3, 0]} />
            </Canvas>
        </div>
    );
}

