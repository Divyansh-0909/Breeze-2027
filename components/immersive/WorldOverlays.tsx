"use client";
import { useEffect, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import * as THREE from "three";
import { destinationOptions, type TravelId } from "./navigation";
import type { ImmersiveRuntime, Snapshot } from "./runtime";
import { world } from "./world";
import styles from "./immersive.module.css";

type MapPoint = { id: string; label: string; position: readonly number[]; destination?: TravelId };
export function mapPoints(): MapPoint[] {
  return [
    ...destinationOptions.map(d => ({ id: d.id, label: d.id === "hub" ? "Gullyverse hub" : d.label, position: d.worldPosition, destination: d.id })),
    { id: "left-stalls", label: "Left stalls", position: world.stalls[1].position },
    { id: "right-stalls", label: "Right stalls", position: world.stalls[4].position },
    { id: "scaffold", label: "Scaffold", position: world.scaffold.position },
    { id: "tunnel-exit", label: "Tunnel exit", position: [0, 0, world.tunnel.endZ] },
  ];
}
export type MapDOM = {
  container: HTMLDivElement | null;
  nodes: Map<string, HTMLElement>;
  dots: Map<string, HTMLElement>;
  lines: Map<string, SVGLineElement>;
};

/** Project DOM labels through the same R3F camera, without a React update per frame. */
export function MapMarkerProjection({ runtime, elements }: { runtime: ImmersiveRuntime; elements: MapDOM }) {
  const vector = useRef(new THREE.Vector3());
  const previousFrame = useRef("");
  const points = mapPoints();
  useFrame(({ camera, size }) => {
    if (!runtime.getSnapshot().map || !elements.container) { previousFrame.current = ""; return; }
    const signature = `${size.width}:${size.height}:${runtime.mapProgress}:${camera.position.x}:${camera.position.y}:${camera.position.z}:${elements.nodes.size}`;
    if (signature === previousFrame.current) return;
    previousFrame.current = signature;
    camera.updateMatrixWorld();
    elements.container.style.opacity = String(Math.max(0, Math.min(1, (runtime.mapProgress - 0.78) / 0.22)));
    const placed: { x: number; y: number; w: number; h: number }[] = [];
    const overlaps = (x: number, y: number, w: number, h: number) => placed.filter(p => Math.abs(x - p.x) < (w + p.w) / 2 + 5 && Math.abs(y - p.y) < (h + p.h) / 2 + 5).length;
    const projected = points.map(point => {
      vector.current.set(point.position[0], point.position[1] ?? 0, point.position[2]).project(camera);
      return { point, x: (vector.current.x + 1) * size.width / 2, y: (1 - vector.current.y) * size.height / 2 };
    }).sort((a, b) => a.y - b.y);
    for (const { point, x, y } of projected) {
      const node = elements.nodes.get(point.id), dot = elements.dots.get(point.id), line = elements.lines.get(point.id);
      if (!node || !dot || !line) continue;
      const w = node.offsetWidth, h = node.offsetHeight;
      let best = { x: Math.max(w / 2 + 10, Math.min(size.width - w / 2 - 10, x)), y: Math.max(100, Math.min(size.height - 80, y - 24)), score: Infinity };
      for (const dy of [0, -38, 38, -76, 76, -114, 114, -152, 152]) for (const dx of [0, -70, 70, -140, 140]) {
        const nx = Math.max(w / 2 + 10, Math.min(size.width - w / 2 - 10, x + dx));
        const ny = Math.max(100, Math.min(size.height - 80, y - 24 + dy));
        const score = overlaps(nx, ny, w, h) * 10000 + Math.hypot(nx - x, ny - (y - 24));
        if (score < best.score) best = { x: nx, y: ny, score };
      }
      placed.push({ x: best.x, y: best.y, w, h });
      node.style.transform = `translate(${best.x}px, ${best.y}px) translate(-50%, -50%)`;
      dot.style.transform = `translate(${x}px, ${y}px)`;
      line.setAttribute("x1", String(x)); line.setAttribute("y1", String(y));
      line.setAttribute("x2", String(best.x)); line.setAttribute("y2", String(best.y));
    }
  });
  return null;
}

function useOverlayFocus(ref: React.RefObject<HTMLElement | null>) {
  useEffect(() => {
    const previous = document.activeElement as HTMLElement | null;
    const node = ref.current;
    node?.querySelector<HTMLElement>("button:not(:disabled)")?.focus({ preventScroll: true });
    const trap = (event: KeyboardEvent) => {
      if (event.key !== "Tab" || !node) return;
      const controls = [...node.querySelectorAll<HTMLButtonElement>("button:not(:disabled)")];
      const first = controls[0], last = controls[controls.length - 1];
      if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last?.focus(); }
      else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first?.focus(); }
    };
    node?.addEventListener("keydown", trap);
    return () => { node?.removeEventListener("keydown", trap); previous?.focus({ preventScroll: true }); };
  }, [ref]);
}

