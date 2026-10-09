// The Live Timeline's gallery wall: one side wall faced head-on, posters
// laid flat in a horizontal row with time flowing left → right. The row
// slides past a fixed NOW line on a continuous timeline coordinate (act
// index + in-act drift + gap interpolation, equal-width slots). Only the
// previous act, the current act and the next few are mounted; the rest of
// the wall stays dimmed graffiti.
"use client";
import React, { useEffect, useMemo, useRef, useState } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { TUNNEL } from "../palette";
import type { TimelineEvent } from "./types";
import {
  buildSlotTable,
  deriveStatus,
  selectNextIndex,
  timelineCoord,
  type SlotTable,
} from "./timelineMath";
import { makeHaloTexture, makePosterTexture, type PosterRibbon } from "./posterTexture";
import type { ScrubMode } from "./useScrub";

/**
 * The gallery geometry, shared with the camera rig so the two agree.
 * FOV 52 at ~5.1 m puts the live poster at ~2/3 screen height: clear of
 * the bottom card and the top bar on phones and desktop alike.
 */
export const GALLERY = {
  side: -1, // -1 faces the left wall head-on, +1 the right
  camX: 2.1,
  camY: 1.7,
  /** Row centre along the tunnel (near the mouth, clear of the menu). */
  zc: -30,
  aimY: 1.93,
  fov: 52,
  /** Metres per act slot along the wall (equal-width, not by duration). */
  slotW: 1.7,
  /** Poster row height (eye-level): centre of every poster. */
  posterY: 2.6,
  posterW: 1.05,
  posterH: 1.575,
  liveScale: 1.25,
} as const;

const WALL_X = GALLERY.side * (TUNNEL.halfW - 0.07);
const FACE_ROT_Y = GALLERY.side === -1 ? Math.PI / 2 : -Math.PI / 2;

/** Advances the mutable sim clock per frame. Scrub-hold wins over advance. */
export function SimDriver({
  nowRef,
  pausedRef,
  speedRef,
  scrubRef,
  coordRef,
  slotsRef,
}: {
  nowRef: React.MutableRefObject<number>;
  pausedRef: React.MutableRefObject<boolean>;
  speedRef: React.MutableRefObject<number>;
  scrubRef: React.MutableRefObject<number | null>;
  /** Timeline coordinate, refreshed every frame from the sim clock. */
  coordRef?: React.MutableRefObject<number>;
  slotsRef?: React.MutableRefObject<SlotTable>;
}): null {
  useFrame((state, dt) => {
    if (!reducedMotion()) {
      const scrub = scrubRef.current;
      if (scrub !== null) {
        nowRef.current = scrub;
      } else if (!pausedRef.current) {
        nowRef.current += Math.min(dt, 0.1) * 1000 * speedRef.current;
      }
    }
    if (coordRef && slotsRef)
      coordRef.current = timelineCoord(slotsRef.current, nowRef.current);
    void state;
  });
  return null;
}

let rmCache: boolean | null = null;
function reducedMotion(): boolean {
  if (rmCache !== null) return rmCache;
  rmCache =
    typeof window !== "undefined" &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  return rmCache;
}

