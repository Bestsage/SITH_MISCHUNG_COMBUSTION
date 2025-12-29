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
    wallColor?: string;
    outerShellColor?: string;
    wallThickness?: number; // in mm
    outerShellThickness?: number; // in mm
}

function MotorMesh({
    profile,
    showChannels = false,
    nChannels = 48,
    rotate = true,
    wallColor = "#cc7733",
    outerShellColor = "#71717a",
    wallThickness = 2,
    outerShellThickness = 0
}: MotorMeshProps) {
    const meshRef = useRef<THREE.Mesh>(null);
    const groupRef = useRef<THREE.Group>(null);

    useFrame((state) => {
        if (groupRef.current && rotate) {
            groupRef.current.rotation.y = state.clock.elapsedTime * 0.2;
        }
    });

    // ... (getDefaultRadius remains same)
    const getDefaultRadius = (t: number) => {
        const rThroat = 0.020;
        const contractionRatio = 3.5;
        const expansionRatio = 8.0;
        const rChamber = rThroat * Math.sqrt(contractionRatio);
        const rExit = rThroat * Math.sqrt(expansionRatio);
        const chamberEnd = 0.55;
        const throatStart = 0.60;
        const throatEnd = 0.62;

        if (t < chamberEnd) return rChamber;
        else if (t < throatStart) {
            const s = (t - chamberEnd) / (throatStart - chamberEnd);
            const blend = (1.0 - Math.cos(s * Math.PI)) / 2.0;
            return rChamber - (rChamber - rThroat) * blend;
        } else if (t < throatEnd) return rThroat;
        else {
            const s = (t - throatEnd) / (1.0 - throatEnd);
            return rThroat + (rExit - rThroat) * Math.pow(2.0 * s - s * s, 0.85);
        }
    };

    const geometry = useMemo(() => {
        if (!profile || !profile.x || !profile.r) {
            const points: THREE.Vector2[] = [];
            for (let i = 0; i <= 50; i++) {
                const t = i / 50;
                const x = t * 0.35;
                const r = getDefaultRadius(t);
                points.push(new THREE.Vector2(r, x - 0.175));
            }
            return new THREE.LatheGeometry(points, 64);
        }
        const points = profile.x.map((x, i) =>
            new THREE.Vector2(profile.r[i], x - profile.x[profile.x.length - 1] / 2)
        );
        return new THREE.LatheGeometry(points, 64);
    }, [profile]);

    // Outer Shell Geometry (Jacket)
    const outerGeometry = useMemo(() => {
        const t_total = (wallThickness + (showChannels ? 6 : 0) + outerShellThickness) / 1000;
        if (!profile || !profile.x || !profile.r) {
            const points: THREE.Vector2[] = [];
            for (let i = 0; i <= 50; i++) {
                const t = i / 50;
                const x = t * 0.35;
                const r = getDefaultRadius(t) + t_total;
                points.push(new THREE.Vector2(r, x - 0.175));
            }
            return new THREE.LatheGeometry(points, 64);
        }
        const points = profile.x.map((x, i) =>
            new THREE.Vector2(profile.r[i] + t_total, x - profile.x[profile.x.length - 1] / 2)
        );
        return new THREE.LatheGeometry(points, 64);
    }, [profile, wallThickness, outerShellThickness, showChannels]);

    // ... (channelPositions remains mostly same, but uses wallThickness)
    const channelPositions = useMemo(() => {
        if (!showChannels) return [];
        const positions: Array<{ x: number, y: number, z: number }> = [];
        const lengthSteps = 25;
        for (let c = 0; c < nChannels; c++) {
            const angle = (c / nChannels) * Math.PI * 2;
            for (let i = 0; i <= lengthSteps; i++) {
                const t = i / lengthSteps;
                const xPos = t * 0.35 - 0.175;
                let nozzleRadius: number;
                if (profile && profile.x && profile.r) {
                    const idx = Math.floor(t * (profile.x.length - 1));
                    nozzleRadius = profile.r[Math.min(idx, profile.r.length - 1)];
                } else {
                    nozzleRadius = getDefaultRadius(t);
                }
                const outerRadius = nozzleRadius + (wallThickness / 1000) + 0.003;
                positions.push({
                    x: Math.cos(angle) * outerRadius,
                    y: xPos,
                    z: Math.sin(angle) * outerRadius
                });
            }
        }
        return positions;
    }, [showChannels, nChannels, profile, wallThickness]);

    return (
        <group ref={groupRef}>
            {/* Inner Liner */}
            <mesh ref={meshRef} geometry={geometry}>
                <meshStandardMaterial
                    color={wallColor}
                    metalness={0.8}
                    roughness={0.2}
                    side={THREE.DoubleSide}
                />
            </mesh>

            {/* If we have an outer shell, render it with some transparency to see channels */}
            {outerShellThickness > 0 && (
                <mesh geometry={outerGeometry}>
                    <meshStandardMaterial
                        color={outerShellColor}
                        metalness={0.9}
                        roughness={0.1}
                        transparent
                        opacity={0.4}
                        side={THREE.DoubleSide}
                    />
                </mesh>
            )}

            {/* Coolant Channels */}
            {showChannels && channelPositions.map((pos, i) => (
                <mesh key={i} position={[pos.x, pos.y, pos.z]}>
                    <sphereGeometry args={[0.002, 6, 6]} />
                    <meshStandardMaterial
                        color="#00d4ff"
                        emissive="#00d4ff"
                        emissiveIntensity={0.5}
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
