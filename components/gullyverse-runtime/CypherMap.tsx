"use client";

import { useEffect, useRef } from "react";
import { useFrame } from "@react-three/fiber";
import { Vector4 } from "three";
import { projectMapPoint } from "../immersive/mapProjection";
import type { ImmersiveRuntime, Snapshot } from "../immersive/runtime";
import { arrivalPose, mapStops, type CypherStart, type MapStop } from "./cypher-map";

const here = "here";
/** DOM nodes the canvas positions every frame, without a React update per frame. */
export type CypherMapDOM = {
  container: HTMLDivElement | null;
  nodes: Map<string, HTMLElement>;
  dots: Map<string, HTMLElement>;
  lines: Map<string, SVGLineElement>;
};
export const createCypherMapDOM = (): CypherMapDOM => ({ container: null, nodes: new Map(), dots: new Map(), lines: new Map() });

/** The stop whose arrival is closest to the visitor, used as the starting focus. */
export function nearestStop(pose: { x: number; z: number }): MapStop {
  let best = mapStops[0], distance = Infinity;
  for (const stop of mapStops) {
    const arrival = arrivalPose(stop.id);
    const d = Math.hypot(arrival.x - pose.x, arrival.z - pose.z);
    if (d < distance) { best = stop; distance = d; }
  }
  return best;
}

/** Projects the map markers through the same camera as the aerial view. */
export function CypherMapProjection({ runtime, elements }: { runtime: ImmersiveRuntime; elements: CypherMapDOM }) {
  const clip = useRef(new Vector4());
  useFrame(({ camera, size }) => {
    if (!runtime.getSnapshot().map || !elements.container) return;
    camera.updateMatrixWorld();
    elements.container.style.opacity = String(Math.max(0, Math.min(1, (runtime.mapProgress - 0.78) / 0.22)));
    const { x, y, z } = runtime.pose;
    const points = [...mapStops.map(stop => ({ id: stop.id as string, position: stop.marker })),
      { id: here, position: [x, y - 1.7, z] as const }];
    const placed: { x: number; y: number; w: number; h: number }[] = [];
    const overlaps = (px: number, py: number, w: number, h: number) =>
      placed.filter(p => Math.abs(px - p.x) < (w + p.w) / 2 + 4 && Math.abs(py - p.y) < (h + p.h) / 2 + 4).length;
    // Keep labels between the map header and the walking toolbar.
    const frame = elements.container.getBoundingClientRect();
    const header = elements.container.parentElement?.querySelector(".cypher-map-header")?.getBoundingClientRect();
    const toolbar = elements.container.closest(".native-journey")?.querySelector(".gully-controls")?.getBoundingClientRect();
    const top = header ? header.bottom - frame.top + 8 : 96;
    const bottom = (toolbar ? toolbar.top - frame.top : size.height - 110) - 8;
    const projected = points.map(point => {
      const projection = projectMapPoint(point.position, camera, size.width, size.height, clip.current);
      const node = elements.nodes.get(point.id), dot = elements.dots.get(point.id), line = elements.lines.get(point.id);
      for (const element of [node, dot, line]) if (element) element.style.visibility = projection ? "visible" : "hidden";
      // Every dot stays uncovered: labels are placed around them.
      if (projection) placed.push({ x: projection.x, y: projection.y, w: 16, h: 16 });
      return { point, projection, node, dot, line };
    });
    for (const { projection, node, dot, line } of projected) {
      if (!projection || !node || !dot || !line) continue;
      const w = node.offsetWidth, h = node.offsetHeight;
      const clampX = (value: number) => Math.max(w / 2 + 8, Math.min(size.width - w / 2 - 8, value));
      const clampY = (value: number) => Math.max(top + h / 2, Math.min(bottom - h / 2, value));
      const preferredY = projection.y - 14 - h / 2;
      let best = { x: clampX(projection.x), y: clampY(preferredY), score: Infinity };
      for (const dy of [0, -34, 34, -68, 68, -102, 102, 136]) for (const dx of [0, -60, 60, -120, 120, -180, 180]) {
        const nx = clampX(projection.x + dx), ny = clampY(preferredY + dy);
        const score = overlaps(nx, ny, w, h) * 10000 + Math.hypot(nx - projection.x, ny - preferredY);
        if (score < best.score) best = { x: nx, y: ny, score };
      }
      placed.push({ x: best.x, y: best.y, w, h });
      node.style.transform = `translate(${best.x}px, ${best.y}px) translate(-50%, -50%)`;
      dot.style.transform = `translate(${projection.x}px, ${projection.y}px)`;
      line.setAttribute("x1", String(projection.x)); line.setAttribute("y1", String(projection.y));
      line.setAttribute("x2", String(best.x)); line.setAttribute("y2", String(best.y));
    }
  });
  return null;
}

/** Aerial cypher map: every destination and place is one tap away from anywhere on the route. */
export function CypherMap({ runtime, state, elements, travel }: {
  runtime: ImmersiveRuntime;
  state: Snapshot;
  elements: CypherMapDOM;
  travel(stop: CypherStart): void;
}) {
  const ref = useRef<HTMLElement>(null);
  const open = state.mapStage === "open";
  useEffect(() => {
    if (!open) return;
    const current = nearestStop(runtime.pose).id;
    ref.current?.querySelector<HTMLButtonElement>(`[data-map-stop="${current}"]`)?.focus({ preventScroll: true });
  }, [open, runtime]);
  const setNode = (id: string) => (node: HTMLElement | null) => {
    if (node) elements.nodes.set(id, node); else elements.nodes.delete(id);
  };
  const setDot = (id: string) => (node: HTMLElement | null) => {
    if (node) elements.dots.set(id, node); else elements.dots.delete(id);
  };
  const ids = [...mapStops.map(stop => stop.id as string), here];
  return <section ref={ref} className="cypher-map" aria-label="Cypher map" data-stage={state.mapStage}>
    <header className="cypher-map-header">
      <p>Map</p>
      <h2>Gullyverse from above</h2>
    </header>
    <div ref={node => { elements.container = node; }} className="cypher-map-markers">
      <svg aria-hidden="true">{ids.map(id => <line key={id} ref={node => {
        if (node) elements.lines.set(id, node); else elements.lines.delete(id);
      }} />)}</svg>
      {mapStops.map(stop => <div key={stop.id}>
        <i ref={setDot(stop.id)} className="cypher-map-dot" data-kind={stop.kind} aria-hidden="true" />
        <button type="button" ref={setNode(stop.id)} className="cypher-map-stop" data-map-stop={stop.id}
          data-kind={stop.kind} disabled={!open} onClick={() => {
            if (runtime.travelFromMap(arrivalPose(stop.id))) travel(stop.id);
          }}>{stop.label}</button>
      </div>)}
      <div>
        <i ref={setDot(here)} className="cypher-map-dot" data-kind="here" aria-hidden="true" />
        <span ref={setNode(here)} className="cypher-map-here">You are here</span>
      </div>
    </div>
    <p className="cypher-map-hint" aria-live="polite">{open
      ? <>Choose a place · <kbd>M</kbd> <kbd>Esc</kbd> back to your view</>
      : state.mapStage === "descent" ? "Landing" : "Rising above the gully"}</p>
  </section>;
}