function Poster({
  ev,
  slot,
  ribbon,
  prominent,
  focused,
  nowRef,
  coordRef,
  scrubRef,
  modeRef,
  onSelect,
  geo,
  haloGeo,
}: {
  ev: TimelineEvent;
  /** Global slot index (position in the full start-sorted schedule). */
  slot: number;
  ribbon: PosterRibbon;
  prominent: boolean;
  /** Centred under the focus (screen centre): scaled up, brightened. */
  focused: boolean;
  nowRef: React.MutableRefObject<number>;
  /** Follow-mode time coordinate (SimDriver, per frame). */
  coordRef: React.MutableRefObject<number>;
  /** Scrub-mode absolute coordinate (gestures/glide). */
  scrubRef: React.MutableRefObject<number>;
  modeRef: React.MutableRefObject<ScrubMode>;
  onSelect: (id: string) => void;
  geo: THREE.PlaneGeometry;
  haloGeo: THREE.PlaneGeometry;
}): React.ReactElement {
  const mesh = useRef<THREE.Mesh>(null);
  const mat = useRef<THREE.MeshStandardMaterial>(null);
  const halo = useRef<THREE.MeshBasicMaterial>(null);
  // Artist photo, loaded once per act — the procedural print stands in
  // until (or unless) it resolves. <img> failure is silent and the
  // fallback is already on the wall.
  const [photo, setPhoto] = useState<HTMLImageElement | null>(null);
  useEffect(() => {
    setPhoto(null);
    if (!ev.posterUrl) return;
    let alive = true;
    const img = new Image();
    img.onload = () => {
      if (alive) setPhoto(img);
    };
    img.src = ev.posterUrl;
    return () => {
      alive = false;
    };
  }, [ev.posterUrl]);
  const tex = useMemo(
    () => makePosterTexture(ev, deriveStatus(ev, Date.parse(ev.startTime))),
    [ev]
  );
  // Refresh the cached texture when status, ribbon or photo changes (live
  // glow / scratch-out / NOW band / photo paint-in).
  const texTick = useRef("");

  useFrame((state) => {
    const m = mesh.current;
    if (!m) return;
    const now = nowRef.current;
    const st = deriveStatus(ev, now);
    const key = `${st}|${ribbon ?? "-"}|${photo ? "img" : "-"}`;
    if (texTick.current !== key) {
      texTick.current = key;
      const fresh = makePosterTexture(ev, st, ribbon, photo ?? undefined);
      if (mat.current) {
        mat.current.map = fresh;
        mat.current.emissiveMap = fresh;
        mat.current.needsUpdate = true;
      }
    }
    // the row slides past the fixed NOW line in follow mode; scrub mode
    // owns the coordinate absolutely. Either way: future → right (-z).
    const display =
      modeRef.current === "follow" ? coordRef.current : scrubRef.current;
    m.position.z = GALLERY.zc - (slot - display) * GALLERY.slotW;
    // live rides 1.25×, the focused poster 1.12× (smooth, no allocation)
    const live = st === "live" || st === "delayed";
    const goal = live ? GALLERY.liveScale : focused ? 1.12 : 1;
    const s = m.scale.x + (goal - m.scale.x) * 0.12;
    m.scale.setScalar(s);
    if (mat.current) {
      // the FACE stays low-emissive so time/stage text never blows out;
      // all the glow lives on the frame outline behind it
      const target = live ? 0.35 : 0.12;
      mat.current.emissiveIntensity += (target - mat.current.emissiveIntensity) * 0.08;
      const dim = prominent || focused ? 1 : 0.35;
      mat.current.opacity = (st === "done" || st === "cancelled" ? 0.75 : 1) * dim;
    }
    if (halo.current) {
      const t = state.clock.elapsedTime;
      const pulse = live || focused ? 0.7 + Math.sin(t * 2.4) * 0.15 : 0;
      const target = prominent || focused ? pulse : 0;
      halo.current.opacity += (target - halo.current.opacity) * 0.1;
    }
  });

  const haloColor =
    ribbon === "NOW"
      ? "#ff5a3c"
      : ribbon === "NEXT"
        ? "#4a7dd6"
        : ribbon === "DELAYED"
          ? "#ffc24b"
          : "#ff5a3c";
  const haloTex = useMemo(() => makeHaloTexture(haloColor), [haloColor]);

  return (
    <mesh
      ref={mesh}
      geometry={geo}
      position={[WALL_X, GALLERY.posterY, GALLERY.zc]}
      rotation={[0, FACE_ROT_Y, 0]}
      // above the graffiti dim box (renderOrder does not inherit through
      // groups, so this lives on the mesh itself)
      renderOrder={2}
      onClick={(e) => {
        e.stopPropagation();
        onSelect(ev.id);
      }}
    >
      <meshStandardMaterial
        ref={mat}
        map={tex}
        emissiveMap={tex}
        emissive={new THREE.Color("#ffffff")}
        emissiveIntensity={0.12}
        transparent
        roughness={0.9}
        metalness={0}
      />
      {/* frame outline: the bloom source. Transparent centre, tone-mapped
          off so the line pops while the face keeps its text readable. */}
      <mesh geometry={haloGeo} position={[0, 0, -0.012]} renderOrder={1}>
        <meshBasicMaterial
          ref={halo}
          map={haloTex}
          transparent
          opacity={0}
          toneMapped={false}
          depthWrite={false}
        />
      </mesh>
    </mesh>
  );
}

