from pathlib import Path

def edit(path,old,new):
 p=Path(path);s=p.read_text();assert old in s,(path,old[:80]);p.write_text(s.replace(old,new))
# Held key ownership: clear on entering a form, reject stale repeat, suspend touch/drag too.
p='components/immersive/input.ts'
edit(p,'const movementCodes', 'const editableSelector = "form, input, textarea, select, [contenteditable]:not([contenteditable=false])";\nconst movementCodes')
edit(p,'    const down = (e: KeyboardEvent) => {\n      if ((e.target as HTMLElement)?.closest("input, textarea, select, [contenteditable=true]")) return;', '''    runtime.suspended = document.hidden;
    const editable = (target: EventTarget | null) => target instanceof Element && !!target.closest(editableSelector);
    const focusIn = (e: FocusEvent) => { if (editable(e.target)) clear(); };
    const down = (e: KeyboardEvent) => {
      if (runtime.suspended || editable(document.activeElement) || e.composedPath().some(editable)) { clear(); return; }''')
edit(p,'e.preventDefault(); keys.current.add(e.code); update();','if (e.repeat && !keys.current.has(e.code)) return; e.preventDefault(); keys.current.add(e.code); update();')
edit(p,'      if (!(e.target as HTMLElement)?.closest("canvas")) return;','      if (runtime.suspended || !(e.target as HTMLElement)?.closest("canvas")) return;')
edit(p,'const s = runtime.getSnapshot(); if (s.phase !== "local"','const s = runtime.getSnapshot(); if (runtime.suspended || s.phase !== "local"')
edit(p,'    window.addEventListener("keydown", down, true);','    document.addEventListener("focusin", focusIn);\n    window.addEventListener("keydown", down, true);')
edit(p,'      window.removeEventListener("keydown", down, true);','      document.removeEventListener("focusin", focusIn);\n      window.removeEventListener("keydown", down, true);')
# Coordinator entry intent. Session is a hint, explicit URL/history wins.
p='components/immersive/navigation.ts'
s=Path(p).read_text();s += '''
/** Fresh entry and deliberate Home arrival share the existing coordinator. */
export function initialNavigation(path: string, search: string, history: unknown, entered = false) {
  const location = locationFromPath(path) ?? "hub";
  const intent = new URLSearchParams(search).get("arrival");
  const marked = !!history && typeof history === "object" && "breezeArrival" in history && history.breezeArrival === "hub";
  return { location, intro: location === "hub" && (intent === "entrance" || !(intent === "hub" || marked || entered)) };
}
export function immersiveHref(id: LocationId, entrance = false) {
  return id === "hub" ? `/?arrival=${entrance ? "entrance" : "hub"}` : locations[id].href;
}
export function enteredGullyverse(): boolean {
  try { return window.sessionStorage.getItem("breeze:entered") === "1"; } catch { return false; }
}
export function rememberGullyverseEntry() {
  try { window.sessionStorage.setItem("breeze:entered", "1"); } catch { /* Explicit URLs/history still work without storage. */ }
}
''';Path(p).write_text(s)
edit('components/Navbar.tsx','import { cn }','import { immersiveHref } from "@/components/immersive/navigation";\nimport { cn }')
edit('components/Navbar.tsx','          href="/"','          href={immersiveHref("hub")}')
# Independent active cinematic and safe locomotion clocks, with event timestamps.
p='components/immersive/runtime.ts'
edit(p,'  suspended = false;', '''  private paused = false;
  private resumed = false;
  activeFrameDelta = 0;
  private activatedAt: number | null = null;
  private departureOpacity = 0;
  get suspended() { return this.paused; }
  set suspended(value: boolean) { if (this.paused && !value) this.resumed = true; this.paused = value; }''')
edit(p,'private onArrival?: (id: LocationId, source: RequestSource) => void;','private onArrival?: (id: LocationId, source: RequestSource, entrance?: boolean) => void;')
edit(p,'constructor(initial: LocationId, onArrival?: (id: LocationId, source: RequestSource) => void)', 'constructor(initial: LocationId, onArrival?: (id: LocationId, source: RequestSource, entrance?: boolean) => void, private intro = true, private clock?: () => number)')
edit(p,'this.pose = initial === "hub" ? landingPose() : spawnPose(initial, true);','this.pose = initial === "hub" && intro ? landingPose() : spawnPose(initial, true);')
edit(p,'private publish(update: Partial<Snapshot>) { this.state', 'private publish(update: Partial<Snapshot>) {\n    if (this.clock && (update.phase !== undefined || update.movie !== undefined || update.mapStage !== undefined)) this.activatedAt = this.clock();\n    this.state')
edit(p,'    this.clearInput(); this.focusFrom = { ...this.pose }; this.focusTime = 0;','    const restoring = !this.state.movie && this.focusFrom !== null;\n    this.clearInput(); this.focusFrom = { ...this.pose }; this.focusTime = 0;')
edit(p,'    if (movie) this.from = { ...this.pose };','    if (movie && !restoring) this.from = { ...this.pose };')
edit(p,'    this.source = source; this.elapsed = 0; this.ready = false;','    this.source = source; this.elapsed = 0; this.ready = false;\n    this.departureOpacity = this.opacity;')
edit(p,'if (this.state.scene === "hub") { this.opacity = 0; this.publish({ phase: "landing" }); }','if (this.state.scene === "hub" && this.intro) { this.opacity = 0; this.publish({ phase: "landing" }); }')
edit(p,'''    if (this.suspended || ["error", "context-lost", "recovering"].includes(this.state.phase)) return;
    const dt = Math.min(delta, 0.05); // restoring a background tab cannot teleport the player
    const phase = this.state.phase;
    this.elapsed += dt;''', '''    this.activeFrameDelta = 0;
    if (this.suspended || !Number.isFinite(delta) || delta < 0) return;
    if (this.resumed) { this.resumed = false; this.activatedAt = null; return; }
    this.activeFrameDelta = delta;
    if (["error", "context-lost", "recovering"].includes(this.state.phase)) return;
    let cinematicDelta = delta;
    if (this.activatedAt !== null && this.clock) {
      cinematicDelta = Math.min(delta, Math.max(0, this.clock() - this.activatedAt));
      this.activatedAt = null;
    }
    const dt = Math.min(delta, 0.05); // locomotion never catches up across a long frame
    const phase = this.state.phase;
    this.elapsed += cinematicDelta;''')
