"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useEffect, useMemo, useRef, useState } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";

import { useFrame, useThree } from "@react-three/fiber";
import * as THREE from "three";
import { Canvas } from "@react-three/fiber";
import { Bloom, EffectComposer, Vignette } from "@react-three/postprocessing";
import BlenderAsset from "../three/BlenderAsset";
import { FestivalNightLighting } from "../three/FestivalNight";
import {
  makeMudTexture,
  makeTurfPatchTexture,
  makeTurfTexture,
} from "../landing-page/gate3d/textures";
import { RoomEnvironment } from "three/examples/jsm/environments/RoomEnvironment.js";
import styles from "./help-desk.module.css";

const formSchema = z.object({
  name: z.string().min(2, "Tell us your name.").max(50),
  email: z.string().email("Enter a valid email address.").max(100),
  phone: z.string().min(10, "Enter at least 10 digits.").max(15),
  message: z.string().min(10, "Give us a little more detail.").max(500),
});

type FormValues = z.infer<typeof formSchema>;

const BLACK = "#080a09";
const PANEL = "#111412";
const METAL = "#69706c";
const WARM = "#ffd8a3";

function Environment() {
  const gl = useThree((state) => state.gl);
  const scene = useThree((state) => state.scene);

  useEffect(() => {
    const pmrem = new THREE.PMREMGenerator(gl);
    const env = pmrem.fromScene(new RoomEnvironment(), 0.05).texture;
    scene.environment = env;
    scene.environmentIntensity = 0.2;

    return () => {
      scene.environment = null;
      env.dispose();
      pmrem.dispose();
    };
  }, [gl, scene]);

  return null;
}

function Box({
  position,
  scale,
  color,
  roughness = 0.62,
  metalness = 0.04,
  emissive,
  emissiveIntensity = 0,
  castShadow = true,
  receiveShadow = true,
}: {
  position: [number, number, number];
  scale: [number, number, number];
  color: string;
  roughness?: number;
  metalness?: number;
  emissive?: string;
  emissiveIntensity?: number;
  castShadow?: boolean;
  receiveShadow?: boolean;
}) {
  return (
    <mesh position={position} castShadow={castShadow} receiveShadow={receiveShadow}>
      <boxGeometry args={scale} />
      <meshStandardMaterial
        color={color}
        roughness={roughness}
        metalness={metalness}
        emissive={emissive}
        emissiveIntensity={emissiveIntensity}
      />
    </mesh>
  );
}

function FestivalGround() {
  const turf = useMemo(() => {
    const texture = makeTurfTexture();
    texture.repeat.set(34 / 3, 30 / 3);
    return texture;
  }, []);

  const turfPatches = useMemo(
    () =>
      makeTurfPatchTexture({
        w: 1536,
        h: 1536,
        count: 240,
        minR: 7,
        maxR: 62,
        seed: 7714,
        feather: 120,
      }),
    [],
  );

  const mud = useMemo(() => {
    const texture = makeMudTexture();
    texture.repeat.set(4.8 / 3.2, 14 / 3.2);
    return texture;
  }, []);

  useEffect(
    () => () => {
      turf.dispose();
      turfPatches.dispose();
      mud.dispose();
    },
    [mud, turf, turfPatches],
  );

  return (
    <group>
      <mesh rotation-x={-Math.PI / 2} position={[0, -0.028, 2]} receiveShadow>
        <planeGeometry args={[36, 32]} />
        <meshStandardMaterial color="#090c09" roughness={0.99} />
      </mesh>

      <mesh rotation-x={-Math.PI / 2} position={[0, -0.016, 2]} receiveShadow>
        <planeGeometry args={[34, 30]} />
        <meshStandardMaterial map={turf} roughness={0.97} metalness={0} />
      </mesh>

      <mesh rotation-x={-Math.PI / 2} position={[0, -0.011, 2]}>
        <planeGeometry args={[30, 26]} />
        <meshStandardMaterial
          map={turfPatches}
          transparent
          depthWrite={false}
          roughness={0.97}
          metalness={0}
        />
      </mesh>

      <mesh rotation-x={-Math.PI / 2} rotation-z={-0.015} position={[0.12, -0.004, 7.45]} receiveShadow>
        <planeGeometry args={[4.8, 14]} />
        <meshStandardMaterial map={mud} roughness={0.98} metalness={0} />
      </mesh>
    </group>
  );
}

