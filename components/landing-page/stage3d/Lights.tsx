"use client";
import React, { useMemo, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";

/**
 * Scene lighting + show lights:
 * - low ambient & two colored washes (real lights, no shadows for perf)
 * - 6 moving heads on the front roof truss with fake-volumetric shader cones
 * `motion` prop freezes sweeps for prefers-reduced-motion users.
 */

const BEAM_VERT = /* glsl */ `
  varying vec2 vUv;
  varying vec3 vNormal;
  varying vec3 vView;
  void main() {
    vUv = uv;
    vec4 wp = modelMatrix * vec4(position, 1.0);
    vNormal = normalize(mat3(modelMatrix) * normal);
    vView = cameraPosition - wp.xyz;
    gl_Position = projectionMatrix * viewMatrix * wp;
  }
`;

// Bright at the fixture (uv.y = 1, narrow end), fading toward the floor.
// Rim term blurs the cone's silhouette: grazing angles dissolve to nothing.
const BEAM_FRAG = /* glsl */ `
  varying vec2 vUv;
  varying vec3 vNormal;
  varying vec3 vView;
  uniform vec3 uColor;
  uniform float uOpacity;
  void main() {
    float fade = pow(vUv.y, 3.2);
    float rim = abs(dot(normalize(vNormal), normalize(vView)));
    float soft = smoothstep(0.1, 0.95, rim);
    gl_FragColor = vec4(uColor * (0.6 + 0.4 * fade), fade * soft * uOpacity);
  }
`;

function makeBeamMaterial(hex: string, opacity: number) {
  return new THREE.ShaderMaterial({
    vertexShader: BEAM_VERT,
    fragmentShader: BEAM_FRAG,
    uniforms: { uColor: { value: new THREE.Color(hex) }, uOpacity: { value: opacity } },
    transparent: true,
    blending: THREE.AdditiveBlending,
    depthWrite: false,
    side: THREE.DoubleSide,
  });
}

// near-white with a warm hint: all heads run the same yellowish-white
const HEAD_COLORS = ["#fffbe8", "#fffbe8", "#fffbe8", "#fffbe8", "#fffbe8", "#fffbe8"];

function MovingHead({
  x,
  color,
  phase,
  motion,
  on,
}: {
  x: number;
  color: string;
  phase: number;
  motion: boolean;
  on: boolean;
}): React.ReactElement {
  const rig = useRef<THREE.Group>(null!);
  const spot = useRef<THREE.SpotLight>(null!);
  const fade = useRef(1); // 1 = lit, 0 = blacked out for the aftermovie
  const beamMat = useMemo(() => makeBeamMaterial(color, 0.16), [color]);
  const lensMat = useMemo(() => {
    const m = new THREE.MeshBasicMaterial({ color });
    m.toneMapped = false;
    return m;
  }, [color]);
  const lensBase = useMemo(() => new THREE.Color(color), [color]);
  // real spotlight target riding inside the rig, 10 units down the beam axis —
  // the light pool on the deck follows the visible cone exactly
  const spotTarget = useMemo(() => {
    const o = new THREE.Object3D();
    o.position.set(0, -10, 0);
    return o;
  }, []);

  useFrame(({ clock }, dt) => {
    const t = motion ? clock.elapsedTime : 0;
    rig.current.rotation.z = Math.sin(t * 0.35 + phase) * 0.5;
    rig.current.rotation.x = -0.45 + Math.sin(t * 0.22 + phase * 1.7) * 0.18;
    // smooth blackout/restore when the aftermovie starts/stops
    const f = (fade.current += ((on ? 1 : 0) - fade.current) * Math.min(1, dt * 2.5));
    beamMat.uniforms.uOpacity.value = f * (0.13 + 0.05 * Math.sin(t * 1.3 + phase * 3.0));
    spot.current.intensity = 300 * f;
    lensMat.color.copy(lensBase).multiplyScalar(0.05 + 1.75 * f);
  });

  return (
    <group position={[x, 11.15, 6.5]}>
      {/* yoke + housing — chunkier fixture body; beam cone below is untouched */}
      <mesh>
        <boxGeometry args={[0.5, 0.32, 0.5]} />
        <meshStandardMaterial color="#15181d" roughness={0.5} metalness={0.5} />
      </mesh>
      <group ref={rig}>
        <spotLight
          ref={spot}
          position={[0, -0.55, 0]}
          target={spotTarget}
          angle={0.34}
          penumbra={0.9}
          intensity={300}
          decay={2}
          color={color}
        />
        <primitive object={spotTarget} />
        <mesh position-y={-0.3}>
          <cylinderGeometry args={[0.21, 0.29, 0.58, 12]} />
          <meshStandardMaterial color="#1a1e25" roughness={0.45} metalness={0.55} />
        </mesh>
        {/* lens glow — kept large-ish and moderately bright: tiny ultra-bright
            sources strobe in the bloom mip chain as the camera moves */}
        <mesh position-y={-0.52} material={lensMat}>
          <sphereGeometry args={[0.13, 10, 10]} />
        </mesh>
        {/* volumetric-look cone: apex at fixture, opens toward the floor */}
        <mesh position-y={-8.5} material={beamMat} renderOrder={10}>
          <cylinderGeometry args={[0.06, 2.1, 16, 20, 1, true]} />
        </mesh>
      </group>
    </group>
  );
}

export default function Lights({ motion, dimmed }: { motion: boolean; dimmed: boolean }): React.ReactElement {
  return (
    <group>
      {/* Diegetic lighting: the LED wall and the truss beams ARE the light.
          Everything else is lit only by falloff from these sources, so
          distance from screen/beams = darkness — real depth cueing.
          Each moving head carries its own spotlight, so the pools on the
          deck move with the visible cones. */}
      <ambientLight intensity={0.055} />

      {/* LED wall glow — hugging the screens, kept soft so the MOVING head
          spots (not this static glow) own the colored pools on the deck */}
      <pointLight position={[0, 6.5, -3.6]} color="#fffbe8" intensity={110} decay={2} distance={11} />
      <pointLight position={[-7.5, 5.2, -3.8]} color="#fffbe8" intensity={50} decay={2} distance={9} />
      <pointLight position={[7.5, 5.2, -3.8]} color="#fffbe8" intensity={50} decay={2} distance={9} />

      {HEAD_COLORS.map((c, i) => (
        <MovingHead key={i} x={-9 + i * 3.6} color={c} phase={i * 1.13} motion={motion} on={!dimmed} />
      ))}
    </group>
  );
}