function AerialMap({ runtime, state, elements }: { runtime: ImmersiveRuntime; state: Snapshot; elements: MapDOM }) {
  const ref = useRef<HTMLElement>(null);
  useOverlayFocus(ref);
  const points = mapPoints();
  return <section ref={ref} className={styles.aerialMap} aria-label="Festival aerial map" data-stage={state.mapStage}>
    <div className={styles.aerialHeader}><div><p>BREEZE 2027 / GULLYVERSE</p><h2>Gullyverse from above</h2></div><button onClick={() => runtime.setMap(false)} aria-label="Close map">Close <kbd>M / ESC</kbd></button></div>
    <div ref={node => { elements.container = node; }} className={styles.mapMarkers}>
      <svg className={styles.markerLines} aria-hidden="true">{points.map(p => <line key={p.id} ref={node => { if (node) elements.lines.set(p.id, node); else elements.lines.delete(p.id); }} />)}</svg>
      {points.map(point => {
        const destination = destinationOptions.find(d => d.id === point.destination);
        return <div key={point.id}>
          <i ref={node => { if (node) elements.dots.set(point.id, node); else elements.dots.delete(point.id); }} className={styles.mapDot} data-map-point={point.id} data-world-position={point.position.join(",")} aria-hidden="true" />
          {destination ? <button ref={node => { if (node) elements.nodes.set(point.id, node); else elements.nodes.delete(point.id); }} className={styles.mapMarker} aria-label={destination.id === "aftermovie" ? "Aftermovie" : point.label} data-destination={destination.id} disabled={!destination.available || state.mapStage !== "open"} onClick={() => destination.id === state.scene ? runtime.setMap(false) : runtime.requestDestination(destination.id, "map")}>
            {point.label}{!destination.available && <small>Coming soon</small>}
          </button> : <span ref={node => { if (node) elements.nodes.set(point.id, node); else elements.nodes.delete(point.id); }} className={styles.mapLandmark}>{point.label}</span>}
        </div>;
      })}
    </div>
    <p className={styles.aerialHint}>{state.mapStage === "open" ? "Choose a destination · M / ESC returns to your view" : state.mapStage === "descent" ? "Returning to your view" : "Rising above the quarry"}</p>
  </section>;
}

function DestinationMenu({ runtime }: { runtime: ImmersiveRuntime }) {
  const ref = useRef<HTMLDivElement>(null);
  useOverlayFocus(ref);
  return <div ref={ref} role="dialog" aria-modal="true" aria-labelledby="destination-menu-title" className={styles.boundaryMenu}>
    <h2 id="destination-menu-title">Where to next?</h2>
    <div className={styles.boundaryOptions}>{destinationOptions.filter(d => d.id !== "aftermovie").map(destination => <button key={destination.id} disabled={!destination.available} onClick={() => runtime.requestDestination(destination.id, "map")}>
      <span>{destination.id === "hub" ? "Return to Hub" : destination.label}</span>{!destination.available && <small>Coming soon</small>}
    </button>)}</div>
    <button className={styles.stayHere} onClick={() => runtime.dismissDestinationMenu()}>Stay Here</button><p>ESC — Stay here</p>
  </div>;
}

export default function WorldOverlays({ runtime, state, elements }: { runtime: ImmersiveRuntime; state: Snapshot; elements: MapDOM }) {
  return <>
    {state.map && <AerialMap runtime={runtime} state={state} elements={elements} />}
    {state.destinationMenu && <DestinationMenu runtime={runtime} />}
    {state.unavailableDestination && <div className={styles.destinationNotice} role="status"><span>{destinationOptions.find(d => d.id === state.unavailableDestination)?.label} · Coming soon</span><button onClick={() => runtime.dismissUnavailableDestination()} aria-label="Dismiss coming soon notice">×</button></div>}
  </>;
}