function Practical({ x }: { x: number }) {
  return (
    <group position={[x, 4.42, 1.25]}>
      <mesh rotation={[Math.PI / 2, 0, 0]} castShadow>
        <cylinderGeometry args={[0.085, 0.105, 0.095, 18]} />
        <meshStandardMaterial color="#252925" roughness={0.32} metalness={0.68} />
      </mesh>
      <mesh position={[0, -0.06, 0]}>
        <sphereGeometry args={[0.052, 16, 16]} />
        <meshStandardMaterial color="#fff3d7" emissive="#ffd28f" emissiveIntensity={4.2} />
      </mesh>
      <pointLight color={WARM} intensity={0.72} distance={3.3} decay={2} />
    </group>
  );
}

function HelpDeskStall() {
  return (
    <group position={[0, 0, -0.2]}>
      <Box position={[0, 2.75, -0.34]} scale={[7.2, 5.25, 0.18]} color={PANEL} roughness={0.9} />
      <Box position={[0, 3.0, -0.215]} scale={[6.55, 3.72, 0.045]} color="#0c0f0d" roughness={0.94} />

      <Box position={[-3.48, 2.72, 0.98]} scale={[0.19, 5.25, 2.72]} color="#0d100e" roughness={0.86} />
      <Box position={[3.48, 2.72, 0.98]} scale={[0.19, 5.25, 2.72]} color="#0d100e" roughness={0.86} />
      <Box position={[0, 5.28, 0.98]} scale={[7.14, 0.18, 2.72]} color="#0a0c0b" roughness={0.78} />

      {[-3.57, 3.57].map((x) => (
        <Box key={x} position={[x, 2.72, 1.02]} scale={[0.075, 5.42, 2.9]} color={METAL} roughness={0.3} metalness={0.76} />
      ))}
      <Box position={[0, 4.63, 1.76]} scale={[7.18, 1.02, 0.32]} color={BLACK} roughness={0.56} metalness={0.08} />
      <Box position={[0, 4.08, 1.61]} scale={[6.72, 0.055, 0.14]} color="#565d58" roughness={0.26} metalness={0.78} />

      <Box position={[0, 3.12, -0.085]} scale={[4.6, 2.55, 0.11]} color="#252a26" roughness={0.34} metalness={0.5} />
      <Box position={[0, 3.12, -0.015]} scale={[4.36, 2.31, 0.055]} color="#0a0d0b" roughness={0.72} metalness={0.03} />

      <Box position={[0, 1.02, 2.13]} scale={[6.15, 1.82, 1.18]} color="#0b0e0c" roughness={0.82} />
      <Box position={[0, 1.98, 2.12]} scale={[6.34, 0.13, 1.38]} color="#171b18" roughness={0.4} metalness={0.08} />
      <Box position={[0, 1.08, 2.74]} scale={[5.78, 1.28, 0.035]} color="#0a0c0b" roughness={0.9} />
      <Box position={[0, 0.39, 2.74]} scale={[6.02, 0.055, 0.05]} color="#444b46" roughness={0.32} metalness={0.74} />

      {[-2.45, -1.22, 0, 1.22, 2.45].map((x) => (
        <Practical key={x} x={x} />
      ))}
    </group>
  );
}

function CameraRig({ onArrive }: { onArrive: () => void }) {
  const { camera, pointer, size } = useThree();
  const target = useRef(new THREE.Vector3(0, 2.86, 0.28));
  const desired = useRef(new THREE.Vector3());
  const lookTarget = useRef(new THREE.Vector3());
  const elapsed = useRef(0);
  const arrived = useRef(false);

  useEffect(() => {
    const mobile = size.width < 760;
    camera.position.set(0, mobile ? 3.08 : 2.98, mobile ? 10.9 : 9.4);
    target.current.set(0, mobile ? 2.62 : 2.5, mobile ? 0.35 : 0.28);
    camera.lookAt(target.current);
    elapsed.current = 0;
    arrived.current = false;
  }, [camera, size.width]);

  useFrame((_, dt) => {
    elapsed.current += Math.min(dt, 0.05);
    const mobile = size.width < 760;
    const baseZ = mobile ? 10.25 : 8.3;
    const baseY = mobile ? 3.05 : 2.98;
    const progress = THREE.MathUtils.smoothstep(Math.min(elapsed.current / 1.45, 1), 0, 1);
    const introOffset = (1 - progress) * (mobile ? 0.55 : 1.0);
    const pointerFade = 1 - THREE.MathUtils.smoothstep(progress, 0.78, 1);
    const pointerX = mobile ? 0 : pointer.x * 0.09 * pointerFade;
    const pointerY = mobile ? 0 : pointer.y * 0.035 * pointerFade;

    desired.current.set(pointerX, baseY + pointerY, baseZ + introOffset);
    camera.position.lerp(desired.current, 1 - Math.exp(-6.2 * dt));

    lookTarget.current.set(pointerX * 0.2, (mobile ? 2.62 : 2.5) + pointerY * 0.16, mobile ? 0.35 : 0.28);
    target.current.lerp(lookTarget.current, 1 - Math.exp(-7 * dt));
    camera.lookAt(target.current);

    if (!arrived.current && elapsed.current >= 1.62) {
      camera.position.copy(desired.current);
      target.current.copy(lookTarget.current);
      camera.lookAt(target.current);
      arrived.current = true;
      onArrive();
    }
  });

  return null;
}