/** The NOW line: a physical element ON the wall at the current-time
 *  position. Scrubbed away it moves off-centre with the row; the live
 *  poster keeps its glow and NOW ribbon wherever it stands. Sits a hair
 *  behind the poster plane, so posters cover it where they stand. */
function NowLine({
  coordRef,
  scrubRef,
  modeRef,
}: {
  coordRef: React.MutableRefObject<number>;
  scrubRef: React.MutableRefObject<number>;
  modeRef: React.MutableRefObject<ScrubMode>;
}): React.ReactElement {
  const mesh = useRef<THREE.Mesh>(null);
  const mat = useRef<THREE.MeshBasicMaterial>(null);
  useFrame((state) => {
    if (!mat.current) return;
    const t = state.clock.elapsedTime;
    mat.current.opacity = 0.65 + Math.sin(t * 2.4) * 0.2;
    // wall position of "now": centre minus the drift between time and view
    const follow = coordRef.current;
    const display =
      modeRef.current === "follow" ? follow : scrubRef.current;
    if (mesh.current)
      mesh.current.position.z = GALLERY.zc - (follow - display) * GALLERY.slotW;
  });
  return (
    <mesh
      ref={mesh}
      position={[WALL_X - 0.025, GALLERY.posterY, GALLERY.zc]}
      rotation={[0, FACE_ROT_Y, 0]}
      renderOrder={1}
    >
      <planeGeometry args={[0.07, 2.3]} />
      <meshBasicMaterial
        ref={mat}
        color="#ffc24b"
        transparent
        opacity={0.7}
        toneMapped={false}
        depthWrite={false}
      />
    </mesh>
  );
}

