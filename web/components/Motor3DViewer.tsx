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

    useFrame((state) => {
        if (meshRef.current && rotate) {
            meshRef.current.rotation.y = state.clock.elapsedTime * 0.2;
        }
    });

    const geometry = useMemo(() => {
        if (!profile || !profile.x || !profile.r) {
            // Default geometry if no profile
            const points: THREE.Vector2[] = [];
            for (let i = 0; i <= 50; i++) {
                const t = i / 50;
                const x = t * 0.35;  // 350mm total length
                let r = 0.05;  // Default radius

                if (t < 0.4) {
                    // Chamber
                    r = 0.05;
                } else if (t < 0.5) {
                    // Convergent
                    const s = (t - 0.4) / 0.1;
                    r = 0.05 - (0.05 - 0.025) * s * s;
                } else if (t < 0.55) {
                    // Throat
                    r = 0.025;
                } else {
                    // Divergent
                    const s = (t - 0.55) / 0.45;
                    r = 0.025 + (0.08 - 0.025) * Math.sqrt(s);
                }
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

    return (
        <group>
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
