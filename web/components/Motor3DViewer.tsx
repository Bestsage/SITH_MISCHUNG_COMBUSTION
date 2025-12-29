"use client";

import { useRef, useMemo } from "react";
import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls, Environment, MeshTransmissionMaterial, Text } from "@react-three/drei";
import * as THREE from "three";

interface MotorMeshProps {
    profile: { x: number[]; r: number[] } | null;
    showChannels?: boolean;
    nChannels?: number;
    rotate?: boolean;
}

function MotorMesh({ profile, showChannels = false, nChannels = 48, rotate = true }: MotorMeshProps) {
    const meshRef = useRef<THREE.Mesh>(null);
    const groupRef = useRef<THREE.Group>(null);

    useFrame((state) => {
        if (groupRef.current && rotate) {
            groupRef.current.rotation.y = state.clock.elapsedTime * 0.2;
        }
    });

    // Nozzle profile matching Rust backend (main.rs lines 280-301)
    // This generates the same geometry as the backend for consistency
    const getDefaultRadius = (t: number) => {
        // Typical values matching Rust backend defaults
        const rThroat = 0.020;    // 20mm throat radius
        const contractionRatio = 3.5;  // Ac/At
        const expansionRatio = 8.0;    // Ae/At

        const rChamber = rThroat * Math.sqrt(contractionRatio);  // ~37.4mm
        const rExit = rThroat * Math.sqrt(expansionRatio);        // ~56.6mm

        // Section boundaries matching Rust backend logic
        // Chamber cylindrical: 0 to chamberEnd
        // Convergent (cosine blend): chamberEnd to throatStart
        // Throat: throatStart to throatEnd
        // Divergent (80% parabolic bell): throatEnd to 1.0
        const chamberEnd = 0.55;
        const throatStart = 0.60;
        const throatEnd = 0.62;

        if (t < chamberEnd) {
            // Cylindrical chamber section
            return rChamber;
        } else if (t < throatStart) {
            // Convergent section with cosine-blend transition (like Rust backend)
            const s = (t - chamberEnd) / (throatStart - chamberEnd);
            const blend = (1.0 - Math.cos(s * Math.PI)) / 2.0;
            return rChamber - (rChamber - rThroat) * blend;
        } else if (t < throatEnd) {
            // Throat section (minimum radius)
            return rThroat;
        } else {
            // Divergent section (80% parabolic bell - same as Rust backend)
            const s = (t - throatEnd) / (1.0 - throatEnd);
            return rThroat + (rExit - rThroat) * Math.pow(2.0 * s - s * s, 0.85);
        }
    };

    const geometry = useMemo(() => {
        if (!profile || !profile.x || !profile.r) {
            // Default geometry if no profile
            const points: THREE.Vector2[] = [];
            for (let i = 0; i <= 50; i++) {
                const t = i / 50;
                const x = t * 0.35;  // 350mm total length
                const r = getDefaultRadius(t);
                points.push(new THREE.Vector2(r, x - 0.175));  // Center the mesh
            }
            return new THREE.LatheGeometry(points, 64);
        }

        // Create lathe geometry from profile
        const points = profile.x.map((x, i) =>
            new THREE.Vector2(profile.r[i], x - profile.x[profile.x.length - 1] / 2)
        );
        return new THREE.LatheGeometry(points, 64);
    }, [profile]);

    // Generate coolant channel positions
    const channelPositions = useMemo(() => {
        if (!showChannels) return [];

        const positions: Array<{ x: number, y: number, z: number }> = [];
        const lengthSteps = 25;

        for (let c = 0; c < nChannels; c++) {
            const angle = (c / nChannels) * Math.PI * 2;

            for (let i = 0; i <= lengthSteps; i++) {
                const t = i / lengthSteps;
                const xPos = t * 0.35 - 0.175;

                // Get radius from profile or default
                let nozzleRadius: number;
                if (profile && profile.x && profile.r) {
                    // Interpolate from profile
                    const idx = Math.floor(t * (profile.x.length - 1));
                    nozzleRadius = profile.r[Math.min(idx, profile.r.length - 1)];
                } else {
                    nozzleRadius = getDefaultRadius(t);
                }

                const outerRadius = nozzleRadius + 0.006; // 6mm outside the wall

                positions.push({
                    x: Math.cos(angle) * outerRadius,
                    y: xPos, // Y is the length axis in lathe geometry
                    z: Math.sin(angle) * outerRadius
                });
            }
        }
        return positions;
    }, [showChannels, nChannels, profile]);

    return (
        <group ref={groupRef}>
            {/* Outer shell */}
            <mesh ref={meshRef} geometry={geometry}>
                <meshStandardMaterial
                    color="#cc7733"
                    metalness={0.8}
                    roughness={0.2}
                    side={THREE.DoubleSide}
                />
            </mesh>

            {/* Inner surface (darker) */}
            <mesh geometry={geometry} scale={[0.95, 1, 0.95]}>
                <meshStandardMaterial
                    color="#442200"
                    metalness={0.3}
                    roughness={0.8}
                    side={THREE.BackSide}
                />
            </mesh>

            {/* Coolant Channels - Cyan tubes */}
            {showChannels && channelPositions.map((pos, i) => (
                <mesh key={i} position={[pos.x, pos.y, pos.z]}>
                    <sphereGeometry args={[0.003, 6, 6]} />
                    <meshStandardMaterial
                        color="#00d4ff"
                        emissive="#00d4ff"
                        emissiveIntensity={0.3}
                        metalness={0.8}
                        roughness={0.2}
                    />
                </mesh>
            ))}
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
    showChannels?: boolean;
    nChannels?: number;
}

export default function Motor3DViewer({
    profile = null,
    height = 400,
    showFlames = false,
    showChannels = false,
    nChannels = 48
}: Motor3DViewerProps) {
    return (
        <div style={{ height, width: "100%", background: "#0a0a10", borderRadius: 12, overflow: "hidden" }}>
            <Canvas camera={{ position: [0.3, 0.2, 0.3], fov: 45 }}>
                <ambientLight intensity={0.5} />
                <directionalLight position={[5, 5, 5]} intensity={1} />
                <pointLight position={[-3, 2, -2]} intensity={0.5} color="#00d4ff" />

                <MotorMesh
                    profile={profile}
                    showChannels={showChannels}
                    nChannels={nChannels}
                />

                {showFlames && <Flames />}

                <OrbitControls
                    enablePan={true}
                    enableZoom={true}
                    enableRotate={true}
                    autoRotate={false}
                    minDistance={0.2}
                    maxDistance={2}
                />

                <gridHelper args={[1, 10, "#27272a", "#1a1a25"]} rotation={[Math.PI / 2, 0, 0]} />
            </Canvas>
        </div>
    );
}