export default function LiveLayer({
  events,
  allEvents,
  nowMs,
  nowRef,
  pausedRef,
  speedRef,
  scrubRef,
  dimmed,
  onSelect,
  modeRef,
  scrubCoordRef,
  focusIdx,
}: {
  /** Windowed posters (previous + current + next few). */
  events: TimelineEvent[];
  /** Full start-sorted schedule, for global slot indexes. */
  allEvents: TimelineEvent[];
  /** 1 Hz snapshot — drives ribbons and prominence (positions use nowRef). */
  nowMs: number;
  nowRef: React.MutableRefObject<number>;
  pausedRef: React.MutableRefObject<boolean>;
  speedRef: React.MutableRefObject<number>;
  scrubRef: React.MutableRefObject<number | null>;
  /** Slightly knock back the graffiti so posters read. */
  dimmed: boolean;
  onSelect: (id: string) => void;
  /** Wall scrub state (GateHero): follow pins to time, scrub owns display. */
  modeRef: React.MutableRefObject<ScrubMode>;
  scrubCoordRef: React.MutableRefObject<number>;
  /** Centred slot (card focus): scaled up, brightened. */
  focusIdx: number;
}): React.ReactElement {
  const geo = useMemo(
    () => new THREE.PlaneGeometry(GALLERY.posterW, GALLERY.posterH),
    []
  );
  const haloGeo = useMemo(
    () => new THREE.PlaneGeometry(GALLERY.posterW + 0.18, GALLERY.posterH + 0.18),
    []
  );
  // global slot order + precomputed start/end table (rebuilt only when the
  // schedule changes — the per-frame coordinate then costs nothing).
  // The NEXT ribbon uses the same shared selector as the card and hook,
  // so posters never point at a cancelled act.
  const { slotOf, slots, nextId } = useMemo(() => {
    const sorted = [...allEvents].sort(
      (a, b) =>
        Date.parse(a.startTime) - Date.parse(b.startTime) ||
        a.sortOrder - b.sortOrder
    );
    const ni = selectNextIndex(sorted, nowMs, -1, true);
    return {
      slotOf: new Map(sorted.map((e, i) => [e.id, i])),
      slots: buildSlotTable(sorted),
      nextId: ni >= 0 ? sorted[ni].id : null,
    };
  }, [allEvents, nowMs]);
  const slotsRef = useRef(slots);
  slotsRef.current = slots;
  const coordRef = useRef(0);

  // NOW + the next few upcoming acts carry the wall; everything past that
  // sits dim. Recomputed when the 1 Hz snapshot lands, not per frame.
  const { ribbons, prominentIds } = useMemo(() => {
    const withSt = events.map((ev) => ({ ev, st: deriveStatus(ev, nowMs) }));
    const upcoming = withSt
      .filter((w) => w.st === "upcoming" || w.st === "delayed")
      .sort((a, b) => Date.parse(a.ev.startTime) - Date.parse(b.ev.startTime));
    const prominent = new Set<string>();
    for (const w of withSt)
      if (w.st === "live" || w.st === "delayed") prominent.add(w.ev.id);
    for (const w of upcoming.slice(0, 3)) prominent.add(w.ev.id);
    const ribbons = new Map<string, PosterRibbon>();
    for (const w of withSt) {
      if (w.st === "cancelled") ribbons.set(w.ev.id, "CANCELLED");
      else if (w.st === "live") ribbons.set(w.ev.id, "NOW");
      else if (w.st === "delayed") ribbons.set(w.ev.id, "DELAYED");
      else if (w.ev.id === nextId) ribbons.set(w.ev.id, "NEXT");
    }
    return { ribbons, prominentIds: prominent };
  }, [events, nextId, nowMs]);
  return (
    <group>
      <SimDriver
        nowRef={nowRef}
        pausedRef={pausedRef}
        speedRef={speedRef}
        scrubRef={scrubRef}
        coordRef={coordRef}
        slotsRef={slotsRef}
      />
      {/* stronger knock-back while live is on: the big black wall
          lettering must not compete with poster text. Drawn right after
          the walls, before the posters, so posters stay bright. */}
      {dimmed && (
        <mesh position={[0, 2.5, (TUNNEL.startZ + TUNNEL.endZ) / 2]} renderOrder={1}>
          <boxGeometry
            args={[TUNNEL.halfW * 2 - 0.1, TUNNEL.roofY - 0.1, TUNNEL.length - 0.5]}
          />
          <meshBasicMaterial
            color="#000000"
            transparent
            opacity={0.45}
            side={THREE.BackSide}
            depthWrite={false}
          />
        </mesh>
      )}
      {events.map((ev) => (
        <Poster
          key={ev.id}
          ev={ev}
          slot={slotOf.get(ev.id) ?? 0}
          ribbon={ribbons.get(ev.id) ?? null}
          prominent={prominentIds.has(ev.id)}
          focused={focusIdx === (slotOf.get(ev.id) ?? -1)}
          nowRef={nowRef}
          coordRef={coordRef}
          scrubRef={scrubCoordRef}
          modeRef={modeRef}
          onSelect={onSelect}
          geo={geo}
          haloGeo={haloGeo}
        />
      ))}
      <NowLine coordRef={coordRef} scrubRef={scrubCoordRef} modeRef={modeRef} />
    </group>
  );
}
