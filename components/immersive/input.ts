"use client";
import { useEffect, useRef } from "react";
import type { ImmersiveRuntime } from "./runtime";

const movementCodes = new Set(["KeyW", "KeyA", "KeyS", "KeyD", "ArrowUp", "ArrowDown", "ArrowLeft", "ArrowRight"]);
export function useImmersiveInput(runtime: ImmersiveRuntime) {
  const keys = useRef(new Set<string>());
  const virtual = useRef(new Map<number, { forward: number; strafe: number }>());
  const drag = useRef<{ id: number; x: number; y: number } | null>(null);
  useEffect(() => {
    const update = () => {
      let forward = Number(keys.current.has("KeyW") || keys.current.has("ArrowUp")) - Number(keys.current.has("KeyS") || keys.current.has("ArrowDown"));
      let strafe = Number(keys.current.has("KeyD") || keys.current.has("ArrowRight")) - Number(keys.current.has("KeyA") || keys.current.has("ArrowLeft"));
      virtual.current.forEach((v) => { forward += v.forward; strafe += v.strafe; });
      runtime.input.forward = Math.max(-1, Math.min(1, forward)); runtime.input.strafe = Math.max(-1, Math.min(1, strafe));
    };
    const clear = () => { keys.current.clear(); virtual.current.clear(); drag.current = null; runtime.clearInput(); };
    const down = (e: KeyboardEvent) => {
      if ((e.target as HTMLElement)?.closest("input, textarea, select, [contenteditable=true]")) return;
      const s = runtime.getSnapshot();
      if (e.code === "Escape" && runtime.handleEscape()) { e.preventDefault(); e.stopImmediatePropagation(); return; }
      if (s.inspection) return;
      if (s.phase === "landing" && ["Enter", "Space"].includes(e.code) && !(e.target as HTMLElement)?.closest("button, a")) { e.preventDefault(); runtime.enter(); return; }
      if (e.code === "KeyM" && s.phase === "local" && !s.movie && !s.destinationMenu && !e.repeat) { e.preventDefault(); runtime.setMap(!s.map || s.mapStage === "descent"); return; }
      if (movementCodes.has(e.code) && s.phase === "local" && !s.map && !s.movie && !s.destinationMenu) { e.preventDefault(); keys.current.add(e.code); update(); }
    };
    const up = (e: KeyboardEvent) => { keys.current.delete(e.code); update(); };
    const visibility = () => { runtime.suspended = document.hidden; clear(); };
    const blur = () => { runtime.suspended = true; clear(); };
    const focus = () => { runtime.suspended = document.hidden; clear(); };
    const media = window.matchMedia("(prefers-reduced-motion: reduce)");
    const reduced = () => { runtime.reduced = media.matches; };
    reduced(); media.addEventListener("change", reduced);
    let ownership = `${runtime.getSnapshot().phase}:${runtime.getSnapshot().map}:${runtime.getSnapshot().movie}:${runtime.getSnapshot().inspection}:${runtime.getSnapshot().destinationMenu}`;
    const unsubscribe = runtime.subscribe(() => {
      const state = runtime.getSnapshot();
      const next = `${state.phase}:${state.map}:${state.movie}:${state.inspection}:${state.destinationMenu}`;
      if (ownership !== next) clear();
      ownership = next;
    });
    // Pointer drags operate on the rendering surface only; no pointer-lock requirement.
    const pointerDown = (e: PointerEvent) => {
      if (!(e.target as HTMLElement)?.closest("canvas")) return;
      const s = runtime.getSnapshot();
      if (s.phase === "landing") { runtime.enter(); return; }
      if (s.phase !== "local" || s.map || s.movie || s.inspection || s.destinationMenu) return;
      drag.current = { id: e.pointerId, x: e.clientX, y: e.clientY };
      (e.target as HTMLElement).setPointerCapture(e.pointerId);
    };
    const pointerMove = (e: PointerEvent) => {
      const d = drag.current; if (!d || d.id !== e.pointerId) return;
      runtime.input.lookX += (e.clientX - d.x) * 0.003;
      runtime.input.lookY += (e.clientY - d.y) * 0.003;
      d.x = e.clientX; d.y = e.clientY;
    };
    const pointerUp = (e: PointerEvent) => { if (drag.current?.id === e.pointerId) drag.current = null; virtual.current.delete(e.pointerId); update(); };
    // Touch pad events are converted to the same axes as the keyboard.
    const padDown = (e: PointerEvent) => {
      const pad = (e.target as HTMLElement)?.closest<HTMLElement>("[data-move]"); if (!pad) return;
      const s = runtime.getSnapshot(); if (s.phase !== "local" || s.map || s.movie || s.inspection || s.destinationMenu) return;
      e.preventDefault(); pad.setPointerCapture(e.pointerId);
      const direction = pad.dataset.move;
      virtual.current.set(e.pointerId, { forward: direction === "forward" ? 1 : direction === "back" ? -1 : 0, strafe: direction === "right" ? 1 : direction === "left" ? -1 : 0 }); update();
    };
    window.addEventListener("keydown", down, true); window.addEventListener("keyup", up);
    window.addEventListener("blur", blur); window.addEventListener("focus", focus); document.addEventListener("visibilitychange", visibility);
    document.addEventListener("freeze", blur); document.addEventListener("resume", focus);
    window.addEventListener("pointerdown", pointerDown); window.addEventListener("pointerdown", padDown);
    window.addEventListener("pointermove", pointerMove); window.addEventListener("pointerup", pointerUp); window.addEventListener("pointercancel", pointerUp);
    window.addEventListener("lostpointercapture", pointerUp);
    return () => {
      clear(); unsubscribe(); media.removeEventListener("change", reduced);
      window.removeEventListener("keydown", down, true); window.removeEventListener("keyup", up);
      window.removeEventListener("blur", blur); window.removeEventListener("focus", focus); document.removeEventListener("visibilitychange", visibility);
      document.removeEventListener("freeze", blur); document.removeEventListener("resume", focus);
      window.removeEventListener("pointerdown", pointerDown); window.removeEventListener("pointerdown", padDown);
      window.removeEventListener("pointermove", pointerMove); window.removeEventListener("pointerup", pointerUp); window.removeEventListener("pointercancel", pointerUp); window.removeEventListener("lostpointercapture", pointerUp);
    };
  }, [runtime]);
}