const HELP_DESK_UPLIGHTS = [
  { position: [-3.25, 0, 1.85] as const, target: [-2.2, 3.72, 1.7] as const },
  { position: [3.25, 0, 1.85] as const, target: [2.2, 3.72, 1.7] as const },
];

function HelpDeskUplights() {
  const targets = useMemo(
    () =>
      HELP_DESK_UPLIGHTS.map((fixture) => {
        const target = new THREE.Object3D();
        target.position.set(fixture.target[0], fixture.target[1], fixture.target[2]);
        return target;
      }),
    []
  );

  const headQuaternions = useMemo(
    () =>
      HELP_DESK_UPLIGHTS.map((fixture, index) => {
        const head = new THREE.Vector3(fixture.position[0], 0.34, fixture.position[2]);
        const direction = targets[index].position.clone().sub(head).normalize();
        return new THREE.Quaternion().setFromUnitVectors(new THREE.Vector3(0, 0, 1), direction);
      }),
    [targets]
  );

  return (
    <group>
      {HELP_DESK_UPLIGHTS.map((fixture, index) => (
        <group key={fixture.position[0]}>
          <primitive object={targets[index]} />

          <group position={fixture.position} scale={1.6}>
            <mesh position={[0, 0.05, 0]} castShadow>
              <boxGeometry args={[0.34, 0.1, 0.34]} />
              <meshStandardMaterial color="#25292d" roughness={0.7} metalness={0.5} />
            </mesh>
            <mesh position={[0, 0.2, 0]} castShadow>
              <cylinderGeometry args={[0.034, 0.034, 0.25, 8]} />
              <meshStandardMaterial color="#25292d" roughness={0.7} metalness={0.5} />
            </mesh>
            <group position={[0, 0.34, 0]} quaternion={headQuaternions[index]}>
              <mesh rotation-x={Math.PI / 2} castShadow>
                <cylinderGeometry args={[0.13, 0.16, 0.34, 12]} />
                <meshStandardMaterial color="#25292d" roughness={0.64} metalness={0.56} />
              </mesh>
              <mesh position={[0, 0, 0.18]}>
                <circleGeometry args={[0.11, 18]} />
                <meshStandardMaterial
                  color="#fff0cf"
                  emissive="#ffe6b4"
                  emissiveIntensity={3.1}
                  roughness={0.28}
                  toneMapped={false}
                />
              </mesh>
            </group>
          </group>

          <pointLight
            position={[fixture.position[0], 0.42, fixture.position[2]]}
            color="#ffdca8"
            intensity={1.8}
            distance={5}
            decay={2}
          />
          <spotLight
            target={targets[index]}
            position={[fixture.position[0], 0.42, fixture.position[2]]}
            color="#ffebc5"
            intensity={78}
            angle={0.34}
            penumbra={0.62}
            distance={18}
            decay={2}
            castShadow
            shadow-mapSize-width={1024}
            shadow-mapSize-height={1024}
            shadow-camera-near={0.35}
            shadow-camera-far={18}
            shadow-bias={-0.00035}
          />
        </group>
      ))}
    </group>
  );
}