edit(p,'Math.exp(-8*dt)','Math.exp(-8*cinematicDelta)')
edit(p,'this.publish({ phase: "local" }); }','this.publish({ phase: "local" }); this.onArrival?.("hub", "url"); }')
edit(p,'this.opacity = smooth(Math.max(0, (u - 0.35) / 0.65));','this.opacity = mix(this.departureOpacity, 1, smooth(Math.max(0, (u - 0.35) / 0.65)));')
edit(p,'this.onArrival?.(this.state.scene, this.source);','this.onArrival?.(this.state.scene, this.source, this.targetEntrance);')
edit(p,'direction * dt /','direction * cinematicDelta /')
edit(p,'this.focusTime += dt;','this.focusTime += cinematicDelta;')
# Arrival URL/history preserves Next metadata. Completion marks session and existing history entry.
p='components/immersive/ImmersiveShell.tsx'
edit(p,'import { locationFromPath, locations }','import { enteredGullyverse, initialNavigation, immersiveHref, rememberGullyverseEntry, locationFromPath, locations }')
edit(p,'import styles from','import { activeDeadline } from "./activeDeadline";\nimport styles from')
start=Path(p).read_text();a=start.index('  const [runtime] = useState(');b=start.index('  const state = useSyncExternalStore',a)
start=start[:a]+'''  const [runtime] = useState(() => {
    const entry = initialNavigation(pathname, window.location.search, window.history.state, enteredGullyverse());
    return new ImmersiveRuntime(entry.location, (id, source, entrance) => {
      if (!entrance) rememberGullyverseEntry();
      if (source !== "url" && (locationFromPath(window.location.pathname) !== id || entrance)) {
        const href = immersiveHref(id, entrance);
        const diagnostic = new URLSearchParams(window.location.search).has("diagnostics");
        window.history.pushState({ ...window.history.state, breezeArrival: entrance ? "entrance" : id }, "", href + (diagnostic ? (href.includes("?") ? "&" : "?") + "diagnostics" : ""));
      } else if (id === "hub" && !entrance) {
        window.history.replaceState({ ...window.history.state, breezeArrival: "hub" }, "", window.location.href);
      }
    }, entry.intro, () => performance.now() / 1000);
  });
'''+start[b:];Path(p).write_text(start)
edit(p,'    const timer = setTimeout(() => runtime.fail("Critical scene preparation exceeded 45 seconds."), 45000);\n    return () => clearTimeout(timer);','''    const deadline = activeDeadline(45000, () => runtime.fail("Critical scene preparation exceeded 45 seconds."));
    const suspend = () => deadline.pause();
    const resume = () => { if (!document.hidden) deadline.resume(); };
    const visibility = () => document.hidden ? suspend() : resume();
    if (!runtime.suspended && !document.hidden) deadline.resume();
    window.addEventListener("blur", suspend); window.addEventListener("focus", resume);
    document.addEventListener("visibilitychange", visibility); document.addEventListener("freeze", suspend); document.addEventListener("resume", resume);
    return () => {
      deadline.cancel(); window.removeEventListener("blur", suspend); window.removeEventListener("focus", resume);
      document.removeEventListener("visibilitychange", visibility); document.removeEventListener("freeze", suspend); document.removeEventListener("resume", resume);
    };''')
# First resumed/background delta must not count as warm rendering cost.
edit('components/immersive/rendering.tsx','if (!prepared.current || warm.current.done || gl.getContext().isContextLost() || runtime.suspended) return;','if (!prepared.current || warm.current.done || gl.getContext().isContextLost() || runtime.suspended || runtime.activeFrameDelta <= 0) return;')
edit('components/immersive/rendering.tsx','warm.current.seconds += dt;', 'warm.current.seconds += runtime.activeFrameDelta;')
# Irrelevant preload only, no not-found content redesign.
edit('components/notFound.tsx','priority','loading="lazy"')