function HelpDeskScene({ onArrive }: { onArrive: () => void }) {
  return (
    <Canvas
      shadows
      dpr={[1, 1.5]}
      camera={{ fov: 42, near: 0.1, far: 90, position: [0, 2.98, 9.4] }}
      gl={{ antialias: true, powerPreference: "high-performance" }}
      onCreated={({ gl }) => {
        gl.toneMapping = THREE.ACESFilmicToneMapping;
        gl.toneMappingExposure = 0.92;
        gl.shadowMap.type = THREE.PCFSoftShadowMap;
      }}
    >
      <color attach="background" args={["#050706"]} />
      <fog attach="fog" args={["#050706", 15, 36]} />
      <FestivalNightLighting />
      <FestivalGround />
      <BlenderAsset url="/models/breeze/help-desk.glb" />
      <HelpDeskUplights />
      <CameraRig onArrive={onArrive} />

      <EffectComposer multisampling={0}>
        <Bloom intensity={0.22} luminanceThreshold={1.05} luminanceSmoothing={0.48} mipmapBlur />
        <Vignette eskil={false} offset={0.2} darkness={0.45} />
      </EffectComposer>
    </Canvas>
  );
}

function ContactForm() {
  const [state, setState] = useState<"idle" | "sending" | "sent" | "error">("idle");
  const form = useForm<FormValues>({
    resolver: zodResolver(formSchema),
    defaultValues: { name: "", email: "", phone: "", message: "" },
  });

  const onSubmit = async (values: FormValues) => {
    setState("sending");
    try {
      const response = await fetch("/api/contact", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(values),
      });
      if (!response.ok) throw new Error("Request failed");
      form.reset();
      setState("sent");
    } catch {
      setState("error");
    }
  };

  if (state === "sent") {
    return (
      <div className={styles.successState}>
        <span className={styles.statusDot} />
        <p className={styles.kicker}>MESSAGE RECEIVED</p>
        <h2>We’ve got it.</h2>
        <p>The Breeze crew will get back to you as soon as possible.</p>
        <button type="button" onClick={() => setState("idle")}>
          Send another message
        </button>
      </div>
    );
  }

  return (
    <form className={styles.form} onSubmit={form.handleSubmit(onSubmit)}>
      <div className={styles.formHeader}>
        <div>
          <p className={styles.kicker}>BREEZE ’27 / CREW SUPPORT</p>
          <h2>Talk to the crew</h2>
        </div>
        <span className={styles.livePill}>
          <span /> ON SITE
        </span>
      </div>

      <div className={styles.twoCol}>
        <label>
          <span>Name</span>
          <input autoComplete="name" placeholder="Your name" {...form.register("name")} />
          {form.formState.errors.name && <small>{form.formState.errors.name.message}</small>}
        </label>
        <label>
          <span>Email</span>
          <input type="email" autoComplete="email" placeholder="you@email.com" {...form.register("email")} />
          {form.formState.errors.email && <small>{form.formState.errors.email.message}</small>}
        </label>
      </div>

      <label>
        <span>Phone</span>
        <input inputMode="tel" autoComplete="tel" placeholder="+91 …" {...form.register("phone")} />
        {form.formState.errors.phone && <small>{form.formState.errors.phone.message}</small>}
      </label>

      <label>
        <span>What do you need help with?</span>
        <textarea rows={3} placeholder="Tell us what’s going on…" {...form.register("message")} />
        {form.formState.errors.message && <small>{form.formState.errors.message.message}</small>}
      </label>

      {state === "error" && <p className={styles.errorBanner}>Couldn’t send that. Please try again.</p>}

      <div className={styles.formFooter}>
        <span>INFO · LOST &amp; FOUND · ACCESS</span>
        <button className={styles.submit} type="submit" disabled={state === "sending"}>
          <span>{state === "sending" ? "Sending…" : "Send message"}</span>
          <span aria-hidden="true">↗</span>
        </button>
      </div>
    </form>
  );
}

export default function HelpDeskExperience() {
  const [formReady, setFormReady] = useState(false);

  useEffect(() => {
    const revealTimer = window.setTimeout(() => setFormReady(true), 1750);
    return () => window.clearTimeout(revealTimer);
  }, []);

  return (
    <main className={styles.page}>
      <div className={styles.scene} aria-hidden="true">
        <HelpDeskScene onArrive={() => setFormReady(true)} />
      </div>

      <div className={styles.fasciaCopy} aria-hidden="true">
        <span>BREEZE ’27</span>
        <strong>HELP DESK</strong>
      </div>

      {formReady && (
        <section className={styles.formShell} aria-label="Contact Breeze help desk">
          <div className={styles.panelPatina} aria-hidden="true" />
          <ContactForm />
        </section>
      )}

      <p className={styles.sceneCaption}>
        <span className={styles.captionDot} />
        FESTIVAL CREW · OPEN DURING EVENT HOURS
      </p>
    </main>
  );
}
